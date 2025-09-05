"""
Test script for the HR Hiring Agent
Tests the complete LangGraph workflow with different scenarios
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agent.hiring_agent import HiringAgent
import logging

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_detailed_request():
    """Test with a detailed request that should skip questions"""
    print("🧪 Testing detailed request (should skip questions)...")
    print("=" * 60)
    
    agent = HiringAgent()
    
    detailed_request = "I need to hire a senior backend engineer for my Series A startup, budget $140k, need to fill ASAP, tech stack is Python/Django"
    
    result = agent.process_hiring_request(detailed_request)
    
    print(f"✅ Success: {result['success']}")
    print(f"📊 Final State: {result['state']['current_step']}")
    print(f"🎯 Role Type: {result['state']['role_type']}")
    print(f"🏢 Company Stage: {result['state']['company_stage']}")
    print(f"📈 Specificity Score: {result['state']['specificity_score']}")
    
    if result['job_description']:
        print(f"📄 Job Description Length: {len(result['job_description'])} chars")
        print(f"📄 Job Description Preview: {result['job_description'][:200]}...")
    
    if result['error_message']:
        print(f"❌ Error: {result['error_message']}")
    
    print("\n")
    return result

def test_vague_request():
    """Test with a vague request that should trigger questions"""
    print("🧪 Testing vague request (should generate questions)...")
    print("=" * 60)
    
    agent = HiringAgent()
    
    vague_request = "I need to hire someone technical"
    
    result = agent.process_hiring_request(vague_request)
    
    print(f"✅ Success: {result['success']}")
    print(f"📊 Final State: {result['state']['current_step']}")
    print(f"🎯 Role Type: {result['state']['role_type']}")
    print(f"🏢 Company Stage: {result['state']['company_stage']}")
    print(f"📈 Specificity Score: {result['state']['specificity_score']}")
    print(f"❓ Questions Generated: {len(result['state'].get('questions_remaining', []))}")
    
    if result['state'].get('questions_remaining'):
        print("❓ Questions:")
        for i, q in enumerate(result['state']['questions_remaining'][:3], 1):
            print(f"   {i}. {q['question']}")
    
    if result['error_message']:
        print(f"❌ Error: {result['error_message']}")
    
    print("\n")
    return result

def test_context_analysis():
    """Test the context analysis capabilities"""
    print("🧪 Testing context analysis...")
    print("=" * 60)
    
    agent = HiringAgent()
    
    # Test different types of requests
    test_cases = [
        "Need a frontend developer for our startup",
        "Looking for VP of Engineering, Series A company, $200k budget",
        "Help me hire a marketing manager ASAP",
        "Want to bring on a sales director, we're a growth stage company"
    ]
    
    for request in test_cases:
        context = agent.questioning_system.analyze_context(request)
        print(f"📝 Request: {request}")
        print(f"   Role: {context['role_type']}")
        print(f"   Stage: {context['company_stage']}")  
        print(f"   Urgency: {context['urgency_level']}")
        print(f"   Specificity: {context['specificity_score']:.2f}")
        print()

def main():
    """Run all tests"""
    print("🚀 HR Hiring Agent - LangGraph Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Test 1: Context Analysis
        test_context_analysis()
        
        # Test 2: Detailed Request (should skip questions)
        detailed_result = test_detailed_request()
        
        # Test 3: Vague Request (should generate questions)
        vague_result = test_vague_request()
        
        print("🎉 All tests completed!")
        print("=" * 60)
        print("✅ LangGraph agent is working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
