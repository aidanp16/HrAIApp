# HR Hiring Agent - LangGraph Workflow Design

## 🔄 **Core Conversation Flow**

```
START → Request Analysis → Question Generation → User Response → Context Building → Output Generation → END
```

## 📊 **Detailed LangGraph State Machine**

### **State Object Structure**
```python
class HiringState(TypedDict):
    # User Input
    original_request: str
    user_responses: Dict[str, str]
    
    # Context Analysis  
    role_type: str                 # "engineering", "marketing", "sales", "executive"
    company_stage: str             # "seed", "series_a", "growth", "enterprise"  
    urgency_level: str             # "low", "medium", "high", "emergency"
    
    # Conversation Management
    current_step: str              # Current workflow step
    questions_asked: List[str]     # Questions we've asked
    questions_remaining: List[str] # Questions still to ask
    conversation_history: List[Dict] # Full conversation log
    
    # Generated Content
    job_description: Optional[str]
    hiring_checklist: Optional[List[Dict]]
    timeline_estimate: Optional[Dict]
    recommendations: List[str]
    
    # Workflow Control
    is_complete: bool
    needs_clarification: bool
    error_message: Optional[str]
```

## 🔀 **LangGraph Node Definitions**

### **1. Request Analyzer Node**
```python
def analyze_request_node(state: HiringState) -> HiringState:
    """
    Analyzes initial hiring request to extract:
    - Role type (engineering, marketing, sales, executive)
    - Urgency indicators
    - Company stage hints
    - Initial context
    """
    # OpenAI call to analyze request
    # Updates: role_type, company_stage, urgency_level, current_step
```

### **2. Question Generator Node**  
```python
def generate_questions_node(state: HiringState) -> HiringState:
    """
    Uses Intelligent Questioning Framework to generate 
    contextually relevant questions based on:
    - Role type identified
    - Company stage
    - Research-backed question priorities
    """
    # Uses our research + intelligent questioning algorithm
    # Updates: questions_remaining, current_step
```

### **3. Question Presenter Node**
```python  
def present_questions_node(state: HiringState) -> HiringState:
    """
    Presents questions to user in conversational format
    Manages question flow (not overwhelming user)
    """
    # Formats questions for user
    # Updates: questions_asked, current_step = "awaiting_user_response"
```

### **4. Response Processor Node**
```python
def process_response_node(state: HiringState) -> HiringState:
    """
    Processes user responses and builds context
    Decides if more questions needed or ready for generation
    """
    # Analyzes user responses
    # Updates: user_responses, needs_clarification, current_step
```

### **5. Content Generator Node**
```python
def generate_content_node(state: HiringState) -> HiringState:
    """
    Generates job description, checklist, timeline
    Uses all accumulated context for rich generation
    """
    # Multiple OpenAI calls with full context
    # Updates: job_description, hiring_checklist, timeline_estimate
```

### **6. Response Formatter Node**
```python
def format_response_node(state: HiringState) -> HiringState:
    """
    Formats final response with all generated content
    Provides structured output (markdown/JSON)
    """
    # Formats final response
    # Updates: is_complete = True
```

## 🛤️ **LangGraph Edge Routing Logic**

### **Conditional Edges**
```python
def route_after_analysis(state: HiringState) -> str:
    """Routes after request analysis"""
    if state["role_type"] == "unknown":
        return "generate_questions"
    elif state["company_stage"] == "unknown": 
        return "generate_questions"
    else:
        return "generate_content"  # Skip questions if we have enough context

def route_after_questions(state: HiringState) -> str:
    """Routes after question generation"""
    if len(state["questions_remaining"]) > 0:
        return "present_questions"
    else:
        return "generate_content"

def route_after_response(state: HiringState) -> str:
    """Routes after processing user response"""
    if state["needs_clarification"]:
        return "generate_questions"  # Ask more questions
    else:
        return "generate_content"    # Ready to generate
```

## 🎯 **Conversation Flow Examples**

