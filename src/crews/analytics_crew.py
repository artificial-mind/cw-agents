"""
Analytics Crew - Handles KPIs, reports, trends, and forecasting.
Replaces AnalyticsAgent from old architecture.

Features preserved:
- Generate comprehensive reports
- Calculate KPIs
- Analyze trends
- Forecast performance
- Cache results (3600s TTL)
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json

from crewai import Agent, Task, Crew, Process

from ..core.llm_factory import get_llm, get_llm_with_retry
from ..tools.mcp_tools import MCPToolFactory
from ..infrastructure.redis_client import get_redis_client
from ..core.config import settings

logger = logging.getLogger(__name__)


class AnalyticsCrew:
    """
    Analytics Crew for reporting, KPIs, trends, and forecasting.
    
    Agents:
    - KPI Analyst: Calculates and analyzes key performance indicators
    - Report Generator: Creates comprehensive reports and forecasts
    
    Features:
    - KPI calculation and analysis
    - Report generation
    - Trend analysis
    - Performance forecasting
    - Result caching (1 hour TTL)
    """
    
    def __init__(self):
        self.name = "analytics_crew"
        self.tools = MCPToolFactory.get_analytics_tools()
        
        # Create agents
        self.kpi_analyst = self._create_kpi_analyst()
        self.report_generator = self._create_report_generator()
        
        logger.info(f"AnalyticsCrew initialized with {len(self.tools)} tools")
    
    def _create_kpi_analyst(self) -> Agent:
        """Create KPI analyst agent."""
        return Agent(
            role="Logistics KPI Analyst",
            goal="Calculate and analyze key performance indicators for logistics operations",
            backstory="""You are a data analyst specializing in logistics KPIs. You excel
            at identifying meaningful metrics, calculating accurate statistics, and providing
            actionable insights from data. You understand industry benchmarks and can
            identify performance gaps and opportunities.""",
            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm=get_llm()
        )
    
    def _create_report_generator(self) -> Agent:
        """Create report generator agent."""
        return Agent(
            role="Analytics Report Specialist",
            goal="Generate comprehensive reports with insights, trends, and forecasts",
            backstory="""You are a reporting expert with deep knowledge of logistics analytics.
            You create clear, actionable reports that combine historical data, trend analysis,
            and future forecasting. You understand how to present complex data in ways that
            drive business decisions.""",
            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm=get_llm()
        )
    
    def _generate_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """Generate cache key from parameters."""
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{prefix}_{param_hash}"
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get result from cache if available."""
        redis_client = await get_redis_client()
        cached = await redis_client.get_cache(cache_key)
        if cached:
            logger.info(f"Cache hit for {cache_key}")
        return cached
    
    async def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache result with TTL."""
        redis_client = await get_redis_client()
        await redis_client.set_cache(cache_key, result, ttl=settings.ANALYTICS_CACHE_TTL)
        logger.info(f"Cached result for {cache_key} (TTL: {settings.ANALYTICS_CACHE_TTL}s)")
    
    async def initialize(self):
        """Initialize crew resources."""
        logger.info(f"{self.name} initialized")
    
    async def cleanup(self):
        """Cleanup crew resources."""
        logger.info(f"{self.name} cleaned up")
    
    async def generate_report(
        self,
        report_type: str,
        start_date: str,
        end_date: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate analytics report.
        
        Args:
            report_type: Type of report
            start_date: Start date
            end_date: End date
            filters: Additional filters
        
        Returns:
            Report data
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key("report", {
                "type": report_type,
                "start": start_date,
                "end": end_date,
                "filters": filters or {}
            })
            
            cached = await self._get_cached_result(cache_key)
            if cached:
                return {**cached, "cached": True}
            
            # Generate new report
            llm = await get_llm_with_retry()
            self.report_generator.llm = llm
            
            filter_str = ", ".join([f"{k}={v}" for k, v in (filters or {}).items()])
            
            task = Task(
                description=f"""Generate a comprehensive {report_type} report for the period
                from {start_date} to {end_date}. Apply filters: {filter_str or 'none'}.
                
                The report should include:
                - Executive summary
                - Key metrics and KPIs
                - Trend analysis
                - Notable events or anomalies
                - Recommendations for improvement
                
                Present data clearly with insights that drive action.""",
                expected_output="Comprehensive report with metrics, trends, and recommendations",
                agent=self.report_generator
            )
            
            crew = Crew(
                agents=[self.report_generator],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            response = {
                "success": True,
                "report_type": report_type,
                "start_date": start_date,
                "end_date": end_date,
                "filters": filters,
                "result": str(result),
                "generated_at": datetime.now().isoformat(),
                "cached": False
            }
            
            # Cache result
            await self._cache_result(cache_key, response)
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                "success": False,
                "report_type": report_type,
                "error": str(e)
            }
    
    async def calculate_kpis(
        self,
        start_date: str,
        end_date: str,
        kpi_types: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate KPIs for date range.
        
        Args:
            start_date: Start date
            end_date: End date
            kpi_types: Specific KPIs to calculate
        
        Returns:
            KPI values
        """
        try:
            # Check cache
            cache_key = self._generate_cache_key("kpis", {
                "start": start_date,
                "end": end_date,
                "types": kpi_types or []
            })
            
            cached = await self._get_cached_result(cache_key)
            if cached:
                return {**cached, "cached": True}
            
            # Calculate KPIs
            llm = await get_llm_with_retry()
            self.kpi_analyst.llm = llm
            
            kpi_list = ", ".join(kpi_types) if kpi_types else "all standard logistics KPIs"
            
            task = Task(
                description=f"""Calculate {kpi_list} for the period from {start_date} to {end_date}.
                
                Calculate:
                - On-time delivery rate
                - Average delivery time
                - Exception rate
                - Customer satisfaction score
                - Cost per shipment
                - Route efficiency
                
                For each KPI, provide the value, comparison to previous period, and
                benchmark comparison if available.""",
                expected_output="Complete KPI calculations with comparisons and benchmarks",
                agent=self.kpi_analyst
            )
            
            crew = Crew(
                agents=[self.kpi_analyst],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            response = {
                "success": True,
                "start_date": start_date,
                "end_date": end_date,
                "kpi_types": kpi_types,
                "result": str(result),
                "calculated_at": datetime.now().isoformat(),
                "cached": False
            }
            
            # Cache result
            await self._cache_result(cache_key, response)
            
            return response
        
        except Exception as e:
            logger.error(f"Error calculating KPIs: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_trends(
        self,
        metric: str,
        start_date: str,
        end_date: str,
        granularity: str = "daily"
    ) -> Dict[str, Any]:
        """
        Analyze trends for a specific metric.
        
        Args:
            metric: Metric to analyze
            start_date: Start date
            end_date: End date
            granularity: Time granularity
        
        Returns:
            Trend analysis
        """
        try:
            # Check cache
            cache_key = self._generate_cache_key("trends", {
                "metric": metric,
                "start": start_date,
                "end": end_date,
                "granularity": granularity
            })
            
            cached = await self._get_cached_result(cache_key)
            if cached:
                return {**cached, "cached": True}
            
            # Analyze trends
            llm = await get_llm_with_retry()
            self.kpi_analyst.llm = llm
            
            task = Task(
                description=f"""Analyze trends for {metric} from {start_date} to {end_date}
                at {granularity} granularity.
                
                Provide:
                - Overall trend direction (increasing/decreasing/stable)
                - Rate of change
                - Notable spikes or drops
                - Seasonal patterns if detectable
                - Correlation with known events
                - Predicted continuation of trend
                
                Include visual description of the trend pattern.""",
                expected_output="Comprehensive trend analysis with patterns and predictions",
                agent=self.kpi_analyst
            )
            
            crew = Crew(
                agents=[self.kpi_analyst],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            response = {
                "success": True,
                "metric": metric,
                "start_date": start_date,
                "end_date": end_date,
                "granularity": granularity,
                "result": str(result),
                "analyzed_at": datetime.now().isoformat(),
                "cached": False
            }
            
            # Cache result
            await self._cache_result(cache_key, response)
            
            return response
        
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {
                "success": False,
                "metric": metric,
                "error": str(e)
            }
    
    async def forecast_performance(
        self,
        metric: str,
        forecast_days: int = 30,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Forecast future performance.
        
        Args:
            metric: Metric to forecast
            forecast_days: Days to forecast
            confidence_level: Confidence level
        
        Returns:
            Performance forecast
        """
        try:
            # Check cache
            cache_key = self._generate_cache_key("forecast", {
                "metric": metric,
                "days": forecast_days,
                "confidence": confidence_level
            })
            
            cached = await self._get_cached_result(cache_key)
            if cached:
                return {**cached, "cached": True}
            
            # Generate forecast
            llm = await get_llm_with_retry()
            self.report_generator.llm = llm
            
            task = Task(
                description=f"""Generate a {forecast_days}-day forecast for {metric}
                with {confidence_level*100}% confidence level.
                
                Based on historical data and trends:
                - Predict values for the next {forecast_days} days
                - Provide confidence intervals
                - Identify key factors affecting the forecast
                - Highlight potential risks or opportunities
                - Suggest proactive actions based on forecast
                
                Include both optimistic and pessimistic scenarios.""",
                expected_output="Detailed forecast with confidence intervals and scenarios",
                agent=self.report_generator
            )
            
            crew = Crew(
                agents=[self.report_generator],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = await crew.kickoff_async()
            
            response = {
                "success": True,
                "metric": metric,
                "forecast_days": forecast_days,
                "confidence_level": confidence_level,
                "result": str(result),
                "forecast_date": datetime.now().isoformat(),
                "cached": False
            }
            
            # Cache result
            await self._cache_result(cache_key, response)
            
            return response
        
        except Exception as e:
            logger.error(f"Error forecasting performance: {e}")
            return {
                "success": False,
                "metric": metric,
                "error": str(e)
            }
    
    async def clear_cache(self, pattern: str = "*"):
        """Clear analytics cache."""
        redis_client = await get_redis_client()
        await redis_client.clear_cache_pattern(pattern)
        logger.info(f"Cleared cache pattern: {pattern}")
