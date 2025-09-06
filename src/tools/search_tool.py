"""
Intelligent Search/Salary Benchmarking Tool

This tool provides comprehensive market data and salary benchmarking using LLM intelligence
instead of hard-coded data tables. It generates realistic salary insights based on current
market conditions, role requirements, and location-specific factors.
"""

from typing import Dict, Any
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import ConfigDict
import os
from dotenv import load_dotenv

load_dotenv()


class IntelligentMarketAnalyzer:
    """Provides salary benchmarking and market intelligence using LLM analysis"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            temperature=0.1,  # Very low temperature for consistent market data
            max_tokens=2000   # Enough for detailed salary analysis
        )
        
        self.salary_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a compensation expert and market research analyst with deep knowledge of tech industry salaries and hiring trends.
            
            Provide realistic, current salary benchmarking data based on:
            - Role requirements and seniority level
            - Geographic location and market competitiveness
            - Company stage and funding level
            - Current market conditions and demand
            
            Always provide salary ranges that reflect realistic 2024 market conditions.
            Include market percentiles, equity expectations, and hiring difficulty assessments.
            Be specific with numbers and provide actionable insights."""),
            
            ("human", """Provide comprehensive salary benchmarking and market analysis for this hiring context:

ROLE CONTEXT:
- Role Title: {role_title}
- Department: {department}
- Seniority Level: {seniority_level}
- Company Stage: {company_stage}
- Location: {location}
- Remote Policy: {remote_policy}

CONTEXT:
- Original Request: {original_request}
- User Responses: {user_responses}
- Tech Stack: {tech_stack}
- Industry: {industry}
- Urgency: {urgency}

Provide a detailed salary benchmarking report including:

## Salary Benchmarking Report
**Base Salary Range:** (25th-75th percentile for {location})
**Total Compensation:** (including equity estimates)
**Market Percentiles:**
- 25th percentile: $X
- 50th percentile (median): $X  
- 75th percentile: $X
- 90th percentile: $X

**Equity Expectations:**
- Typical equity range for {company_stage} stage
- Vesting schedule recommendations

## Market Intelligence Report  
**Market Conditions:** (competitive/moderate/favorable)
**Role Demand:** (very high/high/moderate/low)
**Talent Availability:** (scarce/limited/moderate/abundant)
**Average Time to Hire:** X weeks
**Hiring Difficulty:** (very difficult/difficult/moderate/easy)

**Competitive Factors:**
- Key factors that attract talent for this role
- What candidates prioritize beyond salary

**Trending Skills:**
- Most in-demand skills for this role
- Emerging technologies/skills to consider

**Market Outlook:**
- 6-12 month hiring forecast
- Salary trend predictions

**Recommendations:**
- Competitive positioning advice
- Hiring strategy recommendations

Base all numbers on realistic 2024 market data for {location} and {company_stage} companies.""")
        ])
    
    def generate_market_analysis(self, hiring_context: Dict[str, Any]) -> str:
        """Generate comprehensive salary benchmarking and market analysis using LLM"""
        prompt_context = {
            "role_title": hiring_context.get("role_title", "Software Engineer"),
            "department": hiring_context.get("department", "Engineering"),
            "seniority_level": hiring_context.get("seniority_level", "mid"),
            "company_stage": hiring_context.get("company_stage", "seed"),
            "location": hiring_context.get("location", "San Francisco, CA"),
            "remote_policy": hiring_context.get("remote_policy", "hybrid"),
            "original_request": hiring_context.get("original_request", "N/A"),
            "user_responses": str(hiring_context.get("user_responses", {})),
            "tech_stack": hiring_context.get("tech_stack", "Not specified"),
            "industry": hiring_context.get("industry", "Technology"),
            "urgency": hiring_context.get("urgency", "standard")
        }
        
        try:
            chain = self.salary_prompt | self.llm
            response = chain.invoke(prompt_context)
            return response.content
        except Exception as e:
            return f"Error generating market analysis: {str(e)}"


class SearchSalaryTool(BaseTool):
    """Tool to provide intelligent salary benchmarking and market analysis"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "search_salary_benchmark"
    description: str = "Provide comprehensive salary benchmarking and market intelligence using AI analysis"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'market_analyzer', IntelligentMarketAnalyzer())

    def _run(self, hiring_context: Dict[str, Any]) -> str:
        """Generate comprehensive salary and market analysis"""
        return self.market_analyzer.generate_market_analysis(hiring_context)

    def _arun(self, hiring_context: Dict[str, Any]):
        raise NotImplementedError("Async not implemented yet")