### **Scenario 1: Clear Request**
```
User: "I need to hire a senior backend engineer for my Series A startup, budget $140k, need to fill ASAP"

Flow: START → analyze_request → generate_content → format_response → END
(Skips questions because request has sufficient context)
```

### **Scenario 2: Vague Request**
```  
User: "I need to hire someone technical"

Flow: START → analyze_request → generate_questions → present_questions → 
      [USER RESPONDS] → process_response → generate_content → format_response → END
```

### **Scenario 3: Iterative Clarification**
```
User: "Need to hire for marketing"

Flow: START → analyze_request → generate_questions → present_questions →
      [USER RESPONDS] → process_response → generate_questions → present_questions →
      [USER RESPONDS] → process_response → generate_content → format_response → END
```

## 🧠 **Intelligent Routing Features**

### **Context-Aware Question Prioritization**
- **Seed Stage Companies**: Prioritize culture fit, equity comfort, generalist questions
- **Growth Stage Companies**: Focus on scaling experience, leadership, specialization
- **Technical Roles**: Emphasize tech stack, architecture experience, team size
- **Executive Roles**: Strategic vision, board experience, scaling challenges

### **Smart Question Batching**
- Present 2-3 questions max at once (avoid overwhelming)
- Group related questions together
- Prioritize most important questions first
- Skip questions if context is already clear

### **Dynamic Content Generation**
- Job descriptions adapt to company stage and role level
- Checklists include stage-appropriate complexity
- Timelines factor in urgency and market conditions
- Recommendations personalized to context

## 🔧 **Implementation Architecture**

```python
from langgraph.graph import StateGraph, END

# Build the graph
workflow = StateGraph(HiringState)

# Add nodes
workflow.add_node("analyze_request", analyze_request_node)
workflow.add_node("generate_questions", generate_questions_node)  
workflow.add_node("present_questions", present_questions_node)
workflow.add_node("process_response", process_response_node)
workflow.add_node("generate_content", generate_content_node)
workflow.add_node("format_response", format_response_node)

# Add edges
workflow.set_entry_point("analyze_request")
workflow.add_conditional_edges("analyze_request", route_after_analysis)
workflow.add_conditional_edges("generate_questions", route_after_questions)
workflow.add_edge("present_questions", "process_response") 
workflow.add_conditional_edges("process_response", route_after_response)
workflow.add_edge("generate_content", "format_response")
workflow.add_edge("format_response", END)

# Compile the graph
app = workflow.compile()
```

## 🎭 **User Experience Flow**

### **Example Conversation**
```
🤖 HR Assistant: Hi! I'm here to help you plan your hiring process. What role are you looking to fill?

👤 User: I need to hire an engineer

🤖 HR Assistant: Great! To create the best hiring plan for you, I have a few quick questions:

1. What's your company stage - are you seed stage, Series A, or further along?
2. What's your budget range for this role?  
3. How quickly do you need to fill this position?

👤 User: We're Series A, budget around $130k, and we need someone within 6 weeks

🤖 HR Assistant: Perfect! Based on your Series A stage and timeline, I'll create a comprehensive hiring plan for a mid-to-senior backend engineer role...

[Generated Content: Job Description, Hiring Checklist, Timeline, Recommendations]
```

## ✨ **Unique AI Features Integration**

### **Intelligent Questioning Algorithm**
- Dynamic question prioritization based on context
- Research-backed questioning strategies  
- Adaptive follow-up based on user responses

### **Context-Aware Generation**
- Job descriptions tailored to company stage
- Interview processes appropriate for role level
- Realistic timelines based on market conditions

### **Workflow Orchestration**  
- Smart routing that adapts to conversation needs
- Efficient question batching and flow management
- Context preservation throughout entire workflow

---

This workflow design ensures our HR Assistant provides intelligent, contextual assistance that feels natural and valuable to users while showcasing sophisticated AI reasoning beyond basic chatbot interactions.
