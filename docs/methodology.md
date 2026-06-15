# Regulatory Friction and Foregone GDP: Quantifying the Economic Cost of Delayed and Cancelled Canadian Energy Projects

**Status:** Preliminary analysis (2026)

A research project quantifying the direct and indirect GDP loss from delayed, cancelled, and rejected Canadian oil and gas infrastructure projects, with particular attention to the role of regulatory and legal uncertainty.

## Research Question

**How much real GDP may Canada have forgone from delayed and cancelled oil and gas infrastructure projects, and what portion is plausibly linked to regulatory and legal uncertainty?**

## Key Findings (Preliminary)

- **$88.4B** in total proposed capex across delayed/cancelled projects in dataset
- **$41.2B** in friction-weighted capex from Canadian regulatory/legal friction alone (strict estimate)
- **$44.2B** in total capex classified as regulatory/legal friction (when including related projects)
- **Alberta exposure:** 22.7% of GDP in narrow direct energy industries; 61.1% in broad project-development exposure (2025)
- **Newfoundland & Labrador exposure:** 18.7% (narrow); 56.8% (broad)

### Covered Projects

- Energy East ($15.7B, crude pipeline, cancelled)
- Keystone XL (~$12B, crude pipeline, delayed/cancelled in US)
- Northern Gateway ($7.9B, crude pipeline + marine terminal, cancelled)
- Teck Frontier ($20.6B, oil sands mine, withdrawn)
- Pacific NorthWest LNG ($36B, LNG export, cancelled)

## Methodology

### Three-Tier NAICS Classification

Projects are mapped to three categories of NAICS industries:

1. **Tier 1 - Directly Affected Industries**
   - Oil and gas extraction (211, 213)
   - Pipeline transportation (4861, 4862)

2. **Tier 2 - Construction & Capital Formation**
   - Heavy and civil engineering construction (237)
   - Engineering services (5413)

3. **Tier 3 - Indirect Supply Chain**
   - Manufacturing (332, 333)
   - Transportation and logistics (482, 484, 493)
   - Professional services (541)

### GDP Estimation

**Construction Phase:**
```
LostConstructionGDP = Capex × DomesticShare × ValueAddedShare
```

**Operating Phase:**
```
LostOperatingGDP = AnnualOutputValue × ValueAddedShare × YearsLost
```

**Regulatory Attribution:**
Projects coded by stated reason for delay/cancellation:
- Regulatory/legal (scored 3)
- Mixed (scored 2)
- Market/cost (scored 1)

**Friction Index** (0-100 scale, evidence-adjusted):
```
AdjustedFrictionIndex = (RawScore / 3) × 100 × EvidenceWeight
```

### Sensitivity Analysis

Results reported in three scenarios:

| Scenario | Domestic Share | Value-Added Share | Regulatory Attribution |
| --- | --- | --- | --- |
| Conservative | 50% | 30% | 25% |
| Base | 65% | 40% | 50% |
| High | 80% | 50% | 75% |

## Data Sources

### Statistics Canada
- **Table 36-10-0434-06:** Gross domestic product at basic prices, by industry (annual)
- **Table 36-10-0711-01:** Provincial GDP by industry
- **Table 34-10-0035-01:** Capital and repair expenditures by industry

### FRED (Federal Reserve Economic Data)
- WTI crude oil prices (DCOILWTICO)
- Henry Hub natural gas prices (DHHNGSP)
- Fed funds rate (FEDFUNDS)
- CAD/USD exchange rate (DEXCAUS)

### Primary Sources
- Impact Assessment Agency of Canada project registry
- Company press releases and investor disclosures
- Government of Canada economic updates
- CEO statements and media reports

## Repository Structure

```
.
├── README.md                          # This file
├── METHODOLOGY.md                     # Detailed NAICS and GDP methodology
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git exclusions
│
├── src/
│   ├── download_fred.py              # Fetch FRED economic data
│   ├── download_statcan.py           # Fetch Statistics Canada tables
│   ├── clean_statcan.py              # Clean and filter StatCan data
│   ├── gdp_exposure.py               # Calculate GDP exposure by geography/industry
│   ├── build_project_dataset.py      # Manual project data entry scaffold
│   ├── red_tape_index.py             # Construct friction index and estimates
│   └── make_figures.py               # Generate all charts
│
├── data/
│   ├── raw/                          # Downloaded, unmodified data
│   │   ├── fred_*.csv
│   │   └── statcan_*.csv
│   └── manual/
│       └── project_dataset.csv       # Hand-coded project data (>1B capex)
│
├── outputs/
│   ├── tables/
│   │   ├── gdp_exposure_by_geography_year.csv
│   │   ├── project_red_tape_index_preliminary.csv
│   │   ├── project_red_tape_summary_by_bucket.csv
│   │   ├── strict_canadian_regulatory_estimate.csv
│   │   └── broader_energy_opportunity_cost_estimate.csv
│   └── figures/
│       ├── gdp_exposure_narrow_latest_year.png
│       ├── gdp_exposure_narrow_over_time.png
│       ├── gdp_exposure_broad_latest_year.png
│       ├── gdp_exposure_broad_over_time.png
│       ├── preliminary_friction_index_by_project.png
│       ├── project_count_by_status.png
│       ├── project_count_by_blocking_jurisdiction.png
│       ├── total_capex_by_project_type.png
│       ├── total_capex_by_bucket.png
│       ├── friction_weighted_capex_by_bucket.png
│       └── avg_friction_by_project_type.png
│
├── docs/
│   ├── paper_draft.md                # Main manuscript
│   ├── figures_and_tables.md         # Figure/table notes
│   └── bibliography.bib              # Citation library
│
└── notebooks/ (optional)
    └── exploratory_analysis.ipynb    # Ad-hoc analysis
```

