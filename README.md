> **⚠️ This repository has been archived. Development has moved to [fse-rnd-alpha](https://github.com/vastdreams/fse-rnd-alpha).**

---

# R&D Alpha: Investment Intensity and Long-Term Stock Returns

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://img.shields.io/badge/DOI-SSRN%20Pending-blue)](https://research.finsoeasy.com)

Empirical evidence on the relationship between corporate R&D investment intensity and subsequent long-term equity returns.

**Live Platform:** [https://research.finsoeasy.com](https://research.finsoeasy.com)  
**Full Paper (PDF):** [https://research.finsoeasy.com/rnd-alpha-paper.pdf](https://research.finsoeasy.com/rnd-alpha-paper.pdf)

## Abstract

This research examines whether companies with high research and development (R&D) expenditures relative to revenue generate superior long-term stock returns. Using data from S&P 500 constituents over 30 years (Jul1995-Jun2025), we find that firms in the top quintile of R&D intensity outperform bottom-quintile firms by approximately 3.73 percentage points annually.

The core thesis: R&D spending is expensed rather than capitalized under GAAP and IFRS, systematically understating the true economic value of innovation-intensive companies. This accounting treatment creates a persistent mispricing opportunity.

**Statistical significance** is established via:
- Fama-MacBeth cross-sectional regressions (p = 0.0737)
- Monthly factor spanning tests (FF5 alpha = 4.37%, p < 0.01)

## Key Findings

| Metric | Value | Period |
|--------|-------|--------|
| Annual HML_RD Premium | +3.73% | Jul1995-Jun2025 (30 years) |
| Win Rate (Annual) | 57% | 17 of 30 years positive |
| RD20 Net Premium vs SPY | +7.52%/yr | Jul2001-Jun2025 (24 years) |
| FF5 Alpha | +4.37%/yr | Monthly spanning (p < 0.01) |

## Repository Structure

```
rd-alpha-research/
├── src/
│   ├── scoring/           # R&D intensity scoring algorithm
│   ├── backtesting/       # Portfolio backtest methodology
│   ├── factors/           # Factor premium calculations
│   └── data/              # Data acquisition utilities
├── docs/                  # Methodology documentation
├── notebooks/             # Jupyter notebooks for replication
└── data/                  # Data README and samples
```

## Replication

### Prerequisites

```bash
python >= 3.10
pandas, numpy, scipy
sqlalchemy (optional, for database storage)
```

### Quick Start

```bash
# Clone the repository
git clone https://github.com/vastdreams/rd-alpha-research.git
cd rd-alpha-research

# Install dependencies
pip install -r requirements.txt

# Run the scoring algorithm on sample data
python src/scoring/rd_alpha_scorer.py --sample
```

### Data Acquisition

Financial data is sourced from Financial Modeling Prep (FMP) API. To replicate:

1. Obtain an API key from [financialmodelingprep.com](https://financialmodelingprep.com)
2. Set environment variable: `export FMP_API_KEY=your_key`
3. Run data ingestion: `python src/data/ingest_financials.py`

See `data/README.md` for detailed data provenance and schema.

## Methodology

### Scoring Formula

```
R&D Alpha Score = (RD_Intensity × Sector_Adj × Momentum × Quality) / Volatility
```

Where:
- **RD_Intensity**: R&D Expense / Revenue, capped by sector
- **Sector_Adj**: S&P 500 sector weight / High-R&D sector weight
- **Momentum**: 1 + (Prior 3-year excess return × 0.1), bounded [0.5, 2.0]
- **Quality**: Data quality score (0 to 1)
- **Volatility**: 3-year historical standard deviation, floored at 0.10

### Backtest Protocol

- **Formation Date**: July 1 (Fama-French convention)
- **Holding Period**: 12 months with annual rebalancing
- **Data Lag**: Uses FY(T-1) financials for T-year formation
- **Universe**: S&P 500 constituents (point-in-time)
- **Transaction Costs**: 18.3 bps round-trip (Novy-Marx & Velikov 2016)

## Citation

```bibtex
@techreport{sehgal2026rdalpha,
  author = {Sehgal, Abhishek},
  title = {R&D Alpha: Investment Intensity and Long-Term Stock Returns},
  year = {2026},
  month = {January},
  institution = {FSE Research & Investments Pty Ltd},
  url = {https://research.finsoeasy.com},
  note = {Working paper, Version 1.0}
}
```

## License

MIT License. See LICENSE for details.

## Acknowledgments

This research builds upon foundational work in factor investing and R&D capitalization literature, including studies by Lev & Sougiannis (1996), Chan, Lakonishok & Sougiannis (2001), Eberhart, Maxwell & Siddique (2004), and Ahmed, Bu & Ye (2023).

## Author

**Abhishek Sehgal**  
ORCID: [0009-0000-9424-4695](https://orcid.org/0009-0000-9424-4695)  
FSE Research & Investments Pty Ltd
