"""
Hiring Checklist Builder Tool

This tool creates comprehensive, step-by-step hiring processes using LLM intelligence
instead of hard-coded templates. It generates adaptive workflows based on company stage,
role complexity, urgency, and market conditions.
"""

from typing import Dict, Any, List
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import ConfigDict
import os
from dotenv import load_dotenv

load_dotenv()


class IntelligentHiringChecklistBuilder:
    """Builds comprehensive hiring checklists using LLM intelligence"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            temperature=0.2,  # Low temperature for consistent, structured processes
            max_tokens=2500   # Enough for comprehensive checklists
        )
        
        self.checklist_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert HR consultant specializing in hiring processes and workflow optimization.
            Create detailed, actionable hiring checklists that are tailored to company stage and role complexity.
            
            Adapt your processes based on:
            - Company stage (seed = fast/lean process, series_a = structured process, growth = comprehensive process)
            - Role complexity (junior = simpler evaluation, senior = thorough assessment, executive = extensive vetting)
            - Urgency level (urgent = compressed timeline, normal = standard timeline, low = thorough timeline)
            
            Format as structured markdown with clear phases, activities, owners, and timelines.
            Include practical tips and risk mitigation strategies."""),
            
            ("human", """Create a comprehensive hiring checklist based on this context:

HIRING CONTEXT:
- Role Title: {role_title}
- Company Stage: {company_stage}
- Department: {department}
- Seniority Level: {seniority_level}
- Urgency: {urgency}
- Location: {location}
- Remote Policy: {remote_policy}

ORIGINAL REQUEST:
{original_request}

USER CONTEXT:
{user_responses}

Generate a detailed hiring process checklist with:

1. **Process Overview** (philosophy, timeline estimate)
2. **Phase 1: Preparation** (requirements definition, job posting, interview prep)
3. **Phase 2: Sourcing & Outreach** (posting strategy, candidate pipeline)
4. **Phase 3: Screening** (resume review, initial screening)
5. **Phase 4: Interviews** (rounds appropriate for {company_stage} stage)
6. **Phase 5: Evaluation & Decision** (debrief, reference checks, decision making)
7. **Phase 6: Offer & Closing** (offer preparation, negotiation, onboarding prep)
8. **Success Metrics** (what defines a successful hire)
9. **Risk Mitigation** (potential issues and solutions)

For each phase, include:
- Specific activities with owners and time estimates
- Best practice tips
- Dependencies and potential roadblocks

Tailor the complexity and rigor to the {company_stage} stage - seed companies need lean processes, growth companies need thorough evaluation.""")
        ])
    
    def build_hiring_checklist(self, hiring_context: Dict[str, Any]) -> str:
        """
        Build a comprehensive hiring checklist using LLM intelligence
        
        Args:
            hiring_context: Complete hiring context from LangGraph state
            
        Returns:
            Formatted hiring checklist as string
        """
        # Prepare context for LLM prompt
        prompt_context = self._prepare_prompt_context(hiring_context)
        
        try:
            # Generate hiring checklist using LLM
            chain = self.checklist_prompt | self.llm
            response = chain.invoke(prompt_context)
            return response.content
            
        except Exception as e:
            return f"Error generating hiring checklist: {str(e)}"
    
    def _prepare_prompt_context(self, hiring_context: Dict[str, Any]) -> Dict[str, str]:
        """
        Prepare context dictionary for LLM prompt
        """
        return {
            "role_title": hiring_context.get("role_title", "Software Engineer"),
            "company_stage": hiring_context.get("company_stage", "seed"),
            "department": hiring_context.get("department", "Engineering"),
            "seniority_level": hiring_context.get("seniority_level", "mid"),
            "urgency": hiring_context.get("urgency", "normal"),
            "location": hiring_context.get("location", "San Francisco, CA"),
            "remote_policy": hiring_context.get("remote_policy", "hybrid"),
            "original_request": hiring_context.get("original_request", ""),
            "user_responses": str(hiring_context.get("user_responses", {}))
        }


class ChecklistBuilderTool(BaseTool):
    """
    Tool for generating hiring checklists using LLM intelligence
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = "checklist_builder"
    description: str = "Generate comprehensive hiring checklists and timelines"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'builder', IntelligentHiringChecklistBuilder())
    
    def _run(self, hiring_context: Dict[str, Any]) -> str:
        """Generate hiring checklist from context"""
        return self.builder.build_hiring_checklist(hiring_context)
        
    def _arun(self, hiring_context: Dict[str, Any]):
        """Async version"""
        raise NotImplementedError("Async not implemented yet")