## Quickstart: Reproduce the Analysis

### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/[user]/regulatory-friction-canadian-energy.git
cd regulatory-friction-canadian-energy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/{raw,manual} outputs/{tables,figures}
```

### 2. Add API Keys

Create a `.env` file in the project root:

```
FRED_API_KEY=your_fred_api_key_here
```

Get a FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html

### 3. Download and Process Data

```bash
# Download data from FRED and Statistics Canada
python src/download_fred.py
python src/download_statcan.py

# Clean and filter
python src/clean_statcan.py

# Calculate GDP exposure
python src/gdp_exposure.py
```

### 4. Populate Project Dataset

Edit `data/manual/project_dataset.csv` with project-level data:

```csv
project,country,province_state,project_type,primary_naics,capex_billion,status,status_3cat,cause_category,blocking_jurisdiction,evidence_score,proposed_year,expected_in_service_year,actual_cancel_delay_year,delay_years_by_2026
Energy East,Canada,AB-NB,Crude pipeline,4861,15.7,Cancelled,Delayed/cancelled,Regulatory,Canada,3,2013,2018,2017,8
...
```

Fields:
- `evidence_score`: 1-3 (low to high confidence in regulatory attribution)
- `status_3cat`: Delayed/cancelled, Operating/completed, or Starting/advancing
- `cause_category`: Regulatory, Market, Mixed, Cost, Legal, Policy, Permit, Consultation, Climate, Other

### 5. Build Red Tape Index

```bash
python src/red_tape_index.py
```

Outputs:
- `outputs/tables/project_red_tape_index_preliminary.csv` — full index with all scores
- `outputs/tables/strict_canadian_regulatory_estimate.csv` — domestic regulatory only
- `outputs/tables/broader_energy_opportunity_cost_estimate.csv` — broader estimate

### 6. Generate Figures

```bash
python src/make_figures.py
```

All figures saved to `outputs/figures/`.

## Paper Structure

The manuscript follows this outline (see `docs/paper_draft.md`):

1. **Introduction** — Problem statement and research question
2. **Literature Review** — Regulatory uncertainty literature
3. **Institutional Background** — Canadian energy regulatory timeline
4. **Data** — Project dataset, sources, inclusion criteria
5. **Methodology** — NAICS framework, GDP formulas, sensitivity approach
6. **Results** — Estimates by project type, geography, scenario
7. **Limitations** — Causality challenges, attribution, measurement error
8. **Conclusion** — Synthesis and policy implications

## Key Limitations

- **Causality:** Projects have multiple cancellation drivers. Attribution is estimated, not observed.
- **Capex ≠ GDP:** Capex is converted to GDP using domestic and value-added shares, not treated as direct GDP.
- **Delayed vs. Foregone:** Some delayed projects eventually completed (e.g., Trans Mountain). Cost-of-delay uses NPV logic.
- **NAICS Breadth:** NAICS 211 is broad. Industry movements are not attributed solely to delayed projects.
- **Attribution Weights:** Regulatory attribution scores are coded from primary sources but remain subjective.

## Key References

- Baker, Bloom & Davis (2016) — "Measuring Economic Policy Uncertainty" (*QJE*)
- Coffey, McLaughlin & Peretto (2020) — "The Cumulative Cost of Regulations" (*REDyn*)
- Gabriel & Kunga (2022) — "Development Approval Timelines... and New Housing Supply" (*UCLA*)
- OECD (2025) — *Economic Surveys: Canada 2025*
- C.D. Howe Institute (2025) — "Canada's Investment Crisis"

Full bibliography: see `docs/bibliography.bib`

## Contributing

This is a preliminary analysis. Contributions welcome:

- Additional projects (>$1B capex, cancelled/delayed since 2015)
- Refined capex or timing estimates
- Sensitivity analysis alternatives
- Peer review of friction scoring

Contact: [your email]

## License

This research and code are provided as-is for academic and policy purposes. Please cite as:

```
[Author]. "Regulatory Friction and Foregone GDP: Quantifying the Economic Cost of Delayed and Cancelled Canadian Energy Projects." [Journal/Institution], 2026.
```

## Disclaimer

This analysis is preliminary and subject to revision. Estimates are based on available public sources and involve subjective coding of project attributes. The authors do not make claims about precise causality between specific regulations and project outcomes, only that regulatory uncertainty is one plausible factor among several in project delays and cancellations.

---

**Questions or issues?** Open an issue on GitHub or contact the author.
