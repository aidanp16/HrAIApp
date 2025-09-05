"""
HR Hiring Agent - Main agent implementation using LangGraph
Core agentic AI system that orchestrates the hiring assistance workflow
"""

from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END, START
import logging
import os
from datetime import datetime

# Import our intelligent questioning framework
from .intelligent_questioning import (
    IntelligentQuestioning, 
    CompanyStage, 
    RoleType, 
    QuestionPriority
)

# Import OpenAI for LLM calls
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HiringState(TypedDict):
    """
    LangGraph state object that tracks the entire hiring conversation
    This state persists across all nodes and contains all context
    """
    # User Input & Request
    original_request: str
    user_responses: Dict[str, str]
    
    # Context Analysis (from Intelligent Questioning)
    role_type: str                 # "engineering", "marketing", "sales", "executive"
    company_stage: str             # "seed", "series_a", "growth", "enterprise"  
    urgency_level: str             # "low", "medium", "high", "emergency"
    has_budget: bool
    has_timeline: bool
    specificity_score: float       # 0-1, how detailed the request is
    confidence_scores: Dict[str, float]  # Confidence in our analysis
    
    # Conversation Management
    current_step: str              # Current workflow step
    questions_asked: List[str]     # Questions we've presented
    questions_remaining: List[Dict] # Remaining questions to ask
    conversation_history: List[Dict] # Full conversation log
    needs_clarification: bool      # Whether we need more info
    
    # Generated Content
    job_description: Optional[str]
    hiring_checklist: Optional[List[Dict]]
    timeline_estimate: Optional[Dict]
    recommendations: List[str]
    
    # Workflow Control
    is_complete: bool
    error_message: Optional[str]
    session_id: Optional[str]
    timestamp: str

