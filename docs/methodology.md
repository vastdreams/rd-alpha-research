# Methodology

## Research Design

This study examines the relationship between corporate R&D investment intensity and subsequent long-term stock returns using a factor-based approach.

### Core Hypothesis

Companies with high R&D expenditure relative to revenue generate superior risk-adjusted returns because:

1. **Accounting Treatment**: R&D is expensed under GAAP/IFRS rather than capitalized, systematically understating the asset value of innovation-intensive firms

2. **Analyst Coverage**: High-R&D firms are harder to value, leading to less analyst coverage and greater mispricing opportunities

3. **Short-term Bias**: Expensing R&D penalizes current earnings, causing short-term focused investors to undervalue these firms

## Universe Definition

### Primary Universe
- S&P 500 constituents as of formation date
- Point-in-time membership to avoid survivorship bias
- Minimum $100M annual revenue (excludes pre-revenue companies)
- At least 3 years of R&D data history

### Exclusions
- Financial sector (different R&D accounting)
- Utilities (regulated, minimal R&D)
- REITs (different business model)

## R&D Intensity Calculation

```
R&D Intensity = R&D Expense / Total Revenue
```

Where:
- R&D Expense: "Research and Development Expenses" from income statement
- Total Revenue: "Total Revenue" from income statement
- Data source: FY(T-1) for T-year portfolio formation

### Sector Caps

To prevent extreme values in high-R&D sectors:

| Sector | Maximum R&D Intensity |
|--------|----------------------|
| Biotechnology | 200% |
| Pharmaceuticals | 200% |
| Healthcare | 200% |
| Technology | 100% |
| All Others | 100% |

## Portfolio Construction

### Formation Date
July 1 of each year (Fama-French convention)

Rationale: Most fiscal years end in December or March. By July, annual reports are public, ensuring no look-ahead bias.

### Holding Period
12 months with annual rebalancing

### Weighting
Equal-weighted within the portfolio

Rationale: Market-cap weighting would overweight large tech firms; equal weighting captures the R&D effect more purely.

### Number of Holdings
20 companies (top quintile of R&D intensity)

## Return Calculation

### July-June Returns

For year T formation:
```
Return = (Price on June 30, T+1) / (Price on July 1, T) - 1
```

Adjusted for dividends and splits.

### Delisting Adjustment

For companies that delist during the holding period:
- Use CRSP delisting return if available
- Otherwise, assume -30% (Shumway, 1997)

### Transaction Costs

Default assumption: 10 basis points round-trip

Incorporates:
- Bid-ask spread
- Market impact
- Commission (negligible for institutional investors)

## Performance Metrics

### Annualized Return
```
Annualized = (1 + Cumulative)^(1/Years) - 1
```

### Volatility
```
Vol = StdDev(Annual Returns)
```

### Sharpe Ratio
```
Sharpe = (Return - Risk-Free) / Volatility
```

Risk-free rate: 10-year Treasury yield

### Maximum Drawdown
```
MaxDD = Max[(Peak - Trough) / Peak]
```

Computed from monthly cumulative returns.

## Statistical Testing

### T-Statistics

For quintile spreads:
```
t = Mean(Q5 - Q1) / SE(Q5 - Q1)
```

Standard errors adjusted for autocorrelation using Newey-West (1987) with 3 lags.

### Significance Levels
- *: p < 0.10
- **: p < 0.05
- ***: p < 0.01

## Robustness Checks

1. **Alternative Windows**: 5-year, 10-year, 20-year rolling
2. **Value-Weighting**: Market-cap weighted portfolios
3. **Sector Neutrality**: Long-short within sectors
4. **Size Controls**: Separate analysis by market cap decile
5. **Calendar Effects**: January effect, tax-loss selling

## Limitations

1. **Survivorship Bias**: Historical S&P 500 membership data may be incomplete
2. **Look-ahead Bias**: Point-in-time financials require careful data handling
3. **Transaction Costs**: Actual costs may vary from assumptions
4. **Factor Exposure**: R&D premium may overlap with size/value factors
5. **Regime Changes**: Relationship may weaken as strategy becomes known

## References

- Chan, L., Lakonishok, J., & Sougiannis, T. (2001). The stock market valuation of research and development expenditures. Journal of Finance, 56(6), 2431-2456.
- Fama, E., & French, K. (1992). The cross-section of expected stock returns. Journal of Finance, 47(2), 427-465.
- Fama, E., & MacBeth, J. (1973). Risk, return, and equilibrium: Empirical tests. Journal of Political Economy, 81(3), 607-636.
- Lev, B., & Sougiannis, T. (1996). The capitalization, amortization, and value-relevance of R&D. Journal of Accounting and Economics, 21(1), 107-138.
- Newey, W., & West, K. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. Econometrica, 55(3), 703-708.
- Shumway, T. (1997). The delisting bias in CRSP data. Journal of Finance, 52(1), 327-340.

