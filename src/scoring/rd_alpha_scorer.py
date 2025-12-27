"""
R&D Alpha Scoring Engine

Research-based scoring algorithm for identifying companies with high
R&D investment intensity. Used to construct the ETF20 R&D Alpha portfolio.

Publication: https://research.finsoeasy.com

Scoring Formula:
    R&D Alpha Score = (RD_Intensity x Sector_Adj x Momentum x Quality) / Volatility

Components:
    RD_Intensity: R&D Expense / Revenue, capped by sector (e.g., 200% for biotech)
    Sector_Adj:   S&P 500 sector weight / High-R&D sector weight
    Momentum:     1 + (Prior 3-year excess return x 0.1), bounded [0.5, 2.0]
    Quality:      Data quality score (0 to 1)
    Volatility:   3-year historical standard deviation, floored at 0.10

Reference: Lev & Sougiannis (1996), Chan et al. (2001)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np


# S&P 500 Sector Weights (December 2024)
# Source: S&P Dow Jones Indices
SP500_SECTOR_WEIGHTS = {
    "Technology": 0.295,
    "Information Technology": 0.295,
    "Healthcare": 0.125,
    "Health Care": 0.125,
    "Financials": 0.130,
    "Consumer Discretionary": 0.105,
    "Communication Services": 0.085,
    "Industrials": 0.085,
    "Consumer Staples": 0.060,
    "Energy": 0.040,
    "Utilities": 0.025,
    "Real Estate": 0.025,
    "Materials": 0.025,
    "Basic Materials": 0.025,
}

# Sector-specific R&D intensity caps
SECTOR_RD_CAPS = {
    "Healthcare": 2.00,
    "Health Care": 2.00,
    "Biotechnology": 2.00,
    "Pharmaceuticals": 2.00,
    "Technology": 1.00,
    "Information Technology": 1.00,
    "default": 1.00,
}


@dataclass
class RDAlphaScore:
    """
    Complete scoring breakdown for a single company.
    
    Attributes:
        symbol: Stock ticker
        name: Company name
        sector: GICS sector classification
        rd_intensity: Raw R&D/Revenue ratio (percentage)
        rd_intensity_capped: After sector-specific cap (percentage)
        sector_adjustment: Diversification multiplier
        momentum_factor: Based on prior 3-year performance
        quality_score: Data completeness (0 to 1)
        volatility: 3-year historical standard deviation
        raw_score: Before sector constraints
        final_score: After all adjustments
        weight: Portfolio weight (0 to 1)
        selection_rank: Rank in final selection
    """
    symbol: str
    name: str
    sector: str
    rd_intensity: float = 0.0
    rd_intensity_capped: float = 0.0
    sector_adjustment: float = 1.0
    momentum_factor: float = 1.0
    quality_score: float = 1.0
    volatility: float = 0.20
    raw_score: float = 0.0
    final_score: float = 0.0
    weight: float = 0.0
    selection_rank: int = 0
    years_of_data: int = 0
    latest_revenue: float = 0.0
    latest_rd_expense: float = 0.0


class RDAlphaScorer:
    """
    Research-based scoring engine for R&D Alpha portfolio construction.
    
    The scorer applies four factors to rank companies:
    1. R&D Intensity (primary signal from Paper 1)
    2. Sector Adjustment (prevents tech/biotech overconcentration, Paper 2)
    3. Momentum (R&D premium persistence, Paper 3)
    4. Volatility Normalization (risk adjustment, Paper 4)
    
    Usage:
        scorer = RDAlphaScorer()
        scores = scorer.calculate_scores(companies_df)
        top_20 = scorer.select_top_n(scores, n=20)
    """
    
    MAX_SECTOR_WEIGHT = 0.25
    MIN_SECTOR_WEIGHT = 0.02
    DEFAULT_VOLATILITY = 0.25
    VOLATILITY_FLOOR = 0.10
    MIN_MOMENTUM_FACTOR = 0.5
    MAX_MOMENTUM_FACTOR = 2.0
    
    def __init__(
        self,
        sector_weights: Optional[Dict[str, float]] = None,
        sector_caps: Optional[Dict[str, float]] = None,
    ):
        self.sector_weights = sector_weights or SP500_SECTOR_WEIGHTS
        self.sector_caps = sector_caps or SECTOR_RD_CAPS
    
    def get_sector_cap(self, sector: str) -> float:
        """Get R&D intensity cap for a sector."""
        return self.sector_caps.get(sector, self.sector_caps.get("default", 1.0))
    
    def get_sector_adjustment(self, sector: str) -> float:
        """
        Calculate sector adjustment to prevent overconcentration.
        
        High-R&D sectors (tech, healthcare) are downweighted to maintain
        diversification across the portfolio.
        """
        high_rd_sectors = {"Technology", "Information Technology", "Healthcare", "Health Care"}
        if sector in high_rd_sectors:
            target = self.sector_weights.get(sector, 0.10)
            high_rd_total = sum(
                self.sector_weights.get(s, 0.0) for s in high_rd_sectors
            )
            if high_rd_total > 0:
                return target / high_rd_total
        return 1.0
    
    def calculate_momentum_factor(
        self,
        prior_return: float,
        benchmark_return: float,
    ) -> float:
        """
        Calculate momentum factor from prior 3-year excess return.
        
        Args:
            prior_return: Company's 3-year cumulative return
            benchmark_return: Benchmark (e.g., S&P 500) 3-year return
            
        Returns:
            Momentum factor bounded between 0.5 and 2.0
        """
        excess = prior_return - benchmark_return
        factor = 1.0 + (excess * 0.1)
        return np.clip(factor, self.MIN_MOMENTUM_FACTOR, self.MAX_MOMENTUM_FACTOR)
    
    def score_company(
        self,
        symbol: str,
        name: str,
        sector: str,
        rd_expense: float,
        revenue: float,
        volatility: Optional[float] = None,
        prior_3yr_return: float = 0.0,
        benchmark_3yr_return: float = 0.0,
        quality_score: float = 1.0,
    ) -> RDAlphaScore:
        """
        Calculate R&D Alpha score for a single company.
        
        Args:
            symbol: Stock ticker
            name: Company name
            sector: GICS sector
            rd_expense: Annual R&D expense (dollars)
            revenue: Annual revenue (dollars)
            volatility: 3-year standard deviation (optional)
            prior_3yr_return: Company's cumulative 3-year return
            benchmark_3yr_return: S&P 500 cumulative 3-year return
            quality_score: Data quality (0 to 1)
            
        Returns:
            RDAlphaScore with all components and final score
        """
        if revenue <= 0:
            return RDAlphaScore(symbol=symbol, name=name, sector=sector)
        
        rd_intensity = (rd_expense / revenue) * 100.0
        sector_cap = self.get_sector_cap(sector)
        rd_intensity_capped = min(rd_intensity, sector_cap * 100)
        
        sector_adj = self.get_sector_adjustment(sector)
        momentum = self.calculate_momentum_factor(prior_3yr_return, benchmark_3yr_return)
        vol = max(volatility or self.DEFAULT_VOLATILITY, self.VOLATILITY_FLOOR)
        
        raw_score = rd_intensity_capped * sector_adj * momentum * quality_score
        final_score = raw_score / vol
        
        return RDAlphaScore(
            symbol=symbol,
            name=name,
            sector=sector,
            rd_intensity=rd_intensity,
            rd_intensity_capped=rd_intensity_capped,
            sector_adjustment=sector_adj,
            momentum_factor=momentum,
            quality_score=quality_score,
            volatility=vol,
            raw_score=raw_score,
            final_score=final_score,
            latest_revenue=revenue,
            latest_rd_expense=rd_expense,
        )
    
    def select_top_n(
        self,
        scores: List[RDAlphaScore],
        n: int = 20,
        equal_weight: bool = True,
    ) -> List[RDAlphaScore]:
        """
        Select top N companies by R&D Alpha score.
        
        Applies sector constraints to prevent overconcentration:
        max 25% in any single sector.
        
        Args:
            scores: List of RDAlphaScore objects
            n: Number of holdings to select
            equal_weight: If True, assign equal weights; otherwise score-weighted
            
        Returns:
            Top N companies with assigned weights and ranks
        """
        sorted_scores = sorted(scores, key=lambda x: x.final_score, reverse=True)
        
        selected = []
        sector_counts = {}
        max_per_sector = max(1, n // 4)
        
        for score in sorted_scores:
            if len(selected) >= n:
                break
            
            current_count = sector_counts.get(score.sector, 0)
            if current_count >= max_per_sector:
                continue
            
            sector_counts[score.sector] = current_count + 1
            selected.append(score)
        
        if equal_weight:
            weight = 1.0 / len(selected) if selected else 0.0
            for i, s in enumerate(selected):
                s.weight = weight
                s.selection_rank = i + 1
        else:
            total_score = sum(s.final_score for s in selected)
            for i, s in enumerate(selected):
                s.weight = s.final_score / total_score if total_score > 0 else 0.0
                s.selection_rank = i + 1
        
        return selected


if __name__ == "__main__":
    # Sample usage with mock data
    scorer = RDAlphaScorer()
    
    sample_companies = [
        ("AAPL", "Apple Inc.", "Technology", 29_915_000_000, 383_285_000_000, 0.22),
        ("MSFT", "Microsoft Corp.", "Technology", 27_195_000_000, 211_915_000_000, 0.20),
        ("AMGN", "Amgen Inc.", "Healthcare", 4_537_000_000, 26_323_000_000, 0.25),
        ("JNJ", "Johnson & Johnson", "Healthcare", 14_603_000_000, 85_159_000_000, 0.15),
        ("XOM", "Exxon Mobil", "Energy", 1_200_000_000, 344_582_000_000, 0.28),
    ]
    
    scores = []
    for symbol, name, sector, rd, rev, vol in sample_companies:
        score = scorer.score_company(
            symbol=symbol,
            name=name,
            sector=sector,
            rd_expense=rd,
            revenue=rev,
            volatility=vol,
        )
        scores.append(score)
        print(f"{symbol}: R&D Intensity={score.rd_intensity:.1f}%, Score={score.final_score:.2f}")
    
    print("\nTop selections:")
    for s in scorer.select_top_n(scores, n=3):
        print(f"  {s.selection_rank}. {s.symbol} ({s.sector}) - Weight: {s.weight:.1%}")

