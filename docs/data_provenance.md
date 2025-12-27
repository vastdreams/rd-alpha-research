# Data Provenance

Documentation of all data sources, transformations, and quality controls.

## Data Lineage

```
FMP API
    │
    ├── Income Statements (/income-statement/{symbol})
    │       │
    │       └── Extract: revenue, rd_expense, fiscal_year
    │               │
    │               └── Transform: R&D Intensity = rd_expense / revenue
    │
    ├── Company Profiles (/profile/{symbol})
    │       │
    │       └── Extract: sector, industry, market_cap
    │
    ├── Price History (/historical-price-full/{symbol})
    │       │
    │       └── Transform: July-June annual returns
    │
    └── S&P 500 Constituents (/sp500_constituent)
            │
            └── Universe definition (current members)
```

## Raw Data Quality

### Income Statements

| Check | Criteria | Action if Fail |
|-------|----------|----------------|
| Revenue positive | revenue > 0 | Exclude |
| R&D non-negative | rd_expense >= 0 | Set to 0 |
| Fiscal year valid | 1990 <= year <= 2025 | Exclude |
| Period annual | period == "FY" | Skip |

### Returns

| Check | Criteria | Action if Fail |
|-------|----------|----------------|
| Price positive | close > 0 | Exclude |
| Return bounded | -0.99 < return < 10.0 | Winsorize |
| Sufficient history | >= 200 trading days | Exclude |

## Transformations

### R&D Intensity

```python
def calculate_rd_intensity(rd_expense, revenue, sector):
    if revenue <= 0:
        return None
    
    raw_intensity = rd_expense / revenue
    
    # Apply sector cap
    cap = SECTOR_CAPS.get(sector, 1.0)
    capped_intensity = min(raw_intensity, cap)
    
    return capped_intensity * 100  # As percentage
```

### Annual Returns (July-June)

```python
def calculate_july_june_return(prices, year):
    # Get July 1 of formation year
    start_date = f"{year}-07-01"
    start_price = get_nearest_price(prices, start_date, direction="forward")
    
    # Get June 30 of following year
    end_date = f"{year + 1}-06-30"
    end_price = get_nearest_price(prices, end_date, direction="backward")
    
    if start_price is None or end_price is None:
        return None
    
    return (end_price / start_price) - 1
```

### Delisting Adjustment

```python
def adjust_for_delisting(return_value, delist_code):
    if delist_code is None:
        return return_value
    
    # CRSP delisting codes
    if delist_code in [500, 520, 560]:  # Mergers
        return return_value  # Use actual return
    elif delist_code >= 400:  # Bankruptcy/liquidation
        return -0.30  # Assume 30% loss (Shumway, 1997)
    
    return return_value
```

## Point-in-Time Rules

### Financial Data Lag

For portfolio formed in July of year T:
- Use FY(T-1) financial statements
- FY(T-1) ends December (T-1) for most companies
- Data available by April T at latest

Example:
- Formation: July 1, 2023
- Financial data: FY2022 (ending December 2022)
- Data published: March 2023

### Universe Membership

S&P 500 membership as of formation date.

Known limitation: FMP provides current constituents only.
For rigorous historical analysis, use:
- Compustat GVKEY-linked historical index constituents
- S&P historical files (subscription required)

## Data Version Control

Each research run records:

```json
{
  "data_version": "2025-01-15",
  "fmp_api_version": "v3",
  "extraction_date": "2025-01-15T10:30:00Z",
  "symbols_fetched": 503,
  "date_range": "2005-01-01 to 2024-12-31",
  "git_commit": "abc123..."
}
```

## Known Data Issues

### FMP Specific

1. **R&D field name changes**: Historically "researchAndDevelopmentExpenses", verify field name
2. **Missing R&D**: Some companies report R&D as $0 when not disclosed separately
3. **Restated financials**: FMP may overwrite historical data with restated figures
4. **S&P 500 history**: Limited to current constituents; no historical membership

### General

1. **Survivorship bias**: Only currently listed companies in universe
2. **Look-ahead in index**: Current S&P 500 members back-applied
3. **Currency**: All figures in USD (FMP normalizes)
4. **Fiscal year ends**: Mixed (Dec, Mar, Jun) - use calendarYear field

## Audit Trail

All data processing logged:

```
2025-01-15 10:30:00 INFO  Fetching AAPL income statement
2025-01-15 10:30:01 INFO  Extracted 10 annual periods
2025-01-15 10:30:01 WARN  AAPL FY2015 missing R&D, using 0
2025-01-15 10:30:02 INFO  AAPL R&D intensity: 7.8% (FY2023)
...
```

## Reproducibility

To reproduce exact results:

1. Use same FMP API version (v3)
2. Fix extraction date (data changes over time)
3. Use exact code version (git commit hash)
4. Same Python and package versions (requirements.txt)

