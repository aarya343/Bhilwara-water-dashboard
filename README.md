# Bhilwara Groundwater Stress: cleaned data, analysis code and dashboard

**Author:** Aarya Nenawatee, TERI School of Advanced Studies, New Delhi
**Project:** Entry to the International Youth Environmental Challenge (IYEC) 2026-27
**Live dashboard:** https://bhilwara-water.streamlit.app/
**Code repository:** https://github.com/aarya343/Bhilwara-water-dashboard

## What this is
Cleaned tables and code behind a public dashboard on groundwater stress in Bhilwara district,
Rajasthan, India, and a proposed "Basin Water Credits" policy (volume-only credits, traded only
within the basin, hard limits on toxins, public verification).

## Main results (indicative; nine years of public well data)
- Post-monsoon depth to water tracks monsoon rainfall closely (Spearman about -0.85 on 9 yearly means).
- No well in the 25-well long-record set shows a statistically significant deepening trend (p<0.1).
- Three wells stay deep (median >8 m) even after the monsoon.
- After removing the rainfall effect, only Taswariya Bansa shows deepening (p about 0.045); with 25 tests this may be chance.

## Files
| File | Content |
|---|---|
| gw_tidy.csv | Pre- and post-monsoon depth to water (m below ground), 2015-2023, per well (long format) |
| trend_results.csv | Per-well Theil-Sen slope, Kendall p-value, rain-adjusted slope and p, rain correlation |
| rainfall.csv | Bhilwara district monsoon rainfall, normal vs actual, 2015-2023. Source:  Climate Hazards Center (CHC), UC Santa Barbara, CHIRPS v3 (InfraRed Precipitation with Station Data) gridded timeseries calibrated with Indian Meteorological Department (IMD) regional inputs.|
| water_quality.csv | Groundwater chemistry (TDS, fluoride, nitrate, etc.), Shahpura block wells, 2015-2023 |
| industries.csv | 34 textile units from a regulator list (Rajasthan State Pollution Control Board [RSPCB] Bhilwara Regional Office Consent Management Register, active October 2026 Directory) with coordinates found by the author by hand; "Type_guess" is inferred from unit names only |
| benchmarks.csv | Water-use benchmarks per metre of fabric. Source: Central Pollution Control Board (CPCB) "Comprehensive Industry Document for Textile Industry" combined with Bureau of Energy Efficiency (BEE) PAT Scheme specific water consumption thresholds. |
| trend_analysis.py | Reproduces trend_results.csv (run from this folder: `python code/trend_analysis.py`) |
| app.py, requirements.txt | Streamlit dashboard |

## Method (short)
Wells with at least 6 post-monsoon readings get a Theil-Sen slope and a Kendall-tau p-value against year.
To separate rainfall from trend, depth is regressed on monsoon rainfall and the residuals are tested the same way.
The dashboard's "long-record" set uses wells with at least 8 post-monsoon readings (25 wells).

## Sources and credit
Groundwater levels and quality: Central Ground Water Board (CGWB) / India-WRIS records, cleaned and reformatted by the author.
Rainfall, industry list and benchmarks: see the table above. Original data remain the property of their publishers;
please credit them when reusing these tables.

## Limits
- Only nine years of public well data; findings are indicative, not conclusive.
- Mill-level water withdrawal and effluent data are not public. The verification demo in the dashboard uses simulated data and is labelled as such.
- Water quality wells are tens of km from the industrial areas, so they describe regional quality, not mill contamination.
- Industry type (wet processing / spinning) is a guess from names; check consent records.

## Licence
Tables derived by the author and the code: CC BY 4.0 (data) and MIT (code), subject to the original publishers' terms.

Nenawatee, A. (2026). Bhilwara groundwater stress: cleaned data, analysis code and dashboard [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23302088

