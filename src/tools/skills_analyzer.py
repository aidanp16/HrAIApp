"""
Intelligent Skills Gap Analysis Tool

This tool analyzes candidate skills against job requirements using LLM intelligence.
It provides comprehensive skills assessment, gap identification, and development
recommendations tailored to role requirements and candidate background.
"""

from typing import Dict, Any
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import ConfigDict
import os
from dotenv import load_dotenv

load_dotenv()


class IntelligentSkillsAnalyzer:
    """Analyzes skills gaps and provides candidate evaluation using LLM intelligence"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            temperature=0.2,  # Low temperature for consistent analysis
            max_tokens=2000   # Sufficient for detailed skills analysis
        )
        
        self.skills_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert talent assessment specialist and skills analyst with deep knowledge of role requirements across different industries and seniority levels.
            
            Provide comprehensive skills gap analysis that includes:
            - Technical skills assessment against role requirements
            - Soft skills and competency evaluation
            - Experience level and depth analysis
            - Skill development recommendations and learning paths
            - Hiring recommendation with risk assessment
            
            Consider industry standards, role complexity, and company stage when evaluating candidates.
            Be objective and specific in your assessments."""),
            
            ("human", """Analyze this candidate against the job requirements and provide a comprehensive skills assessment:

JOB REQUIREMENTS:
- Role Title: {role_title}
- Department: {department}
- Seniority Level: {seniority_level}
- Company Stage: {company_stage}
- Required Tech Stack: {tech_stack}
- Location: {location}
- Industry: {industry}

ROLE CONTEXT:
- Original Job Request: {original_request}
- Specific Requirements: {user_responses}

CANDIDATE PROFILE:
{candidate_profile}

Provide a detailed skills gap analysis including:

# Skills Gap Analysis: {role_title}

## Executive Summary
**Overall Match:** [Excellent/Good/Adequate/Poor] - X% match
**Hiring Recommendation:** [Strong Hire/Hire/Maybe/No Hire]
**Key Strengths:** [Top 3 strengths]
**Major Concerns:** [Top 3 concerns]

## Technical Skills Assessment

### Core Technical Requirements
**Required Skills Analysis:**
- Skill 1: [Assessment: Exceeds/Meets/Below/Missing] - [Specific details]
- Skill 2: [Assessment: Exceeds/Meets/Below/Missing] - [Specific details]
- Skill 3: [Assessment: Exceeds/Meets/Below/Missing] - [Specific details]

**Technical Depth Analysis:**
- Years of experience vs. role requirements
- Complexity of projects handled
- Technical leadership and mentoring experience (if applicable)

**Technology Stack Alignment:**
- Direct experience with required technologies
- Related/transferable technology experience
- Learning curve assessment for missing technologies

## Experience & Seniority Assessment

### Role-Appropriate Experience
**Experience Level Match:**
- Years of experience: [Candidate] vs [Required]
- Industry experience relevance
- Company stage experience alignment

**Responsibility Scope:**
- Project scale and complexity handled
- Team size and leadership experience
- Strategic vs. tactical experience level

**Career Progression:**
- Growth trajectory assessment
- Role advancement pattern
- Future potential evaluation

## Soft Skills & Competencies

### Critical Competencies for {seniority_level} {role_title}
**Communication & Collaboration:**
- [Assessment with specific examples]

**Problem-Solving & Critical Thinking:**
- [Assessment with specific examples]

**Leadership & Influence:** (if applicable)
- [Assessment with specific examples]

**Adaptability & Learning:**
- [Assessment with specific examples]

## Skills Gap Analysis

### Critical Gaps
**High-Priority Missing Skills:**
1. [Skill] - Impact: [High/Medium/Low] - Time to develop: [Timeline]
2. [Skill] - Impact: [High/Medium/Low] - Time to develop: [Timeline]

### Development Recommendations
**Immediate Development Needs:**
- [Specific skill development recommendations]
- [Suggested learning resources and timeline]

**Medium-term Growth Areas:**
- [Skills for role advancement]
- [Professional development suggestions]

## Company Fit Assessment

### {company_stage} Stage Alignment
**Stage-Specific Requirements:**
- Startup adaptability and ambiguity tolerance
- Scale-up process and structure experience
- Growth stage specialization and expertise

**Cultural and Work Style Fit:**
- Remote/hybrid work experience
- Cross-functional collaboration style
- Innovation vs. process orientation

## Risk Assessment

### Hiring Risks
**High-Risk Factors:**
- [Specific risks with mitigation strategies]

**Medium-Risk Factors:**
- [Areas of concern with monitoring recommendations]

### Success Factors
**What Would Make This Hire Successful:**
- [Specific success enablers]
- [Support and development needed]

## Final Recommendation

### Hiring Decision Framework
**Strong Hire Criteria Met:** [Yes/No] - [Explanation]
**Minimum Requirements Met:** [Yes/No] - [Explanation]
**Growth Potential:** [High/Medium/Low] - [Reasoning]

**Decision Recommendation:**
[Detailed recommendation with reasoning, including any conditions or development plans needed]

**Alternative Considerations:**
- Other suitable roles in organization
- Timeline for skill development if hired
- Compensation considerations based on gap analysis

Provide specific, actionable insights based on the candidate profile and {seniority_level} {role_title} requirements.""")
        ])
    
    def analyze_candidate_skills(self, candidate_profile: str, job_context: Dict[str, Any]) -> str:
        """Analyze candidate skills against job requirements using LLM"""
        prompt_context = {
            "role_title": job_context.get("role_title", "Software Engineer"),
            "department": job_context.get("department", "Engineering"),
            "seniority_level": job_context.get("seniority_level", "mid"),
            "company_stage": job_context.get("company_stage", "seed"),
            "tech_stack": job_context.get("tech_stack", "Not specified"),
            "location": job_context.get("location", "San Francisco, CA"),
            "industry": job_context.get("industry", "Technology"),
            "original_request": job_context.get("original_request", "N/A"),
            "user_responses": str(job_context.get("user_responses", {})),
            "candidate_profile": candidate_profile
        }
        
        try:
            chain = self.skills_prompt | self.llm
            response = chain.invoke(prompt_context)
            return response.content
        except Exception as e:
            return f"Error analyzing candidate skills: {str(e)}"


class SkillsAnalyzerTool(BaseTool):
    """Tool for intelligent candidate skills analysis and gap assessment"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "skills_analyzer"
    description: str = "Analyze candidate skills against job requirements and identify gaps using AI assessment"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'skills_analyzer', IntelligentSkillsAnalyzer())

    def _run(self, candidate_profile: str, job_context: Dict[str, Any]) -> str:
        """Analyze candidate skills against job requirements"""
        return self.skills_analyzer.analyze_candidate_skills(candidate_profile, job_context)

    def _arun(self, candidate_profile: str, job_context: Dict[str, Any]):
        raise NotImplementedError("Async not implemented yet")
