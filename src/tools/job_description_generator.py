"""
Job Description Generator Tool

This tool creates professional job descriptions based on hiring context,
adapting content for different roles, company stages, and requirements.
"""

from typing import Dict, List, Any
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import ConfigDict
import os
from dotenv import load_dotenv

load_dotenv()




class JobDescriptionGenerator:
    """Generates professional job descriptions using LLM with intelligent context"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            temperature=0.3,  # Slightly creative but consistent
            max_tokens=2000   # Enough for comprehensive job descriptions
        )
        
        self.job_description_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert HR professional and job description writer. 
            Create professional, compelling job descriptions that attract top talent while being realistic about requirements.
            
            Adapt your writing style and content based on:
            - Company stage (seed = entrepreneurial tone, series_a = growth-focused, growth = established/professional)
            - Role seniority (junior = learning focus, senior = leadership focus, lead = strategic focus)
            - Industry and location market conditions
            
            Use markdown formatting for structure and readability."""),
            
            ("human", """Create a professional job description based on this context:

ROLE DETAILS:
- Role Title: {role_title}
- Department: {department}  
- Seniority Level: {seniority_level}
- Company Stage: {company_stage}
- Location: {location}
- Remote Policy: {remote_policy}

COMPANY INFO:
- Industry: {industry}
- Company Size: {company_size}
- Company Description: {company_description}

TECHNICAL REQUIREMENTS:
- Tech Stack: {tech_stack}
- Salary Range: {salary_range}

CONTEXT FROM USER:
- Original Request: {original_request}
- User Responses: {user_responses}
- Urgency Level: {urgency}
- Has Budget Info: {has_budget}

Create a comprehensive job description with these sections:
1. # Role Title (with location)
2. ## Company Overview
3. ## Role Summary  
4. ## Key Responsibilities
5. ## Required Qualifications
6. ## Preferred Qualifications
7. ## Compensation & Benefits
8. ## Work Arrangement
9. ## How to Apply

Make it authentic to the {company_stage} stage - match the tone and expectations appropriately.""")
        ])
    
    def generate_job_description(self, hiring_context: Dict[str, Any]) -> str:
        """
        Generate a complete job description using LLM with full context
        
        Args:
            hiring_context: Complete hiring context from LangGraph state
            
        Returns:
            Complete job description as formatted string
        """
        # Prepare context for LLM prompt
        prompt_context = self._prepare_prompt_context(hiring_context)
        
        try:
            # Generate job description using LLM
            chain = self.job_description_prompt | self.llm
            response = chain.invoke(prompt_context)
            return response.content
            
        except Exception as e:
            return f"Error generating job description: {str(e)}"
    
    def _prepare_prompt_context(self, hiring_context: Dict[str, Any]) -> Dict[str, str]:
        """
        Prepare context dictionary for LLM prompt
        """
        return {
            "role_title": hiring_context.get("role_title", "Software Engineer"),
            "department": hiring_context.get("department", "Engineering"),
            "seniority_level": hiring_context.get("seniority_level", "mid"),
            "company_stage": hiring_context.get("company_stage", "seed"),
            "location": hiring_context.get("location", "San Francisco, CA"),
            "remote_policy": hiring_context.get("remote_policy", "hybrid"),
            "industry": hiring_context.get("industry") or "Technology",
            "company_size": hiring_context.get("company_size") or "startup",
            "company_description": hiring_context.get("company_description") or "Innovative technology company",
            "tech_stack": ", ".join(hiring_context.get("tech_stack", [])) if hiring_context.get("tech_stack") else "Modern tech stack",
            "salary_range": f"${hiring_context.get('salary_range')[0]:,} - ${hiring_context.get('salary_range')[1]:,}" if hiring_context.get('salary_range') else "Competitive salary",
            "original_request": hiring_context.get("original_request", ""),
            "user_responses": str(hiring_context.get("user_responses", {})),
            "urgency": hiring_context.get("urgency", "normal"),
            "has_budget": "Yes" if hiring_context.get("has_budget") else "No"
        }
    
class JobDescriptionGeneratorTool(BaseTool):
    """
    Tool for generating professional job descriptions using LLM with intelligent context
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "job_description_generator"
    description: str = "Generate comprehensive job descriptions from hiring requirements"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'generator', JobDescriptionGenerator())
    
    def _run(self, hiring_context: Dict[str, Any]) -> str:
        """Generate job description from hiring context"""
        return self.generator.generate_job_description(hiring_context)
        
    def _arun(self, hiring_context: Dict[str, Any]):
        """Async version"""
        raise NotImplementedError("Async not implemented yet")


