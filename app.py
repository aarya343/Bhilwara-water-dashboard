"""Bhilwara Water Stress & ZLD Accountability Dashboard (IYEC prototype)."""
from pathlib import Path

import folium
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from streamlit_folium import st_folium

st.set_page_config(page_title="Bhilwara Water Stress Dashboard", page_icon="💧", layout="wide")
try:
    BASE = Path(__file__).parent
except NameError:  # running in a notebook / pasted code
    BASE = Path.cwd()
DATA = BASE / "data" if (BASE / "data").is_dir() else BASE  # works with or without a data/ folder

# ---- Fill these in before submission -------------------------------------
SOURCES = {
    "Groundwater levels": "CGWB / India-WRIS well records, Bhilwara district, 2015-2023 (pre- and post-monsoon)",
    "Rainfall": "District monsoon rainfall table (add exact source, e.g. IMD)",
    "Water quality": "CGWB groundwater quality records, Shahpura block, 2015-2023",
    "Industry list": "Regulator list of 35 textile units (RSPCB; add date/link). 34 plotted.",
    "Benchmarks": "CPCB/BEE water-use benchmarks and cluster averages (add exact source)",
}
# --------------------------------------------------------------------------

BIS = {"TDS": 2000, "Fluoride": 1.5, "Nitrate": 45}  # BIS IS 10500 permissible limits (mg/L)


@st.cache_data
def load():
    gw = pd.read_csv(DATA / "gw_tidy.csv")
    trend = pd.read_csv(DATA / "trend_results.csv")
    rain = pd.read_csv(DATA / "rainfall.csv")
    ind = pd.read_csv(DATA / "industries.csv")
    wq = pd.read_csv(DATA / "water_quality.csv")
    bench = pd.read_csv(DATA / "benchmarks.csv")
    return gw, trend, rain, ind, wq, bench


gw, trend, rain, ind, wq, bench = load()
post = gw[gw.season == "post"].dropna(subset=["Depth"])
counts = post.groupby("Site").Year.nunique()
long_sites = counts[counts >= 8].index  # wells with a (near-)complete 2015-2023 record
post_long = post[post.Site.isin(long_sites)]
wells = (
    post_long.groupby(["Site", "Lat", "Lon", "Aquifer"])
    .Depth.agg(median_depth="median", max_depth="max")
    .reset_index()
    .merge(trend, on="Site", how="left")
)


def depth_class(d):
    return "Deep (>8 m)" if d > 8 else ("Moderate (4-8 m)" if d >= 4 else "Shallow (<4 m)")


wells["Depth class"] = wells.median_depth.apply(depth_class)
COLORS = {"Deep (>8 m)": "#c0392b", "Moderate (4-8 m)": "#e6a23c", "Shallow (<4 m)": "#2e8b57"}

page = st.sidebar.radio(
    "Explore",
    ["1. Key findings", "2. Stress map", "3. Water quality", "4. Industry & water use", "5. Water Credit proposal"],
)
with st.sidebar.expander("Data sources"):
    for k, v in SOURCES.items():
        st.markdown(f"**{k}:** {v}")
st.sidebar.caption("Pilot: Bhilwara, Rajasthan. Nine years of public well data, so findings are indicative.")

