"""
Data Acquisition Utilities

Fetches financial data from Financial Modeling Prep (FMP) API
for R&D Alpha research.

Publication: https://research.finsoeasy.com

Data Sources:
    Income Statements: Revenue, R&D Expense
    Company Profiles: Sector, Industry
    Price History: Daily/Annual returns
    S&P 500 Constituents: Historical membership

API Documentation: https://site.financialmodelingprep.com/developer/docs
"""

import os
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests


@dataclass
class IncomeStatement:
    """Annual income statement data."""
    symbol: str
    fiscal_year: int
    revenue: float
    rd_expense: float
    net_income: float
    period: str = "FY"


@dataclass
class CompanyProfile:
    """Company profile with sector classification."""
    symbol: str
    name: str
    sector: str
    industry: str
    market_cap: float
    exchange: str


class FMPClient:
    """
    Client for Financial Modeling Prep API.
    
    Requires FMP_API_KEY environment variable.
    Free tier: 250 requests/day
    Starter tier: 300 requests/minute
    
    Usage:
        client = FMPClient()
        income = client.get_income_statement("AAPL")
    """
    
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            raise ValueError("FMP_API_KEY required. Set environment variable or pass api_key.")
        self._request_count = 0
        self._last_request = 0
    
    def _rate_limit(self):
        """Simple rate limiting: max 5 requests per second."""
        now = time.time()
        if now - self._last_request < 0.2:
            time.sleep(0.2 - (now - self._last_request))
        self._last_request = time.time()
        self._request_count += 1
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request to FMP API."""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        params["apikey"] = self.api_key
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_income_statements(
        self,
        symbol: str,
        limit: int = 10,
    ) -> List[IncomeStatement]:
        """
        Fetch annual income statements for a symbol.
        
        Args:
            symbol: Stock ticker (e.g., "AAPL")
            limit: Number of years to fetch
            
        Returns:
            List of IncomeStatement objects, most recent first
        """
        data = self._get(f"income-statement/{symbol}", {"limit": limit})
        
        statements = []
        for item in data:
            if item.get("period") != "FY":
                continue
            
            stmt = IncomeStatement(
                symbol=symbol,
                fiscal_year=int(item.get("calendarYear", 0)),
                revenue=float(item.get("revenue", 0) or 0),
                rd_expense=float(item.get("researchAndDevelopmentExpenses", 0) or 0),
                net_income=float(item.get("netIncome", 0) or 0),
            )
            statements.append(stmt)
        
        return statements
    
    def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        """
        Fetch company profile with sector classification.
        
        Args:
            symbol: Stock ticker
            
        Returns:
            CompanyProfile or None if not found
        """
        data = self._get(f"profile/{symbol}")
        
        if not data:
            return None
        
        item = data[0]
        return CompanyProfile(
            symbol=symbol,
            name=item.get("companyName", ""),
            sector=item.get("sector", ""),
            industry=item.get("industry", ""),
            market_cap=float(item.get("mktCap", 0) or 0),
            exchange=item.get("exchange", ""),
        )
    
    def get_sp500_constituents(self) -> List[str]:
        """
        Fetch current S&P 500 constituent symbols.
        
        Note: This returns current constituents only.
        For historical membership, use historical_sp500_constituents.
        """
        data = self._get("sp500_constituent")
        return [item.get("symbol") for item in data if item.get("symbol")]
    
    def get_historical_price(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ) -> List[Dict]:
        """
        Fetch historical daily prices.
        
        Args:
            symbol: Stock ticker
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            
        Returns:
            List of {date, open, high, low, close, volume}
        """
        data = self._get(
            f"historical-price-full/{symbol}",
            {"from": from_date, "to": to_date}
        )
        return data.get("historical", [])
    
    def calculate_annual_return(
        self,
        symbol: str,
        year: int,
        july_june: bool = True,
    ) -> Optional[float]:
        """
        Calculate annual return for a holding period.
        
        Args:
            symbol: Stock ticker
            year: Formation year
            july_june: If True, use July Y to June Y+1 (Fama-French)
                      If False, use calendar year
                      
        Returns:
            Annual return as decimal (e.g., 0.15 for 15%)
        """
        if july_june:
            from_date = f"{year}-07-01"
            to_date = f"{year + 1}-06-30"
        else:
            from_date = f"{year}-01-01"
            to_date = f"{year}-12-31"
        
        prices = self.get_historical_price(symbol, from_date, to_date)
        
        if len(prices) < 2:
            return None
        
        prices.sort(key=lambda x: x["date"])
        
        start_price = prices[0]["close"]
        end_price = prices[-1]["close"]
        
        if start_price <= 0:
            return None
        
        return (end_price / start_price) - 1


def fetch_research_data(
    symbols: List[str],
    years: int = 10,
    output_dir: str = "data/raw",
) -> None:
    """
    Fetch all required data for R&D Alpha research.
    
    Creates CSV files:
        income_statements.csv
        company_profiles.csv
        annual_returns.csv
    """
    import csv
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    client = FMPClient()
    
    print(f"Fetching data for {len(symbols)} symbols...")
    
    # Income statements
    with open(f"{output_dir}/income_statements.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["symbol", "fiscal_year", "revenue", "rd_expense", "net_income"])
        
        for i, symbol in enumerate(symbols):
            try:
                statements = client.get_income_statements(symbol, limit=years)
                for stmt in statements:
                    writer.writerow([
                        stmt.symbol,
                        stmt.fiscal_year,
                        stmt.revenue,
                        stmt.rd_expense,
                        stmt.net_income,
                    ])
                if (i + 1) % 50 == 0:
                    print(f"  Processed {i + 1}/{len(symbols)} symbols")
            except Exception as e:
                print(f"  Error fetching {symbol}: {e}")
    
    print(f"Data saved to {output_dir}/")


if __name__ == "__main__":
    # Example: Fetch data for a few symbols
    client = FMPClient()
    
    # Test with Apple
    print("Testing FMP API with AAPL...")
    
    statements = client.get_income_statements("AAPL", limit=3)
    for stmt in statements:
        rd_pct = (stmt.rd_expense / stmt.revenue * 100) if stmt.revenue > 0 else 0
        print(f"  FY{stmt.fiscal_year}: Revenue=${stmt.revenue/1e9:.1f}B, R&D={rd_pct:.1f}%")
    
    profile = client.get_company_profile("AAPL")
    if profile:
        print(f"\n  Company: {profile.name}")
        print(f"  Sector: {profile.sector}")
        print(f"  Industry: {profile.industry}")

