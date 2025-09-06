"""
Intelligent Hiring Timeline Calculator

This tool generates realistic hiring timeline estimates using LLM intelligence
instead of hardcoded calculations. It provides detailed week-by-week plans,
risk assessments, and optimization recommendations based on current market conditions.
"""

from typing import Dict, Any
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import ConfigDict
import os
from dotenv import load_dotenv

load_dotenv()


class IntelligentTimelineAnalyzer:
    """Generates hiring timelines using LLM intelligence"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            temperature=0.2,  # Low temperature for consistent timeline planning
            max_tokens=2500   # Enough for detailed week-by-week plans
        )
        
        self.timeline_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert HR consultant and project manager specializing in hiring timelines and process optimization.
            
            Create realistic, detailed hiring timelines based on:
            - Role complexity and seniority level
            - Company stage and resources
            - Market conditions and competition
            - Urgency requirements
            - Industry-specific hiring practices
            
            Provide practical week-by-week plans with specific activities, deliverables, owners, and risk mitigation.
            Consider current 2024 hiring market conditions and best practices."""),
            
            ("human", """Generate a comprehensive hiring timeline and project plan for this context:

ROLE CONTEXT:
- Role Title: {role_title}
- Department: {department}
- Seniority Level: {seniority_level}
- Company Stage: {company_stage}
- Location: {location}
- Remote Policy: {remote_policy}

HIRING CONTEXT:
- Original Request: {original_request}
- User Responses: {user_responses}
- Tech Stack: {tech_stack}
- Industry: {industry}
- Urgency Level: {urgency}
- Has Budget: {has_budget}
- Has Timeline: {has_timeline}

Create a detailed hiring timeline plan including:

# Hiring Timeline: {role_title}

## Executive Summary
**Total Duration:** X weeks (X days)
**Start Date:** [Current date + 1 week]
**Target Completion:** [Calculated end date]
**Confidence Level:** [High/Medium/Low with reasoning]

## Week-by-Week Breakdown

### Week 1: [Phase Name]
**Activities:**
- Specific activity 1
- Specific activity 2
- Specific activity 3

**Deliverables:**
- Concrete deliverable 1
- Concrete deliverable 2

**Owners:** [HR, Hiring Manager, Recruiter, etc.]
**Dependencies:** [Any dependencies]
**Risks:** [Potential risks for this week]
**Success Criteria:** [How to measure success]

### Week 2: [Phase Name]
[Continue pattern for each week...]

## Critical Path Analysis
**Timeline-Critical Activities:**
- Most important activities that could delay the hire
- Dependencies that create bottlenecks
- Resource constraints to monitor

## Risk Assessment
**High-Risk Factors:**
- Specific risks based on role, market, company stage
- Market competition impacts
- Resource availability concerns

**Risk Mitigation:**
- Specific strategies to address each risk
- Contingency plans and alternatives

## Timeline Optimization Tips
**Speed Improvements:**
- Specific actions to accelerate the process
- Parallel activities that can be done simultaneously
- Bottleneck elimination strategies

**Quality Improvements:**
- Ways to improve candidate experience
- Better assessment techniques
- Stakeholder alignment strategies

## Contingency Plans
**If Timeline Extends:**
- Alternative approaches if delays occur
- Resource reallocation options
- Communication strategies with stakeholders

**If Urgent Acceleration Needed:**
- Fast-track options while maintaining quality
- Resource mobilization strategies

Ensure the timeline is realistic for a {company_stage} stage company hiring a {seniority_level} {role_title} in {location} with {urgency} urgency.""")
        ])
    
    def generate_hiring_timeline(self, hiring_context: Dict[str, Any]) -> str:
        """Generate comprehensive hiring timeline using LLM"""
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
            "urgency": hiring_context.get("urgency", "normal"),
            "has_budget": "Yes" if hiring_context.get("has_budget") else "No",
            "has_timeline": "Yes" if hiring_context.get("has_timeline") else "No"
        }
        
        try:
            chain = self.timeline_prompt | self.llm
            response = chain.invoke(prompt_context)
            return response.content
        except Exception as e:
            return f"Error generating hiring timeline: {str(e)}"


class TimelineCalculatorTool(BaseTool):
    """Tool to generate intelligent hiring timelines and project plans"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "timeline_calculator"
    description: str = "Generate realistic hiring timelines with detailed week-by-week plans using AI analysis"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'timeline_analyzer', IntelligentTimelineAnalyzer())

    def _run(self, hiring_context: Dict[str, Any]) -> str:
        """Generate comprehensive hiring timeline and project plan"""
        return self.timeline_analyzer.generate_hiring_timeline(hiring_context)

    def _arun(self, hiring_context: Dict[str, Any]):
        raise NotImplementedError("Async not implemented yet")