# ============================ PAGE 1 =======================================
if page.startswith("1"):
    st.title("💧 Bhilwara: a groundwater bank with no savings")
    st.markdown(
        "Shallow groundwater in Bhilwara **refills with each monsoon, but one weak monsoon undoes it**, "
        "and several villages stay deep even after good rain. Industrial and farm draw has little room for error."
    )
    yr = post_long.groupby("Year").Depth.mean().rename("Mean post-monsoon depth (m)").reset_index().merge(rain, on="Year")
    rho = yr["Mean post-monsoon depth (m)"].rank().corr(yr.Actual_Monsoon_mm.rank())  # Spearman = Pearson on ranks (no scipy needed)
    sig_deep = int(((trend.p < 0.1) & (trend.slope_m_yr > 0)).sum())
    sig_shal = int(((trend.p < 0.1) & (trend.slope_m_yr < 0)).sum())
    deep_n = int((wells["Depth class"] == "Deep (>8 m)").sum())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Wells analysed", len(wells))
    c2.metric("Rain vs depth (Spearman)", f"{rho:.2f}")
    c3.metric("Wells with significant decline", sig_deep, help="Theil-Sen slope, Mann-Kendall p<0.1, post-monsoon depth")
    c4.metric("Wells staying deep (>8 m median)", deep_n)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=yr.Year, y=yr.Actual_Monsoon_mm, name="Monsoon rainfall (mm)", marker_color="#9ecae1")
    fig.add_scatter(x=yr.Year, y=yr["Mean post-monsoon depth (m)"], name="Mean depth to water (m)",
                    mode="lines+markers", line=dict(color="#08306b", width=3), secondary_y=True)
    fig.update_yaxes(title_text="Rainfall (mm)", secondary_y=False)
    fig.update_yaxes(title_text="Depth to water (m, deeper = lower)", autorange="reversed", secondary_y=True)
    fig.update_layout(title="Wet years refill the wells; the 2018 deficit pushed water deepest", height=420,
                      legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, width="stretch")
    st.caption(
        f"Based on {len(wells)} wells with near-complete 2015-2023 records. Correlation uses 9 yearly points. "
        "Low depth value = water close to the surface."
    )
    st.info(
        "What we do NOT claim: a proven long-term decline. Over 2015-2023 no well shows a statistically "
        "significant deepening trend at p<0.1 in raw data. Risk comes from rainfall dependence and persistent hotspots."
    )

# ============================ PAGE 2 =======================================
elif page.startswith("2"):
    st.title("Stress map: where water stays deep")
    mode = st.radio("Colour wells by", ["Persistent depth", "Trend after removing rainfall effect"], horizontal=True, key="mode")
    show_ind = st.checkbox("Show textile units", value=True)
    m = folium.Map(location=[25.45, 74.7], zoom_start=9, tiles="OpenStreetMap")
    for r in wells.itertuples():
        if mode == "Persistent depth":
            col = COLORS[depth_class(r.median_depth)]
        else:
            if pd.isna(r.p_adj):
                col = "#999999"
            elif r.p_adj < 0.1 and r.slope_rainadj > 0:
                col = "#c0392b"
            elif r.p_adj < 0.1 and r.slope_rainadj < 0:
                col = "#2e8b57"
            else:
                col = "#9aa5b1"
        tip = (f"<b>{r.Site}</b><br>Median post-monsoon depth: {r.median_depth:.1f} m<br>Aquifer: {r.Aquifer}<br>"
               f"Trend: {r.slope_m_yr:+.2f} m/yr (p={r.p:.2f})<br>Rain-adjusted: {r.slope_rainadj:+.2f} m/yr (p={r.p_adj:.2f})")
        folium.CircleMarker([r.Lat, r.Lon], radius=5 + r.median_depth / 2.5, color=col, fill=True,
                            fill_opacity=0.75, tooltip=tip).add_to(m)
    if show_ind:
        tcol = {"wet": "red", "spinning": "gray", "unclear": "orange"}
        for r in ind.itertuples():
            folium.Marker([r.Latitude, r.Longitude], icon=folium.Icon(color=tcol.get(r.Type_guess, "orange"), icon="industry", prefix="fa"),
                          tooltip=f"{r.Industry} ({r.Cluster}; type guess: {r.Type_guess})").add_to(m)
    st_folium(m, height=560, use_container_width=True, returned_objects=[])
    if mode == "Persistent depth":
        st.markdown("🔴 deep (>8 m)  🟠 moderate (4-8 m)  🟢 shallow (<4 m). Circle size grows with depth. Industry pins: red = wet processing (by name), grey = spinning, orange = unclear.")
    else:
        st.markdown("🔴 deepening after adjusting for rainfall (p<0.1)  🟢 improving  ⚪ no clear trend. With 25 wells tested, one or two hits can occur by chance, so read these as wells to watch.")
    t = wells[["Site", "Aquifer", "median_depth", "slope_m_yr", "p", "slope_rainadj", "p_adj", "Depth class"]].round(2)
    st.dataframe(t.sort_values("median_depth", ascending=False), width="stretch", hide_index=True)

