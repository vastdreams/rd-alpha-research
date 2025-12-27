# Data Sources and Provenance

## Primary Data Source

**Financial Modeling Prep (FMP) API**
- Website: https://financialmodelingprep.com
- Documentation: https://site.financialmodelingprep.com/developer/docs

### Required Endpoints

| Endpoint | Data | Usage |
|----------|------|-------|
| `/income-statement/{symbol}` | Revenue, R&D Expense | R&D intensity calculation |
| `/profile/{symbol}` | Sector, Industry | Sector classification |
| `/historical-price-full/{symbol}` | Daily prices | Return calculation |
| `/sp500_constituent` | Current S&P 500 list | Universe definition |

### API Tiers

- Free: 250 requests/day
- Starter ($19/mo): 300 requests/minute
- Professional ($49/mo): Bulk endpoints

## Data Schema

### Income Statements
```
symbol: str          # Stock ticker
fiscal_year: int     # Calendar year ending
revenue: float       # Total revenue (USD)
rd_expense: float    # R&D expense (USD)
period: str          # "FY" for annual
```

### Company Profiles
```
symbol: str          # Stock ticker
name: str            # Company name
sector: str          # GICS sector
industry: str        # GICS industry
market_cap: float    # Market capitalization (USD)
exchange: str        # Primary exchange
```

### Annual Returns
```
symbol: str          # Stock ticker
year: int            # Formation year
return_jj: float     # July-June return (decimal)
return_cy: float     # Calendar year return (decimal)
```

## Point-in-Time Considerations

To avoid look-ahead bias:

1. **Financial Data**: Use FY(T-1) for T-year formation
   - Example: For July 2023 formation, use FY2022 financials

2. **S&P 500 Membership**: Use historical constituents as of formation date
   - FMP historical endpoint or alternative sources

3. **Delisting**: Include delisting returns for companies that exit the universe
   - CRSP delisting codes (if available) or assume -30% for delists

## Replication Steps

1. Obtain FMP API key
2. Set environment variable: `export FMP_API_KEY=your_key`
3. Run data acquisition:
   ```bash
   python src/data/data_acquisition.py
   ```
4. Data files created in `data/raw/`

## Alternative Data Sources

For academic replication with CRSP/Compustat:

| FMP Field | CRSP/Compustat Equivalent |
|-----------|---------------------------|
| revenue | REVT (Compustat) |
| rd_expense | XRD (Compustat) |
| sector | GICS sector (Compustat) |
| price | PRC (CRSP) |
| return | RET (CRSP) |
| delisting | DLRET (CRSP) |

## Sample Data

Sample data files for testing are not included to avoid copyright issues.
Use the data acquisition scripts to fetch fresh data from FMP.

