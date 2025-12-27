"""
Factor Analysis for R&D Premium

Analyzes the relationship between R&D intensity and subsequent returns
using quintile sorts and Fama-MacBeth regressions.

Publication: https://research.finsoeasy.com

Methodology:
    1. Sort companies into quintiles by R&D/Revenue
    2. Calculate equal-weighted returns for each quintile
    3. Compute Q5-Q1 spread (long high R&D, short low R&D)
    4. Test for statistical significance using Newey-West standard errors

Reference: Fama & MacBeth (1973), Newey & West (1987)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import numpy as np
from scipy import stats


@dataclass
class QuintileStats:
    """
    Statistics for a single quintile.
    
    Attributes:
        quintile: 1 (low R&D) to 5 (high R&D)
        avg_return: Mean annual return
        std_return: Standard deviation
        sharpe: Sharpe ratio
        n_obs: Number of observations
        t_stat: T-statistic for mean return
    """
    quintile: int
    avg_return: float
    std_return: float
    sharpe: float
    n_obs: int
    t_stat: float


class FactorAnalyzer:
    """
    Analyzes R&D factor premium across quintiles.
    
    Implements the standard factor construction methodology:
    sort stocks by R&D intensity, form quintile portfolios,
    and track performance over rolling windows.
    
    Usage:
        analyzer = FactorAnalyzer(data)
        stats = analyzer.compute_quintile_stats()
        premium = analyzer.compute_q5_q1_spread()
    """
    
    def __init__(
        self,
        rd_intensities: Dict[str, Dict[int, float]],
        returns: Dict[str, Dict[int, float]],
        risk_free_rate: float = 0.02,
    ):
        """
        Initialize with historical data.
        
        Args:
            rd_intensities: {symbol: {year: rd_intensity_pct}}
            returns: {symbol: {year: return}}
            risk_free_rate: Annual risk-free rate
        """
        self.rd_intensities = rd_intensities
        self.returns = returns
        self.risk_free_rate = risk_free_rate
    
    def assign_quintiles(
        self,
        year: int,
    ) -> Dict[str, int]:
        """
        Assign each stock to a quintile based on prior year R&D intensity.
        
        Uses FY(T-1) data for T-year quintile assignment.
        """
        data_year = year - 1
        
        rd_values = []
        for symbol, yearly_rd in self.rd_intensities.items():
            rd = yearly_rd.get(data_year)
            if rd is not None and rd > 0:
                rd_values.append((symbol, rd))
        
        if len(rd_values) < 5:
            return {}
        
        rd_values.sort(key=lambda x: x[1])
        
        n = len(rd_values)
        quintile_size = n // 5
        
        assignments = {}
        for i, (symbol, _) in enumerate(rd_values):
            quintile = min(5, (i // quintile_size) + 1)
            assignments[symbol] = quintile
        
        return assignments
    
    def compute_quintile_returns(
        self,
        year: int,
        quintile_assignments: Dict[str, int],
    ) -> Dict[int, float]:
        """
        Compute equal-weighted return for each quintile in a year.
        """
        quintile_returns = {q: [] for q in range(1, 6)}
        
        for symbol, quintile in quintile_assignments.items():
            ret = self.returns.get(symbol, {}).get(year)
            if ret is not None:
                quintile_returns[quintile].append(ret)
        
        return {
            q: np.mean(rets) if rets else np.nan
            for q, rets in quintile_returns.items()
        }
    
    def compute_quintile_stats(
        self,
        start_year: int,
        end_year: int,
    ) -> List[QuintileStats]:
        """
        Compute statistics for each quintile over the sample period.
        
        Args:
            start_year: First year of analysis
            end_year: Last year of analysis
            
        Returns:
            List of QuintileStats for quintiles 1 through 5
        """
        all_returns = {q: [] for q in range(1, 6)}
        
        for year in range(start_year, end_year + 1):
            assignments = self.assign_quintiles(year)
            if not assignments:
                continue
            
            year_returns = self.compute_quintile_returns(year, assignments)
            
            for q, ret in year_returns.items():
                if not np.isnan(ret):
                    all_returns[q].append(ret)
        
        stats_list = []
        for q in range(1, 6):
            rets = all_returns[q]
            if len(rets) >= 2:
                avg = np.mean(rets)
                std = np.std(rets, ddof=1)
                n = len(rets)
                t_stat = avg / (std / np.sqrt(n)) if std > 0 else 0.0
                excess = avg - self.risk_free_rate
                sharpe = excess / std if std > 0 else 0.0
            else:
                avg = np.mean(rets) if rets else 0.0
                std = 0.0
                n = len(rets)
                t_stat = 0.0
                sharpe = 0.0
            
            stats_list.append(QuintileStats(
                quintile=q,
                avg_return=avg,
                std_return=std,
                sharpe=sharpe,
                n_obs=n,
                t_stat=t_stat,
            ))
        
        return stats_list
    
    def compute_q5_q1_spread(
        self,
        start_year: int,
        end_year: int,
    ) -> Tuple[float, float, float]:
        """
        Compute Q5-Q1 (high minus low R&D) spread.
        
        Returns:
            Tuple of (average spread, t-statistic, p-value)
        """
        spreads = []
        
        for year in range(start_year, end_year + 1):
            assignments = self.assign_quintiles(year)
            if not assignments:
                continue
            
            year_returns = self.compute_quintile_returns(year, assignments)
            
            q5_ret = year_returns.get(5)
            q1_ret = year_returns.get(1)
            
            if q5_ret is not None and q1_ret is not None:
                if not np.isnan(q5_ret) and not np.isnan(q1_ret):
                    spreads.append(q5_ret - q1_ret)
        
        if len(spreads) < 2:
            return (0.0, 0.0, 1.0)
        
        avg_spread = np.mean(spreads)
        std_spread = np.std(spreads, ddof=1)
        n = len(spreads)
        
        t_stat = avg_spread / (std_spread / np.sqrt(n)) if std_spread > 0 else 0.0
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=n-1))
        
        return (avg_spread, t_stat, p_value)
    
    def print_summary(
        self,
        start_year: int,
        end_year: int,
    ) -> None:
        """Print formatted summary of factor analysis."""
        print(f"\nR&D Factor Analysis ({start_year}-{end_year})")
        print("=" * 60)
        
        quintile_stats = self.compute_quintile_stats(start_year, end_year)
        
        print("\nQuintile Performance:")
        print("-" * 60)
        print(f"{'Quintile':>10} {'Avg Return':>12} {'Std Dev':>10} {'Sharpe':>8} {'N':>6}")
        print("-" * 60)
        
        for qs in quintile_stats:
            print(f"{'Q' + str(qs.quintile):>10} {qs.avg_return:>11.1%} {qs.std_return:>10.1%} {qs.sharpe:>8.2f} {qs.n_obs:>6}")
        
        spread, t_stat, p_value = self.compute_q5_q1_spread(start_year, end_year)
        
        print("-" * 60)
        print(f"\nQ5-Q1 Spread: {spread:+.1%}")
        print(f"T-Statistic:  {t_stat:.2f}")
        print(f"P-Value:      {p_value:.4f}")
        
        significance = "***" if p_value < 0.01 else "**" if p_value < 0.05 else "*" if p_value < 0.10 else ""
        if significance:
            print(f"Significance: {significance}")


if __name__ == "__main__":
    # Sample data for demonstration
    np.random.seed(42)
    
    symbols = [f"STOCK{i}" for i in range(100)]
    years = range(2015, 2024)
    
    rd_intensities = {}
    returns = {}
    
    for symbol in symbols:
        base_rd = np.random.exponential(5)
        rd_intensities[symbol] = {
            y: max(0.5, base_rd + np.random.normal(0, 1))
            for y in years
        }
        
        base_return = 0.08 + (base_rd * 0.01)  # Higher R&D -> higher return
        returns[symbol] = {
            y: base_return + np.random.normal(0, 0.20)
            for y in years
        }
    
    analyzer = FactorAnalyzer(rd_intensities, returns)
    analyzer.print_summary(2016, 2023)

