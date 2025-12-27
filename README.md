# R&D Alpha: Investment Intensity and Long-Term Stock Returns

Empirical evidence on the relationship between corporate R&D investment intensity and subsequent long-term equity returns.

**Live Platform:** [https://research.finsoeasy.com](https://research.finsoeasy.com)

## Abstract

This research examines whether companies with high research and development (R&D) expenditures relative to revenue generate superior long-term stock returns. Using data from S&P 500 constituents over multiple decades, we find that firms in the top quintile of R&D intensity outperform bottom-quintile firms by approximately 7 percentage points annually on a risk-adjusted basis.

The core thesis: R&D spending is expensed rather than capitalized under GAAP and IFRS, systematically understating the true economic value of innovation-intensive companies. This accounting treatment creates a persistent mispricing opportunity.

## Key Findings

| Metric | Q5 (High R&D) | Q1 (Low R&D) | Spread |
|--------|---------------|--------------|--------|
| Avg Annual Return | 15.2% | 8.1% | +7.1% |
| Sharpe Ratio | 0.72 | 0.41 | +0.31 |
| Win Rate (Annual) | 68% | 52% | +16% |

## Repository Structure

```
rd-alpha-research/
├── src/
│   ├── scoring/           # R&D intensity scoring algorithm
│   ├── backtesting/       # Portfolio backtest methodology
│   ├── factors/           # Factor premium calculations
│   └── data/              # Data acquisition utilities
├── paper/                 # Research paper (markdown)
├── notebooks/             # Jupyter notebooks for replication
├── data/                  # Data README and samples
└── docs/                  # Methodology documentation
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
- **Transaction Costs**: 10 bps round-trip (default)

## Citation

```bibtex
@software{sehgal2025rdalpha,
  author = {Sehgal, Abhishek},
  title = {R&D Alpha: Investment Intensity and Long-Term Stock Returns},
  year = {2025},
  url = {https://research.finsoeasy.com},
  repository = {https://github.com/vastdreams/rd-alpha-research}
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

This research builds upon foundational work in factor investing and R&D capitalization literature, including studies by Lev & Sougiannis (1996), Chan, Lakonishok & Sougiannis (2001), and Eberhart, Maxwell & Siddique (2004).

