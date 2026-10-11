# Bhilwara-water-dashboard
A public dashboard and proposed policy for managing freshwater in Bhilwara, Rajasthan.
Built for the International Youth Environmental Challenge (IYEC).
**Live app:** [https://bhilwara-water.streamlit.app/]
## What it shows
- **Groundwater:** nine years (2015-2023) of well records, analysed with trend tests
  (Theil-Sen, Mann-Kendall) and adjusted for monsoon rainfall.
- **Key finding:** water levels track rainfall closely (Spearman -0.85). No well shows a
  statistically significant long-term decline, but a weak monsoon pushes levels down
  sharply, and a few wells stay deep even after good rain.
- **Water quality:** share of samples above BIS limits (TDS, fluoride, nitrate).
- **Industry:** 34 mapped textile units from a regulator list, with water-use benchmarks.
- **Proposal:** Basin Water Credits, volume only, local basin only, with hard limits on toxins.
## Data sources
- Groundwater levels and quality: CGWB / India-WRIS
- Rainfall: Primary Repository - Climate Hazards Centre (CHC), University of California, Santa Barbara (UCSB)
- Industry list: Rajasthan State Pollution Control Board (RSPCB) Regional Office, Bhilwara, October 2026 Active Directory
- Water-use benchmarks: Jointly compiled from the Central Pollution Control Board (CPCB) Sector-Specific Environmental Guidelines for Textile Industries & Bureau of Energy Efficiency (BEE) Perform, Achieve and Trade (PAT) Lifecycle Parameters.
## Limits
- Only nine years of public well data, so findings are indicative.
- Mill-level withdrawal and effluent data are not public.
- The verification demo on page 5 uses **simulated data** and is labelled as such.
- Industry type (wet/spinning) is guessed from unit names.
## Run locally
    pip install -r requirements.txt
    streamlit run app.py
## Author
Aarya Nenawatee