# ============================ PAGE 3 =======================================
elif page.startswith("3"):
    st.title("Water quality (Shahpura block wells)")
    st.caption("Share of samples above BIS IS 10500 permissible limits: TDS 2000, fluoride 1.5, nitrate 45 mg/L.")
    rows = []
    for y, g in wq.groupby("Year"):
        row = {"Year": int(y), "Samples": len(g)}
        for k, lim in BIS.items():
            v = g[k].dropna()
            row[k] = 100 * (v > lim).mean() if len(v) else np.nan
        rows.append(row)
    ex = pd.DataFrame(rows)
    fig = go.Figure()
    for k in BIS:
        fig.add_scatter(x=ex.Year, y=ex[k], mode="lines+markers", name=f"{k} > {BIS[k]}")
    fig.update_layout(yaxis_title="% of samples above limit", height=380, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, width="stretch")
    st.warning("Sample count changes by year (see table), so year-to-year changes are indicative, not conclusive.")
    st.dataframe(ex.round(1), hide_index=True, width="stretch")
    yr = st.select_slider("Map year", sorted(wq.Year.unique().astype(int)), value=2023)
    param = st.selectbox("Parameter", list(BIS))
    g = wq[wq.Year == yr].dropna(subset=[param])
    m = folium.Map(location=[g.Latitude.mean(), g.Longitude.mean()], zoom_start=10, tiles="OpenStreetMap")
    for r in g.itertuples():
        v = getattr(r, param)
        folium.CircleMarker([r.Latitude, r.Longitude], radius=6, color="#c0392b" if v > BIS[param] else "#2e8b57",
                            fill=True, fill_opacity=0.8, tooltip=f"{r.Site}: {param} {v:.1f} mg/L").add_to(m)
    st_folium(m, height=460, use_container_width=True, returned_objects=[])
    st.caption("Red = above permissible limit. These wells are tens of km from the industrial areas, so this page shows regional quality, not proof of mill contamination. See cited WQI studies for in-city evidence.")

# ============================ PAGE 4 =======================================
elif page.startswith("4"):
    st.title("Industry & water use")
    c1, c2, c3 = st.columns(3)
    c1.metric("Listed textile units", len(ind) + 1, help="35 listed; 34 could be located on the map")
    c2.metric("Name suggests wet processing", int((ind.Type_guess == "wet").sum()))
    c3.metric("Industrial clusters", ind.Cluster.nunique())
    cl = ind.groupby(["Cluster", "Type_guess"]).size().unstack(fill_value=0)
    st.bar_chart(cl)
    st.caption("Type is a guess from unit names only. Check each unit's consent record.")
    b = bench.copy()
    b["Excess %"] = 100 * (b.iloc[:, 2] - b.iloc[:, 1]) / b.iloc[:, 1]
    fig = go.Figure()
    fig.add_bar(x=b.Process_Category, y=b.iloc[:, 1], name="CPCB/BEE standard")
    fig.add_bar(x=b.Process_Category, y=b.iloc[:, 2], name="Bhilwara cluster average")
    fig.update_layout(barmode="group", yaxis_title="Litres per metre of fabric", height=380, legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, width="stretch")
    st.caption("Cluster averages run roughly 17-21% above the standard in every category.")
    with st.expander("Unit list"):
        st.dataframe(ind[["S_No", "Industry", "Cluster", "Type_guess", "Latitude", "Longitude"]], hide_index=True, width="stretch")