class HiringAgent:
    """
    Main HR Hiring Assistant Agent using LangGraph for multi-step reasoning
    
    ARCHITECTURE:
    - Uses LangGraph for stateful conversation management
    - Integrates Intelligent Questioning Framework for adaptive questions
    - Orchestrates multiple AI calls with context preservation
    - Provides structured hiring assistance workflow
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.questioning_system = IntelligentQuestioning()
        
        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            temperature=0.1,  # Low temperature for consistent, professional responses
            max_tokens=1000   # Reasonable limit for most responses
        )
        
        # Build the LangGraph workflow
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()
        
        self.logger.info("HiringAgent initialized with LangGraph workflow")
        
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow for hiring assistance
        
        WORKFLOW NODES:
        1. analyze_request - Extract context from initial request
        2. generate_questions - Create adaptive questions using our framework
        3. process_user_response - Handle user answers and update context
        4. generate_hiring_content - Create job description, checklist, timeline
        5. format_final_response - Structure the final output
        
        ROUTING LOGIC:
        - Smart routing based on context completeness
        - Can skip questions if request is already detailed enough
        - Iterative questioning until sufficient context gathered
        """
        
        # Create the state graph
        workflow = StateGraph(HiringState)
        
        # Add all nodes
        workflow.add_node("analyze_request", self._analyze_request_node)
        workflow.add_node("generate_questions", self._generate_questions_node)  
        workflow.add_node("process_user_response", self._process_response_node)
        workflow.add_node("generate_hiring_content", self._generate_content_node)
        workflow.add_node("format_final_response", self._format_response_node)
        
        # Set entry point
        workflow.add_edge(START, "analyze_request")
        
        # Add conditional routing logic
        workflow.add_conditional_edges(
            "analyze_request",
            self._route_after_analysis
        )
        
        workflow.add_conditional_edges(
            "generate_questions", 
            self._route_after_questions
        )
        
        workflow.add_edge("process_user_response", "generate_questions")
        workflow.add_edge("generate_hiring_content", "format_final_response")
        workflow.add_edge("format_final_response", END)
        
        return workflow
        
    # =============================================================================
    # LANGGRAPH NODE IMPLEMENTATIONS
    # =============================================================================
    
    def _analyze_request_node(self, state: HiringState) -> HiringState:
        """
        Node 1: Analyze the initial hiring request using our Intelligent Questioning system
        Extracts company stage, role type, urgency, and other context
        """
        self.logger.info(f"Analyzing request: {state['original_request'][:50]}...")
        
        try:
            # Use our intelligent questioning system to analyze context
            context = self.questioning_system.analyze_context(
                state['original_request'],
                state.get('conversation_history', [])
            )
            
            # Update state with analysis results
            state.update({
                'role_type': context['role_type'].value if hasattr(context['role_type'], 'value') else str(context['role_type']),
                'company_stage': context['company_stage'].value if hasattr(context['company_stage'], 'value') else str(context['company_stage']),
                'urgency_level': context['urgency_level'],
                'has_budget': context['has_budget'],
                'has_timeline': context['has_timeline'],
                'specificity_score': context['specificity_score'],
                'confidence_scores': context['confidence_scores'],
                'current_step': 'analysis_complete'
            })
            
            self.logger.info(f"Analysis complete - Role: {state['role_type']}, Stage: {state['company_stage']}")
            
        except Exception as e:
            self.logger.error(f"Error in analyze_request_node: {str(e)}")
            state['error_message'] = f"Failed to analyze request: {str(e)}"
            state['current_step'] = 'error'
            
        return state
    
    def _generate_questions_node(self, state: HiringState) -> HiringState:
        """
        Node 2: Generate adaptive questions using our Intelligent Questioning Framework
        Uses ML-inspired algorithms to prioritize most important questions
        """
        self.logger.info("Generating adaptive questions based on context")
        
        try:
            # Build context for questioning system
            context = {
                'role_type': RoleType(state['role_type']) if state['role_type'] != 'unknown' else RoleType.UNKNOWN,
                'company_stage': CompanyStage(state['company_stage']) if state['company_stage'] != 'unknown' else CompanyStage.UNKNOWN,
                'urgency_level': state['urgency_level'],
                'has_budget': state['has_budget'],
                'has_timeline': state['has_timeline'],
                'specificity_score': state['specificity_score'],
                'confidence_scores': state['confidence_scores']
            }
            
            # Generate prioritized questions using our intelligent system
            question_priorities = self.questioning_system.generate_adaptive_questions(context, max_questions=3)
            
            if question_priorities:
                # Store questions in state
                state['questions_remaining'] = [
                    {
                        'question': qp.question,
                        'priority_score': qp.priority_score,
                        'info_gain': qp.information_gain
                    }
                    for qp in question_priorities
                ]
                state['needs_clarification'] = True
                state['current_step'] = 'questions_generated'
                
                self.logger.info(f"Generated {len(question_priorities)} adaptive questions")
            else:
                # No questions needed - sufficient context
                state['needs_clarification'] = False
                state['current_step'] = 'ready_for_generation'
                
                self.logger.info("No additional questions needed - sufficient context available")
                
        except Exception as e:
            self.logger.error(f"Error in generate_questions_node: {str(e)}")
            state['error_message'] = f"Failed to generate questions: {str(e)}"
            state['current_step'] = 'error'
            
        return state
    
    def _process_response_node(self, state: HiringState) -> HiringState:
        """
        Node 3: Process user's responses and update context
        Uses pattern matching to extract structured info from natural language
        """
        self.logger.info("Processing user response and updating context")
        
        try:
            # Get the latest user response (assuming it's stored in user_responses)
            if not state.get('user_responses'):
                state['error_message'] = "No user response found to process"
                state['current_step'] = 'error'
                return state
            
            latest_response = list(state['user_responses'].values())[-1]
            questions_asked = state.get('questions_asked', [])
            
            # Build current context
            current_context = {
                'role_type': RoleType(state['role_type']) if state['role_type'] != 'unknown' else RoleType.UNKNOWN,
                'company_stage': CompanyStage(state['company_stage']) if state['company_stage'] != 'unknown' else CompanyStage.UNKNOWN,
                'urgency_level': state['urgency_level'],
                'has_budget': state['has_budget'],
                'has_timeline': state['has_timeline'],
                'specificity_score': state['specificity_score'],
                'confidence_scores': state['confidence_scores']
            }
            
            # Update context using our intelligent system
            updated_context = self.questioning_system.update_context_from_response(
                current_context,
                latest_response,
                questions_asked
            )
            
            # Update state with new context
            state.update({
                'role_type': updated_context['role_type'].value if hasattr(updated_context['role_type'], 'value') else str(updated_context['role_type']),
                'company_stage': updated_context['company_stage'].value if hasattr(updated_context['company_stage'], 'value') else str(updated_context['company_stage']),
                'urgency_level': updated_context['urgency_level'],
                'has_budget': updated_context['has_budget'],
                'has_timeline': updated_context['has_timeline'],
                'confidence_scores': updated_context.get('confidence_scores', state['confidence_scores']),
                'current_step': 'response_processed'
            })
            
            self.logger.info("User response processed and context updated")
            
        except Exception as e:
            self.logger.error(f"Error in process_response_node: {str(e)}")
            state['error_message'] = f"Failed to process response: {str(e)}"
            state['current_step'] = 'error'
            
        return state
    
    def _generate_content_node(self, state: HiringState) -> HiringState:
        """
        Node 4: Generate hiring content (job description, checklist, timeline)
        Uses all accumulated context for rich, personalized generation
        """
        self.logger.info("Generating hiring content with full context")
        
        try:
            # Build comprehensive context for content generation
            context_prompt = self._build_content_generation_context(state)
            
            # Generate job description
            job_description = self._generate_job_description(context_prompt, state)
            
            # Generate hiring checklist  
            hiring_checklist = self._generate_hiring_checklist(context_prompt, state)
            
            # Generate timeline estimate
            timeline_estimate = self._generate_timeline_estimate(context_prompt, state)
            
            # Update state with generated content
            state.update({
                'job_description': job_description,
                'hiring_checklist': hiring_checklist,
                'timeline_estimate': timeline_estimate,
                'current_step': 'content_generated',
                'is_complete': True
            })
            
            self.logger.info("All hiring content generated successfully")
            
        except Exception as e:
            self.logger.error(f"Error in generate_content_node: {str(e)}")
            state['error_message'] = f"Failed to generate content: {str(e)}"
            state['current_step'] = 'error'
            
        return state
    
    def _format_response_node(self, state: HiringState) -> HiringState:
        """
        Node 5: Format the final response with all generated content
        Creates structured output in markdown format
        """
        self.logger.info("Formatting final response")
        
        try:
            # This will be implemented when we add the actual formatting logic
            state['current_step'] = 'response_formatted'
            self.logger.info("Response formatted successfully")
            
        except Exception as e:
            self.logger.error(f"Error in format_response_node: {str(e)}")
            state['error_message'] = f"Failed to format response: {str(e)}"
            state['current_step'] = 'error'
            
        return state
    
    # =============================================================================
    # ROUTING LOGIC FUNCTIONS
    # =============================================================================
    
    def _route_after_analysis(self, state: HiringState) -> str:
        """
        Smart routing logic after request analysis
        Uses comprehensive context assessment to decide whether to ask questions
        """
        if state.get('error_message'):
            return END
            
        # Use intelligent assessment to determine if we need questions
        should_ask_questions = self._should_generate_questions(state)
        
        if should_ask_questions:
            self.logger.info("Insufficient context - generating questions")
            return "generate_questions"
        else:
            self.logger.info("Sufficient context available - skipping questions")
            return "generate_hiring_content"
    
    def _should_generate_questions(self, state: HiringState) -> bool:
        """
        Intelligent decision logic for whether to generate questions
        
        ALGORITHM:
        1. Check for critical missing information (deal-breakers)
        2. Assess information completeness by role type and urgency
        3. Consider company stage requirements
        4. Apply contextual thresholds based on scenario
        
        Returns True if questions should be generated
        """
        
        # Step 1: Critical missing information (always ask questions)
        if state['role_type'] == 'unknown':
            return True  # Must know role type
            
        if state['company_stage'] == 'unknown' and state['specificity_score'] < 0.5:
            return True  # Need stage for low-specificity requests
        
        # Step 2: Role-specific context requirements
        role_needs_questions = self._assess_role_specific_needs(state)
        if role_needs_questions:
            return True
        
        # Step 3: Urgency-based assessment
        if state['urgency_level'] == 'high' and not (state['has_budget'] and state['has_timeline']):
            return True  # Urgent requests need budget/timeline clarity
        
        # Step 4: Company stage-specific requirements
        stage_needs_questions = self._assess_stage_specific_needs(state)
        if stage_needs_questions:
            return True
        
        # Step 5: Completeness threshold based on specificity and context
        completeness_score = self._calculate_context_completeness(state)
        
        # Dynamic threshold based on role complexity
        if state['role_type'] in ['executive', 'operations']:
            threshold = 0.8  # Executive roles need more context
        elif state['urgency_level'] == 'high':
            threshold = 0.7  # Urgent requests need clarity
        else:
            threshold = 0.75  # Standard threshold
        
        return completeness_score < threshold
    
    def _assess_role_specific_needs(self, state: HiringState) -> bool:
        """Check if role type has specific context requirements"""
        role_type = state['role_type']
        
        if role_type == 'executive':
            # Executive roles need leadership context
            return not (state['has_timeline'] or state['specificity_score'] > 0.8)
        
        if role_type == 'operations':
            # Operations roles need process context
            return state['specificity_score'] < 0.8
        
        if role_type in ['marketing', 'sales'] and not state['has_budget']:
            # Marketing/sales roles need budget context for realistic expectations
            if state['company_stage'] in ['seed', 'series_a', 'growth']:
                # All scaling companies need budget clarity for competitive hiring
                return True
            else:
                # Unknown/enterprise stage - use specificity threshold
                return state['specificity_score'] < 0.9
        
        return False
    
    def _assess_stage_specific_needs(self, state: HiringState) -> bool:
        """Check if company stage has specific context requirements"""
        stage = state['company_stage']
        
        if stage == 'seed' and not state['has_budget']:
            # Seed companies need budget reality check
            return True
        
        if stage in ['series_a', 'growth'] and state['role_type'] == 'executive' and not state['has_timeline']:
            # Scaling companies need exec hire timeline clarity
            return True
        
        return False
    
    def _calculate_context_completeness(self, state: HiringState) -> float:
        """Calculate overall context completeness score (0-1)"""
        completeness = 0.0
        total_factors = 0
        
        # Basic information completeness (40% weight)
        if state['role_type'] != 'unknown':
            completeness += 0.2
        if state['company_stage'] != 'unknown':
            completeness += 0.2
        total_factors += 0.4
        
        # Specificity score (30% weight)
        completeness += state['specificity_score'] * 0.3
        total_factors += 0.3
        
        # Critical details (30% weight)
        if state['has_budget']:
            completeness += 0.1
        if state['has_timeline']:
            completeness += 0.1
        
        # Confidence bonus (high confidence = more complete)
        avg_confidence = sum(state.get('confidence_scores', {}).values()) / max(len(state.get('confidence_scores', {})), 1)
        completeness += avg_confidence * 0.1
        
        total_factors += 0.3
        
        return min(completeness, 1.0)
    
    def _route_after_questions(self, state: HiringState) -> str:
        """
        Routing logic after question generation
        Decides whether to present questions or proceed to content generation
        """
        if state.get('error_message'):
            return END
            
        if state.get('needs_clarification', False):
            # We need to present questions and wait for user response
            # In a real implementation, this would pause for user input
            return "generate_hiring_content"  # For now, skip to content generation
        else:
            return "generate_hiring_content"
    
    # =============================================================================
    # HELPER METHODS FOR CONTENT GENERATION
    # =============================================================================
    
    def _build_content_generation_context(self, state: HiringState) -> str:
        """
        Build comprehensive context string for content generation
        """
        context = f"""
        HIRING REQUEST CONTEXT:
        Original Request: {state['original_request']}
        Role Type: {state['role_type']}
        Company Stage: {state['company_stage']}
        Urgency Level: {state['urgency_level']}
        Has Budget Info: {state['has_budget']}
        Has Timeline Info: {state['has_timeline']}
        
        USER RESPONSES:
        {state.get('user_responses', {})}
        
        CONTEXT ANALYSIS:
        Specificity Score: {state['specificity_score']}
        Confidence Scores: {state['confidence_scores']}
        """
        return context
    
    def _generate_job_description(self, context: str, state: HiringState) -> str:
        """
        Generate job description using LLM with full context
        """
        prompt = f"""
        {context}
        
        Based on this context, create a professional job description that includes:
        - Clear role title and overview
        - Key responsibilities (3-5 main areas)
        - Required qualifications vs. nice-to-have
        - Company stage-appropriate tone and expectations
        
        Make it compelling and realistic for a {state['company_stage']} stage company.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating job description: {str(e)}"
    
    def _generate_hiring_checklist(self, context: str, state: HiringState) -> List[Dict]:
        """
        Generate hiring checklist using LLM with full context
        """
        # For now, return a placeholder - will implement full generation later
        return [{"step": "Job posting creation", "timeline": "Week 1", "status": "pending"}]
    
    def _generate_timeline_estimate(self, context: str, state: HiringState) -> Dict:
        """
        Generate timeline estimate using LLM with full context
        """
        # For now, return a placeholder - will implement full generation later
        return {"total_weeks": 6, "phases": ["Posting", "Screening", "Interviews", "Decision"]}
    
    # =============================================================================
    # PUBLIC INTERFACE METHODS
    # =============================================================================
    
    def process_hiring_request(self, request: str, session_id: str = None) -> Dict[str, Any]:
        """
        Main entry point: Process a hiring request through the LangGraph workflow
        
        Args:
            request: The initial hiring request from user
            session_id: Optional session ID for state persistence
            
        Returns:
            Dict containing the workflow results and generated content
        """
        self.logger.info(f"Processing hiring request: {request[:100]}...")
        
        # Initialize state
        initial_state = HiringState(
            original_request=request,
            user_responses={},
            role_type='unknown',
            company_stage='unknown',
            urgency_level='medium',
            has_budget=False,
            has_timeline=False,
            specificity_score=0.0,
            confidence_scores={},
            current_step='initialized',
            questions_asked=[],
            questions_remaining=[],
            conversation_history=[],
            needs_clarification=False,
            job_description=None,
            hiring_checklist=None,
            timeline_estimate=None,
            recommendations=[],
            is_complete=False,
            error_message=None,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
        try:
            # Run the LangGraph workflow
            final_state = self.compiled_graph.invoke(initial_state)
            
            self.logger.info(f"Workflow completed - Status: {final_state['current_step']}")
            
            return {
                'success': True,
                'state': final_state,
                'job_description': final_state.get('job_description'),
                'hiring_checklist': final_state.get('hiring_checklist'),
                'timeline_estimate': final_state.get('timeline_estimate'),
                'questions_asked': final_state.get('questions_asked', []),
                'error_message': final_state.get('error_message')
            }
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'state': initial_state
            }
    
    def get_questions(self, context: Dict[str, Any]) -> List[str]:
        """
        Get prioritized questions for current context (useful for interactive mode)
        """
        question_priorities = self.questioning_system.generate_adaptive_questions(context)
        return [qp.question for qp in question_priorities]
    
    def format_questions_for_user(self, questions: List[str]) -> str:
        """
        Format questions in user-friendly way
        """
        if not questions:
            return "I have all the information I need!"
            
        if len(questions) == 1:
            return f"To create the best hiring plan, I need to know: {questions[0]}"
            
        formatted = "To create the best hiring plan for you, I have a few quick questions:\n\n"
        for i, q in enumerate(questions, 1):
            formatted += f"{i}. {q}\n"
            
        return formatted
