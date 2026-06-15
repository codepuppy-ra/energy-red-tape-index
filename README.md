
# Canada Energy Regulatory Friction Project

This repository builds a project-level dataset and preliminary empirical framework for studying regulatory friction in Canadian oil and gas infrastructure projects.

## Research Question

How can regulatory delay and approval uncertainty be measured at the project level, and what are the potential implications for capital formation, project completion, and GDP exposure in Canada’s oil and gas sector?

## Core Mechanism

Regulatory friction may increase approval time, uncertainty, and cost. This can reduce the probability that major energy projects proceed to construction or operation. Delayed or cancelled projects may reduce capital formation, construction activity, operating output, transportation capacity, and market access.

## Main Components

1. Project-level dataset of major oil and gas projects
2. NAICS-based industry mapping
3. Statistics Canada GDP and capital expenditure data
4. Regulatory Friction / Red Tape Index
5. Preliminary GDP exposure estimates

## Key StatCan Tables

- 36-10-0434-06: Canada GDP by industry, annual
- 36-10-0711-01: Provincial GDP by industry
- 34-10-0035-01: Capital and repair expenditures by industry and geography

## Core NAICS Codes

T001, 211, 21111, 213, 21311A, 23, 23B, 23X, 48-49, 486, 486A, 4862, 54, 5413, 31-33, 324, 331, 3311, 3312, 332, 333

## Key Preliminary Findings

### Project-Level Dataset
- **5 major projects** (>$1B capex each)
- **$88.4B** total proposed capital expenditure
- **All delayed or cancelled, 2015-2025**

### Direct GDP Estimates (Base Case)
- **Construction GDP loss:** ~$15-20B
- **Operating GDP loss (10-year):** ~$40-60B
- **Total estimated foregone GDP:** ~$50-80B

### Regulatory Attribution
- **Strict estimate** (Canadian regulatory/legal only): **$41.2B** friction-weighted capex
- **Broader estimate** (all regulatory + market): **$44.2B** friction-weighted capex
- **Attribution sensitivity:** 25%-75% of delays linked to regulatory uncertainty

### Provincial GDP Exposure
| Geography | Narrow Energy Exposure | Broad Project Exposure |
|-----------|----------------------|----------------------|
| Alberta | 22.7% of GDP | 61.1% of GDP |
| Newfoundland & Labrador | 18.7% | 56.8% |
| Saskatchewan | 12.4% | 45.2% |
| British Columbia | 3.2% | 35.4% |

**Interpretation:** Alberta's economy is deeply exposed to energy project delays.

## Project Status Categories

- Starting / advancing
- Operating / completed
- Delayed / cancelled / withdrawn / suspended

## Method

This project uses an observational project-level design. It combines descriptive statistics, index construction, NAICS-based industry mapping, and counterfactual GDP exposure estimates.

The core index is:

Adjusted Friction Score = Raw Friction Score × Evidence Weight

where Evidence Weight reflects the strength of company, regulatory, court, or government evidence linking a project outcome to regulatory, legal, permitting, or policy uncertainty.