# ============================ PAGE 5 =======================================
else:
    st.title("Proposed policy: Basin Water Credits")
    st.markdown(
        """
**Design principles**
1. **Volume only.** Credits cover freshwater withdrawal and reuse, never pollution. Toxins keep **hard legal limits** and cannot be offset.
2. **Local basin only.** Credits trade only inside Bhilwara, because water is local.
3. **Cap, then reward.** Each cluster gets a freshwater cap tied to local stress. Units below their benchmark earn credits; units above must buy them.
4. **Public verification.** Publish treated-volume and monitoring data, and cross-check meters against energy use.
        """
    )
    st.subheader("Illustrative credit calculator")
    st.caption("Scenario tool with user inputs. Not measured data: mill-level withdrawal is not public.")
    cat = st.selectbox("Process category", bench.Process_Category)
    row = bench[bench.Process_Category == cat].iloc[0]
    std, avg = float(row.iloc[1]), float(row.iloc[2])
    meters = st.slider("Fabric processed per year (million metres)", 1, 100, 40)
    achieved = st.slider("Unit's actual use (L per metre)", int(std * 0.5), int(avg * 1.4), int(avg))
    stress = st.select_slider("Local groundwater condition", ["Shallow (<4 m)", "Moderate (4-8 m)", "Deep (>8 m)"], value="Moderate (4-8 m)")
    mult = {"Shallow (<4 m)": 1.0, "Moderate (4-8 m)": 1.5, "Deep (>8 m)": 2.0}[stress]
    saved_kl = (std - achieved) * meters * 1e6 / 1000  # litres -> kilolitres
    credits = saved_kl / 10 * mult
    c1, c2, c3 = st.columns(3)
    c1.metric("Water vs standard (KL/yr)", f"{saved_kl:,.0f}")
    c2.metric("Stress multiplier", f"x{mult}")
    c3.metric("Credits (1 credit = 10 KL)", f"{credits:,.0f}", help="Negative = credits the unit must buy")
    st.markdown("Positive credits are earned by beating the benchmark; negative means the unit buys credits. The multiplier makes saving water worth more where wells stay deep.")

    st.subheader("Verification demo (SIMULATED data)")
    st.caption("Idea: a zero-liquid-discharge unit that reports treated flow should also show matching evaporator energy use. Big mismatches get flagged for inspection.")
    kwh_per_kl = st.slider("Assumed evaporator energy per KL (kWh) , adjust to real specs", 10, 60, 30)
    rng = np.random.default_rng(7)
    units = [f"Unit {i:02d}" for i in range(1, 13)]
    flow = rng.uniform(80, 300, len(units))
    energy = flow * kwh_per_kl * rng.normal(1.0, 0.07, len(units))
    cheat = rng.choice(len(units), 3, replace=False)
    energy[cheat] *= rng.uniform(0.35, 0.55, 3)
    sim = pd.DataFrame({"Unit": units, "Reported flow (KL/day)": flow.round(0), "Evaporator energy (kWh/day)": energy.round(0)})
    sim["kWh per KL"] = (sim["Evaporator energy (kWh/day)"] / sim["Reported flow (KL/day)"]).round(1)
    sim["Flag"] = np.where(sim["kWh per KL"] < 0.75 * kwh_per_kl, "INSPECT", "ok")
    fig = go.Figure(go.Bar(x=sim.Unit, y=sim["kWh per KL"], marker_color=np.where(sim.Flag == "INSPECT", "#c0392b", "#2e8b57")))
    fig.add_hline(y=0.75 * kwh_per_kl, line_dash="dash", annotation_text="flag threshold")
    fig.update_layout(yaxis_title="kWh per KL reported", height=340)
    st.plotly_chart(fig, width="stretch")
    st.dataframe(sim, hide_index=True, width="stretch")
    st.error("SIMULATED DATA. Real mill-level readings are not public. This shows what the analysis would do once data is opened.")
