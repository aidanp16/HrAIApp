"""
Mock OpenAI Client for Development
Used when API quota is exceeded or for testing without using credits
"""

import random
from typing import Dict, Any, List

class MockOpenAIResponse:
    """Mock response object that mimics OpenAI API response structure"""
    
    def __init__(self, content: str):
        self.content = content
        
    def __str__(self):
        return self.content

class MockChatCompletion:
    """Mock chat completion response"""
    
    def __init__(self, content: str):
        self.message = MockOpenAIResponse(content)
        
class MockCompletionResponse:
    """Mock completion response"""
    
    def __init__(self, content: str):
        self.choices = [MockChatCompletion(content)]

class MockOpenAIClient:
    """
    Mock OpenAI client for development
    Returns realistic HR-focused responses without using API credits
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        
    @property
    def chat(self):
        return self
        
    @property
    def completions(self):
        return self
        
    def create(self, model: str, messages: List[Dict], **kwargs) -> MockCompletionResponse:
        """Mock chat completion that generates HR-appropriate responses"""
        
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "").lower()
                break
        
        # Generate contextual responses based on user input
        if "hire" in user_message or "hiring" in user_message:
            responses = [
                "I'd be happy to help you with your hiring process! To get started, I need to understand a few key details about the role you're looking to fill. Could you tell me:\n\n1. What specific position are you hiring for?\n2. What's your target timeline for filling this role?\n3. What's your budget range for this position?",
                
                "Great! Let's create a comprehensive hiring plan. Based on your needs, I'll help you generate job descriptions, interview questions, and a step-by-step hiring timeline. What type of role are you focusing on - technical, marketing, sales, or executive?",
                
                "I can help you streamline your hiring process. For a startup hiring process, we typically need to consider company stage, role complexity, and market conditions. What stage is your company at - seed, Series A, growth, or enterprise level?"
            ]
        elif "question" in user_message:
            responses = [
                "Here are some key clarifying questions for your hiring process:\n\n1. What's the seniority level for this role?\n2. Are there any specific technical skills required?\n3. What's your preferred candidate experience range?\n4. Do you have any location preferences or is this remote-friendly?",
                
                "Based on the role type, here are the most important questions to ask:\n\n• What's driving the need for this hire right now?\n• What would success look like in the first 90 days?\n• What's your ideal candidate background?\n• Any deal-breaker requirements?"
            ]
        elif "job description" in user_message:
            responses = [
                "I'll help you create a compelling job description. A great job description should include:\n\n• Clear role title and level\n• Key responsibilities and impact\n• Required vs. preferred qualifications\n• Company culture and benefits\n• Growth opportunities\n\nWhat specific role are we writing this for?",
                
                "Let's craft a job description that attracts top talent. I'll structure it with sections for role overview, key responsibilities, qualifications, and what makes your company unique. What position should we focus on?"
            ]
        elif "timeline" in user_message or "checklist" in user_message:
            responses = [
                "Here's a typical hiring timeline for most roles:\n\n• Week 1: Job posting and initial sourcing\n• Week 2-3: Resume screening and initial calls\n• Week 3-4: Technical/behavioral interviews\n• Week 4-5: Final interviews and reference checks\n• Week 5-6: Offer negotiation and acceptance\n\nThis can be adjusted based on role complexity and urgency.",
                
                "I'll create a comprehensive hiring checklist:\n\n✓ Define role requirements\n✓ Create job posting\n✓ Set up interview process\n✓ Screen candidates\n✓ Conduct interviews\n✓ Check references\n✓ Make offer\n✓ Complete onboarding prep\n\nWould you like me to customize this for your specific role?"
            ]
        elif "test" in user_message:
            responses = ["API connection test successful! Mock client is working perfectly for development."]
        else:
            responses = [
                "I'm your AI-powered HR hiring assistant! I can help you with:\n\n• Generating clarifying questions for hiring needs\n• Creating detailed job descriptions\n• Building step-by-step hiring checklists\n• Calculating realistic timelines\n• Providing market insights\n\nWhat aspect of hiring would you like to work on today?",
                
                "Hello! I'm here to help streamline your startup hiring process. I can assist with job descriptions, interview questions, hiring timelines, and more. What hiring challenge can I help you solve?"
            ]
        
        # Return a random appropriate response
        selected_response = random.choice(responses)
        return MockCompletionResponse(selected_response)

class MockLangChainLLM:
    """Mock LangChain LLM for testing"""
    
    def __init__(self, model: str, temperature: float = 0.1):
        self.model = model
        self.temperature = temperature
        
    def invoke(self, message: str) -> MockOpenAIResponse:
        """Mock invoke method"""
        response = "HR Hiring Assistant integration test successful! Ready for LangGraph implementation."
        return MockOpenAIResponse(response)

def get_client() -> MockOpenAIClient:
    """Get mock client for development"""
    return MockOpenAIClient()

def get_langchain_llm(model: str = "gpt-4o-mini", temperature: float = 0.1) -> MockLangChainLLM:
    """Get mock LangChain LLM for development"""
    return MockLangChainLLM(model, temperature)
