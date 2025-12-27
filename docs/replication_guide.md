# Replication Guide

Step-by-step instructions to replicate the R&D Alpha research findings.

## Prerequisites

### Software
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Data Access
- Financial Modeling Prep (FMP) API key
- Free tier sufficient for basic replication
- Sign up: https://financialmodelingprep.com

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/vastdreams/rd-alpha-research.git
cd rd-alpha-research
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

```bash
export FMP_API_KEY=your_api_key_here
```

Or create a `.env` file:
```
FMP_API_KEY=your_api_key_here
```

## Data Acquisition

### Fetch S&P 500 Data

```bash
python -c "
from src.data.data_acquisition import FMPClient, fetch_research_data

client = FMPClient()
symbols = client.get_sp500_constituents()
print(f'Found {len(symbols)} S&P 500 constituents')

# Fetch 10 years of data (may take 30+ minutes)
fetch_research_data(symbols, years=10)
"
```

### Verify Data

```bash
head data/raw/income_statements.csv
```

Expected output:
```
symbol,fiscal_year,revenue,rd_expense,net_income
AAPL,2023,383285000000,29915000000,96995000000
...
```

## Run Scoring

### Calculate R&D Alpha Scores

```bash
python src/scoring/rd_alpha_scorer.py
```

Expected output:
```
AAPL: R&D Intensity=7.8%, Score=35.45
MSFT: R&D Intensity=12.8%, Score=64.10
...
Top selections:
  1. AMGN (Healthcare) - Weight: 5.0%
  2. MSFT (Technology) - Weight: 5.0%
  ...
```

## Run Backtest

### Basic Backtest

```python
from src.backtesting.portfolio_backtest import PortfolioBacktester

# Load your data into the required format
# returns_data = {symbol: {year: return}, ...}
# financial_data = {symbol: {year: {revenue, rd_expense}}, ...}

backtester = PortfolioBacktester(
    returns_data=returns_data,
    financial_data=financial_data,
    transaction_cost=0.001  # 10 bps
)

result = backtester.run(
    start_year=2005,
    end_year=2024,
    n_holdings=20
)

print(f"Annualized Return: {result.annualized_return:.1%}")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
```

## Run Factor Analysis

### Quintile Analysis

```python
from src.factors.factor_analysis import FactorAnalyzer

analyzer = FactorAnalyzer(
    rd_intensities=rd_data,
    returns=returns_data
)

analyzer.print_summary(start_year=2005, end_year=2024)
```

Expected output:
```
R&D Factor Analysis (2005-2024)
============================================================

Quintile Performance:
------------------------------------------------------------
  Quintile   Avg Return    Std Dev   Sharpe      N
------------------------------------------------------------
        Q1       8.1%       18.2%     0.33     20
        Q2       9.4%       17.8%     0.42     20
        Q3      10.8%       17.5%     0.50     20
        Q4      12.3%       18.0%     0.57     20
        Q5      15.2%       19.1%     0.69     20
------------------------------------------------------------

Q5-Q1 Spread: +7.1%
T-Statistic:  2.85
P-Value:      0.0051
Significance: ***
```

## Jupyter Notebooks

For interactive exploration:

```bash
jupyter notebook notebooks/replication.ipynb
```

## Verification

### Compare with Paper

Your replicated results should match within reasonable tolerance:

| Metric | Paper | Your Result |
|--------|-------|-------------|
| Q5-Q1 Spread | 7.1% | ~ 6-8% |
| T-Statistic | 2.85 | > 2.0 |
| Sharpe Ratio | 0.72 | ~ 0.6-0.8 |

Differences may arise from:
- Data source variations
- Exact date handling
- Transaction cost assumptions
- S&P 500 membership timing

## Troubleshooting

### API Rate Limits

If you hit rate limits:
```python
import time
time.sleep(0.5)  # Add delay between requests
```

### Missing Data

Some symbols may lack R&D data:
```python
# Filter to symbols with valid R&D
valid = [s for s in symbols if s in rd_data and rd_data[s] > 0]
```

### Memory Issues

For large datasets:
```python
# Process in chunks
chunk_size = 100
for i in range(0, len(symbols), chunk_size):
    chunk = symbols[i:i+chunk_size]
    process_chunk(chunk)
```

## Support

For questions or issues:
- Open a GitHub issue: https://github.com/vastdreams/rd-alpha-research/issues
- Email: research@finsoeasy.com
- Live platform: https://research.finsoeasy.com

