"""
Intelligent Interview Question Generator

This tool generates comprehensive, role-specific interview questions using LLM intelligence
instead of hardcoded question banks. It creates structured interview guides with behavioral,
technical, and situational questions tailored to the specific role and company context.
"""

from typing import Dict, Any
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import ConfigDict
import os
from dotenv import load_dotenv

load_dotenv()


class IntelligentInterviewGenerator:
    """Generates interview questions and guides using LLM intelligence"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            temperature=0.3,  # Moderate creativity for diverse questions
            max_tokens=2500   # Enough for comprehensive interview guides
        )
        
        self.interview_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert HR consultant and interview specialist with deep knowledge of effective interviewing techniques.
            
            Create comprehensive interview guides that include:
            - Role-specific behavioral questions using STAR method
            - Technical questions appropriate to seniority level
            - Situational questions that reveal problem-solving approach
            - Cultural fit questions aligned with company stage
            - Leadership questions for senior roles
            
            Adapt question complexity and focus based on:
            - Seniority level (junior = fundamentals, senior = leadership, executive = strategic)
            - Company stage (seed = adaptability, series_a = scale, growth = process)
            - Role specifics and required skills
            
            For each question, provide follow-ups, evaluation criteria, and red flags to watch for."""),
            
            ("human", """Create a comprehensive interview guide for this hiring context:

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
- Urgency: {urgency}

Generate a complete interview guide including:

# Interview Guide: {role_title}

## Interview Overview
**Duration:** X minutes
**Interview Format:** [In-person/Video/Phone]
**Number of Interviewers:** X
**Interview Structure:** [Panel/Sequential/etc.]

## Pre-Interview Preparation
**Interviewer Preparation:**
- Key resume points to discuss
- Specific skills to assess
- Questions about background to explore

**Materials Needed:**
- Technical assessment materials (if applicable)
- Salary range and role expectations
- Company overview materials

## Interview Structure & Questions

### Opening (5-10 minutes)
**Introduction Script:**
- Welcome and introductions
- Interview format explanation
- Role overview and company context

### Section 1: Background & Experience (15-20 minutes)
**Behavioral Questions:**
1. [Question with follow-ups and evaluation criteria]
2. [Question with follow-ups and evaluation criteria]
3. [Question with follow-ups and evaluation criteria]

### Section 2: Technical Assessment (20-25 minutes)
**Technical Questions:** (appropriate for {seniority_level} level)
1. [Technical question with evaluation criteria]
2. [Technical question with evaluation criteria]
3. [Practical/problem-solving scenario]

### Section 3: Role-Specific Scenarios (15-20 minutes)
**Situational Questions:**
1. [Scenario relevant to daily role responsibilities]
2. [Challenge scenario specific to {company_stage} stage company]
3. [Cross-functional collaboration scenario]

### Section 4: Leadership & Cultural Fit (10-15 minutes)
**Cultural & Leadership Questions:**
1. [Cultural fit question for {company_stage} stage]
2. [Leadership question appropriate to {seniority_level} level]
3. [Values alignment question]

### Closing (5-10 minutes)
**Candidate Questions:**
- Time for candidate to ask questions
- Next steps explanation
- Timeline expectations

## Evaluation Framework

### Key Assessment Areas:
**Technical Competency:**
- Core skills evaluation criteria
- Problem-solving approach assessment
- Technical depth appropriate to level

**Behavioral Competencies:**
- Communication and collaboration
- Learning agility and adaptability
- Initiative and ownership

**Cultural Alignment:**
- Fit with company values and stage
- Work style compatibility
- Long-term potential assessment

### Scoring Guidelines:
- **Excellent (4):** Exceeds expectations, clear hire
- **Good (3):** Meets expectations, likely hire
- **Adequate (2):** Meets minimum requirements, maybe hire
- **Poor (1):** Below expectations, no hire

### Red Flags to Watch For:
- Communication issues or unclear explanations
- Lack of specific examples or vague responses
- Inconsistencies with resume or previous answers
- Cultural misalignment indicators
- Technical knowledge gaps for level

## Post-Interview Process
**Immediate Actions:**
- Complete evaluation scorecard
- Document key strengths and concerns  
- Share feedback with hiring team
- Schedule follow-up if needed

**Decision Criteria:**
- Minimum scores required for advancement
- Must-have vs. nice-to-have qualifications
- Team consensus requirements

Make the questions specific to {role_title} at a {company_stage} stage company, appropriate for {seniority_level} level.""")
        ])
    
    def generate_interview_guide(self, hiring_context: Dict[str, Any]) -> str:
        """Generate comprehensive interview guide using LLM"""
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
            "urgency": hiring_context.get("urgency", "normal")
        }
        
        try:
            chain = self.interview_prompt | self.llm
            response = chain.invoke(prompt_context)
            return response.content
        except Exception as e:
            return f"Error generating interview guide: {str(e)}"


class InterviewGeneratorTool(BaseTool):
    """Tool to generate comprehensive interview guides and questions"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "interview_generator"
    description: str = "Generate role-specific interview questions and comprehensive interview guides using AI"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'interview_generator', IntelligentInterviewGenerator())

    def _run(self, hiring_context: Dict[str, Any]) -> str:
        """Generate comprehensive interview guide from hiring context"""
        return self.interview_generator.generate_interview_guide(hiring_context)

    def _arun(self, hiring_context: Dict[str, Any]):
        raise NotImplementedError("Async not implemented yet")
