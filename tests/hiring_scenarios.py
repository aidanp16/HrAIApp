"""
Comprehensive Hiring Scenario Test Cases
Tests the HR Hiring Agent across different role types, company stages, and complexity levels

These scenarios validate that our agent can handle:
- Different role types (Engineering, Marketing, Sales, Executive)  
- Different company stages (Seed, Series A, Growth)
- Various levels of request specificity
- Edge cases and challenging scenarios
"""

import sys
import os
# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agent.hiring_agent import HiringAgent
import logging
import json
from datetime import datetime

class HiringScenarioTester:
    """
    Comprehensive test suite for hiring scenarios
    Validates agent behavior across different contexts and use cases
    """
    
    def __init__(self):
        self.agent = HiringAgent()
        self.test_results = []
        self.setup_logging()
        
    def setup_logging(self):
        """Set up detailed logging for test analysis"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tests/test_results.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def run_scenario(self, scenario_name: str, request: str, expected_outcomes: dict) -> dict:
        """
        Run a single hiring scenario and validate results
        
        Args:
            scenario_name: Name of the test scenario
            request: The hiring request to test
            expected_outcomes: Dict of expected results to validate
            
        Returns:
            Dict with test results and analysis
        """
        self.logger.info(f"🧪 Running scenario: {scenario_name}")
        self.logger.info(f"📝 Request: {request}")
        
        # Run the agent
        result = self.agent.process_hiring_request(request)
        
        # Analyze results
        analysis = self._analyze_result(result, expected_outcomes)
        
        test_result = {
            'scenario_name': scenario_name,
            'request': request,
            'success': result['success'],
            'expected_outcomes': expected_outcomes,
            'actual_results': {
                'role_type': result['state']['role_type'],
                'company_stage': result['state']['company_stage'],
                'specificity_score': result['state']['specificity_score'],
                'questions_generated': len(result['state'].get('questions_remaining', [])),
                'job_description_length': len(result.get('job_description', '') or ''),
                'workflow_path': result['state']['current_step'],
                'error': result.get('error_message')
            },
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(test_result)
        self._print_scenario_results(test_result)
        
        return test_result
    
    def _analyze_result(self, result: dict, expected: dict) -> dict:
        """Analyze test result against expected outcomes"""
        analysis = {
            'role_detection_correct': result['state']['role_type'] == expected.get('role_type'),
            'stage_detection_correct': result['state']['company_stage'] == expected.get('company_stage'),
            'specificity_appropriate': self._check_specificity(result['state']['specificity_score'], expected.get('specificity_level')),
            'questions_appropriate': self._check_questions(result['state'].get('questions_remaining', []), expected.get('should_ask_questions')),
            'content_generated': bool(result.get('job_description')),
            'workflow_completed': result['state']['current_step'] == 'response_formatted',
            'overall_success': result['success'] and not result.get('error_message')
        }
        
        analysis['score'] = sum(analysis.values()) / len(analysis) * 100
        return analysis
    
    def _check_specificity(self, actual_score: float, expected_level: str) -> bool:
        """Check if specificity score matches expected level"""
        if expected_level == 'high':
            return actual_score > 0.6
        elif expected_level == 'medium':
            return 0.3 <= actual_score <= 0.6
        elif expected_level == 'low':
            return actual_score < 0.3
        return True
    
    def _check_questions(self, questions: list, should_ask: bool) -> bool:
        """Check if question generation matches expectation"""
        has_questions = len(questions) > 0
        return has_questions == should_ask
    
    def _print_scenario_results(self, result: dict):
        """Print formatted results for a scenario"""
        print(f"\n{'='*60}")
        print(f"🧪 SCENARIO: {result['scenario_name']}")
        print(f"{'='*60}")
        
        print(f"✅ Success: {result['success']}")
        print(f"🎯 Role Detected: {result['actual_results']['role_type']}")
        print(f"🏢 Stage Detected: {result['actual_results']['company_stage']}")
        print(f"📊 Specificity Score: {result['actual_results']['specificity_score']:.2f}")
        print(f"❓ Questions Generated: {result['actual_results']['questions_generated']}")
        print(f"📄 Job Description: {result['actual_results']['job_description_length']} characters")
        print(f"🔄 Workflow Status: {result['actual_results']['workflow_path']}")
        
        if result['actual_results']['error']:
            print(f"❌ Error: {result['actual_results']['error']}")
        
        print(f"\n📈 ANALYSIS SCORE: {result['analysis']['score']:.1f}%")
        print("✅ PASSED:" if result['analysis']['score'] > 80 else "❌ NEEDS IMPROVEMENT:")
        for check, passed in result['analysis'].items():
            if check != 'score':
                status = "✅" if passed else "❌"
                print(f"   {status} {check.replace('_', ' ').title()}")

    def run_all_scenarios(self):
        """Run comprehensive test suite with all scenarios"""
        
        print("🚀 HR Hiring Agent - Comprehensive Scenario Testing")
        print("="*80)
        
        # SCENARIO 1: Detailed Engineering Request (Series A)
        self.run_scenario(
            "Detailed Engineering Request",
            "I need to hire a senior backend engineer for my Series A startup, budget $120-140k, need someone with Python/Django experience, team of 15 people, need to fill within 6 weeks for our API scaling project",
            {
                'role_type': 'engineering',
                'company_stage': 'series_a', 
                'specificity_level': 'high',
                'should_ask_questions': False  # Should skip questions due to detail
            }
        )
        
        # SCENARIO 2: Vague Technical Request (Unknown stage)
        self.run_scenario(
            "Vague Technical Request",
            "I need to hire someone technical for my company",
            {
                'role_type': 'engineering',
                'company_stage': 'unknown',
                'specificity_level': 'low', 
                'should_ask_questions': True  # Should generate questions
            }
        )
        
        # SCENARIO 3: Marketing Role (Growth Stage)
        self.run_scenario(
            "Marketing Role - Growth Stage",
            "Looking for a growth marketing manager, we're an established company with 100+ employees, need someone with paid acquisition experience",
            {
                'role_type': 'marketing',
                'company_stage': 'growth',
                'specificity_level': 'medium',
                'should_ask_questions': True  # Might need clarification
            }
        )
        
        # SCENARIO 4: Sales Role (Urgent)
        self.run_scenario(
            "Urgent Sales Hire",
            "Need to hire a sales director ASAP, we're a Series A company, revenue is growing fast and we need someone to scale our sales team",
            {
                'role_type': 'executive',  # Director level = executive
                'company_stage': 'series_a',
                'specificity_level': 'medium',
                'should_ask_questions': True  # May need budget/timeline details
            }
        )
        
        # SCENARIO 5: Executive Role (Seed Stage)
        self.run_scenario(
            "Executive Hire - Early Stage",
            "Startup looking for VP of Engineering, we're pre-revenue but have raised seed funding, need someone who can build the team from scratch",
            {
                'role_type': 'executive',
                'company_stage': 'seed',
                'specificity_level': 'medium', 
                'should_ask_questions': True  # Will need clarification
            }
        )
        
        # SCENARIO 6: Detailed Marketing Request (Budget specified)
        self.run_scenario(
            "Detailed Marketing Request",
            "Need a senior marketing manager for our SaaS company, Series A stage, budget $90-110k, need someone with B2B experience, content marketing and demand gen, timeline is 8 weeks",
            {
                'role_type': 'marketing', 
                'company_stage': 'series_a',
                'specificity_level': 'high',
                'should_ask_questions': False  # Very detailed request
            }
        )
        
        # SCENARIO 7: Operations Role (Edge case)
        self.run_scenario(
            "Operations Role Test",
            "Looking to hire a head of operations for our growing startup, need someone with scaling experience",
            {
                'role_type': 'operations',
                'company_stage': 'unknown',  # "Growing" is ambiguous
                'specificity_level': 'low',
                'should_ask_questions': True
            }
        )
        
        # Generate comprehensive report
        self._generate_test_report()
    
    def _generate_test_report(self):
        """Generate comprehensive test report with analysis"""
        
        print(f"\n\n🎯 COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['analysis']['overall_success'])
        avg_score = sum(r['analysis']['score'] for r in self.test_results) / total_tests
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Scenarios Tested: {total_tests}")
        print(f"   Successful Tests: {successful_tests}/{total_tests}")
        print(f"   Success Rate: {successful_tests/total_tests*100:.1f}%")
        print(f"   Average Analysis Score: {avg_score:.1f}%")
        
        print(f"\n🎯 CAPABILITY ANALYSIS:")
        
        # Role Detection Analysis
        role_correct = sum(1 for r in self.test_results if r['analysis']['role_detection_correct'])
        print(f"   Role Detection Accuracy: {role_correct}/{total_tests} ({role_correct/total_tests*100:.1f}%)")
        
        # Stage Detection Analysis  
        stage_correct = sum(1 for r in self.test_results if r['analysis']['stage_detection_correct'])
        print(f"   Stage Detection Accuracy: {stage_correct}/{total_tests} ({stage_correct/total_tests*100:.1f}%)")
        
        # Question Generation Analysis
        questions_correct = sum(1 for r in self.test_results if r['analysis']['questions_appropriate'])
        print(f"   Question Logic Accuracy: {questions_correct}/{total_tests} ({questions_correct/total_tests*100:.1f}%)")
        
        # Content Generation Analysis
        content_generated = sum(1 for r in self.test_results if r['analysis']['content_generated'])
        print(f"   Content Generation Success: {content_generated}/{total_tests} ({content_generated/total_tests*100:.1f}%)")
        
        print(f"\n📝 DETAILED BREAKDOWN:")
        for result in self.test_results:
            status = "✅ PASS" if result['analysis']['score'] > 80 else "❌ NEEDS WORK"
            print(f"   {result['scenario_name']}: {result['analysis']['score']:.1f}% {status}")
        
        # Save detailed results to file
        self._save_results_to_file()
        
        print(f"\n💾 Detailed results saved to: tests/scenario_test_results.json")
        print(f"📋 Test logs saved to: tests/test_results.log")
        
        if avg_score > 80:
            print(f"\n🎉 EXCELLENT! Agent performing well across all scenarios!")
        elif avg_score > 60:
            print(f"\n✅ GOOD! Agent working with room for improvement.")
        else:
            print(f"\n⚠️  NEEDS IMPROVEMENT! Agent requires optimization.")
    
    def _save_results_to_file(self):
        """Save detailed test results to JSON file for analysis"""
        results_file = 'tests/scenario_test_results.json'
        
        # Ensure tests directory exists
        os.makedirs('tests', exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump({
                'test_summary': {
                    'total_tests': len(self.test_results),
                    'timestamp': datetime.now().isoformat(),
                    'avg_score': sum(r['analysis']['score'] for r in self.test_results) / len(self.test_results)
                },
                'test_results': self.test_results
            }, f, indent=2)

def main():
    """Run the comprehensive hiring scenario test suite"""
    tester = HiringScenarioTester()
    tester.run_all_scenarios()

if __name__ == "__main__":
    main()
