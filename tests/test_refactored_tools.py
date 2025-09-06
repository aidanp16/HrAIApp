"""
Test Suite for Refactored LLM-Based Tools

This test suite validates that all refactored tools work correctly with LLM intelligence
instead of hardcoded templates. Tests cover individual tool functionality and
end-to-end system integration.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the refactored tools
from tools.job_description_generator import JobDescriptionGeneratorTool
from tools.search_tool import SearchSalaryTool  
from tools.timeline_calculator import TimelineCalculatorTool
from tools.interview_generator import InterviewGeneratorTool
from tools.checklist_builder import ChecklistBuilderTool
from tools.skills_analyzer import SkillsAnalyzerTool


class TestRefactoredTools:
    """Test individual LLM-based tools"""
    
    def setup_method(self):
        """Setup test data for each test"""
        self.sample_hiring_context = {
            "role_title": "Senior Software Engineer",
            "department": "Engineering", 
            "seniority_level": "senior",
            "company_stage": "series_a",
            "location": "San Francisco, CA",
            "remote_policy": "hybrid",
            "original_request": "We need to hire a senior backend engineer for our API team",
            "user_responses": {
                "role_details": "Python/Django backend engineer with AWS experience",
                "timeline": "Need to hire within 8 weeks",
                "budget": "Budget is $180k-220k"
            },
            "tech_stack": "Python, Django, PostgreSQL, AWS",
            "industry": "SaaS",
            "urgency": "urgent",
            "has_budget": True,
            "has_timeline": True
        }
        
        self.mock_llm_response = Mock()
        self.mock_llm_response.content = "Mocked LLM response content"

    @patch('tools.job_description_generator.ChatOpenAI')
    def test_job_description_generator_tool(self, mock_openai):
        """Test that Job Description Generator produces structured output"""
        # Setup mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = self.mock_llm_response
        mock_openai.return_value = mock_llm
        
        # Test the tool
        tool = JobDescriptionGeneratorTool()
        result = tool._run(self.sample_hiring_context)
        
        # Assertions
        assert result == "Mocked LLM response content"
        mock_llm.invoke.assert_called_once()
        
        # Verify the context passed to LLM includes key information
        call_args = mock_llm.invoke.call_args[0][0]
        assert call_args["role_title"] == "Senior Software Engineer"
        assert call_args["company_stage"] == "series_a"
        assert call_args["seniority_level"] == "senior"

    @patch('tools.search_tool.ChatOpenAI')
    def test_search_salary_tool(self, mock_openai):
        """Test that Salary Benchmarking Tool produces market analysis"""
        # Setup mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = self.mock_llm_response
        mock_openai.return_value = mock_llm
        
        # Test the tool
        tool = SearchSalaryTool()
        result = tool._run(self.sample_hiring_context)
        
        # Assertions
        assert result == "Mocked LLM response content"
        mock_llm.invoke.assert_called_once()
        
        # Verify the context includes salary-relevant information
        call_args = mock_llm.invoke.call_args[0][0]
        assert call_args["role_title"] == "Senior Software Engineer"
        assert call_args["location"] == "San Francisco, CA"
        assert call_args["urgency"] == "urgent"

    @patch('tools.timeline_calculator.ChatOpenAI')
    def test_timeline_calculator_tool(self, mock_openai):
        """Test that Timeline Calculator produces project plans"""
        # Setup mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = self.mock_llm_response
        mock_openai.return_value = mock_llm
        
        # Test the tool
        tool = TimelineCalculatorTool()
        result = tool._run(self.sample_hiring_context)
        
        # Assertions
        assert result == "Mocked LLM response content"
        mock_llm.invoke.assert_called_once()
        
        # Verify timeline-specific context
        call_args = mock_llm.invoke.call_args[0][0]
        assert call_args["urgency"] == "urgent"
        assert call_args["seniority_level"] == "senior"
        assert call_args["has_timeline"] == "Yes"

    @patch('tools.interview_generator.ChatOpenAI')
    def test_interview_generator_tool(self, mock_openai):
        """Test that Interview Generator produces interview guides"""
        # Setup mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = self.mock_llm_response
        mock_openai.return_value = mock_llm
        
        # Test the tool
        tool = InterviewGeneratorTool()
        result = tool._run(self.sample_hiring_context)
        
        # Assertions
        assert result == "Mocked LLM response content"
        mock_llm.invoke.assert_called_once()
        
        # Verify interview-specific context
        call_args = mock_llm.invoke.call_args[0][0]
        assert call_args["role_title"] == "Senior Software Engineer"
        assert call_args["tech_stack"] == "Python, Django, PostgreSQL, AWS"

    @patch('tools.checklist_builder.ChatOpenAI')
    def test_checklist_builder_tool(self, mock_openai):
        """Test that Checklist Builder produces hiring processes"""
        # Setup mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = self.mock_llm_response
        mock_openai.return_value = mock_llm
        
        # Test the tool
        tool = ChecklistBuilderTool()
        result = tool._run(self.sample_hiring_context)
        
        # Assertions
        assert result == "Mocked LLM response content"
        mock_llm.invoke.assert_called_once()
        
        # Verify checklist-specific context
        call_args = mock_llm.invoke.call_args[0][0]
        assert call_args["company_stage"] == "series_a"
        assert call_args["urgency"] == "urgent"

    @patch('tools.skills_analyzer.ChatOpenAI')
    def test_skills_analyzer_tool(self, mock_openai):
        """Test that Skills Analyzer produces candidate evaluation"""
        # Setup mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = self.mock_llm_response
        mock_openai.return_value = mock_llm
        
        # Test the tool with candidate profile
        tool = SkillsAnalyzerTool()
        candidate_profile = """
        John Doe - Senior Software Engineer
        - 8 years Python/Django experience
        - 5 years AWS cloud architecture 
        - Led teams of 4-6 engineers
        - Built scalable APIs serving 10M+ requests/day
        """
        
        result = tool._run(candidate_profile, self.sample_hiring_context)
        
        # Assertions
        assert result == "Mocked LLM response content"
        mock_llm.invoke.assert_called_once()
        
        # Verify skills analysis context
        call_args = mock_llm.invoke.call_args[0][0]
        assert call_args["role_title"] == "Senior Software Engineer"
        assert call_args["candidate_profile"] == candidate_profile

    def test_error_handling_for_all_tools(self):
        """Test that all tools handle errors gracefully"""
        tools_and_contexts = [
            (JobDescriptionGeneratorTool(), self.sample_hiring_context),
            (SearchSalaryTool(), self.sample_hiring_context),
            (TimelineCalculatorTool(), self.sample_hiring_context),
            (InterviewGeneratorTool(), self.sample_hiring_context),
            (ChecklistBuilderTool(), self.sample_hiring_context),
            (SkillsAnalyzerTool(), ("candidate profile", self.sample_hiring_context)),
        ]
        
        for tool, context in tools_and_contexts:
            # Mock LLM to raise an exception
            with patch.object(tool.__class__.__name__.replace('Tool', '').lower() + '_analyzer' if 'skills' in tool.__class__.__name__.lower() else
                             tool.__class__.__name__.replace('Tool', '').lower().replace('searchsalary', 'market_analyzer').replace('jobdescriptiongenerator', 'generator').replace('timelinecalculator', 'timeline_analyzer').replace('interviewgenerator', 'interview_generator').replace('checklistbuilder', 'builder'), 
                             'llm') as mock_llm:
                mock_llm.invoke.side_effect = Exception("LLM API Error")
                
                if isinstance(context, tuple):
                    result = tool._run(*context)
                else:
                    result = tool._run(context)
                
                # Should return error message, not crash
                assert "Error" in result
                assert isinstance(result, str)


class TestSystemIntegration:
    """Test end-to-end system integration with refactored tools"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.sample_state = {
            'original_request': 'Need to hire a senior Python developer for our SaaS startup',
            'company_stage': 'series_a',
            'role_type': 'engineering',
            'urgency_level': 'high',
            'has_budget': True,
            'has_timeline': True,
            'user_responses': {
                'role_details': 'Senior backend engineer with Python/Django expertise',
                'tech_requirements': 'Python, Django, PostgreSQL, AWS, Docker',
                'timeline': 'Need to hire within 6 weeks',
                'budget': 'Budget range $160k-200k',
                'team_info': 'Will be joining a 5-person engineering team'
            },
            'specificity_score': 0.8,
            'confidence_scores': {'role_type': 0.9, 'urgency': 0.8, 'budget': 0.9}
        }

    @patch('tools.job_description_generator.ChatOpenAI')
    @patch('tools.search_tool.ChatOpenAI')
    @patch('tools.timeline_calculator.ChatOpenAI')
    @patch('tools.interview_generator.ChatOpenAI') 
    @patch('tools.checklist_builder.ChatOpenAI')
    def test_all_tools_work_together(self, mock_checklist_llm, mock_interview_llm, 
                                   mock_timeline_llm, mock_salary_llm, mock_job_llm):
        """Test that all refactored tools can be used together in sequence"""
        
        # Setup mocks for all tools
        mock_responses = {
            'job_description': Mock(content="# Senior Python Developer\n\nWe are seeking..."),
            'salary_data': Mock(content="# Salary Benchmarking Report\n\nBase Salary: $160k-200k..."),
            'timeline': Mock(content="# Hiring Timeline\n\nWeek 1: Job posting..."),
            'interview': Mock(content="# Interview Guide\n\nTechnical questions..."),
            'checklist': Mock(content="# Hiring Checklist\n\nPhase 1: Preparation...")
        }
        
        mock_job_llm.return_value.invoke.return_value = mock_responses['job_description']
        mock_salary_llm.return_value.invoke.return_value = mock_responses['salary_data']
        mock_timeline_llm.return_value.invoke.return_value = mock_responses['timeline']
        mock_interview_llm.return_value.invoke.return_value = mock_responses['interview']
        mock_checklist_llm.return_value.invoke.return_value = mock_responses['checklist']
        
        # Simulate the hiring context building (simplified version of what hiring agent does)
        hiring_context = {
            "company_stage": self.sample_state.get('company_stage', 'seed'),
            "role_type": self.sample_state.get('role_type', 'engineering'),
            "urgency_level": self.sample_state.get('urgency_level', 'medium'),
            "original_request": self.sample_state.get('original_request', ''),
            "user_responses": self.sample_state.get('user_responses', {}),
            "role_title": "Senior Python Developer",
            "department": "Engineering",
            "seniority_level": "senior",
            "location": "San Francisco, CA",
            "remote_policy": "hybrid",
            "urgency": "urgent",
            "industry": "Technology",
            "tech_stack": "Python, Django, PostgreSQL, AWS"
        }
        
        # Initialize all tools
        job_tool = JobDescriptionGeneratorTool()
        salary_tool = SearchSalaryTool()
        timeline_tool = TimelineCalculatorTool()
        interview_tool = InterviewGeneratorTool()
        checklist_tool = ChecklistBuilderTool()
        
        # Execute all tools
        results = {}
        results['job_description'] = job_tool._run(hiring_context)
        results['salary_data'] = salary_tool._run(hiring_context)
        results['timeline'] = timeline_tool._run(hiring_context)
        results['interview_guide'] = interview_tool._run(hiring_context)
        results['checklist'] = checklist_tool._run(hiring_context)
        
        # Verify all tools produced output
        for key, result in results.items():
            assert isinstance(result, str)
            assert len(result) > 0
            assert result.startswith("#")  # Should be formatted markdown
        
        # Verify comprehensive hiring package
        assert "Senior Python Developer" in results['job_description']
        assert "Salary Benchmarking" in results['salary_data']
        assert "Hiring Timeline" in results['timeline']
        assert "Interview Guide" in results['interview_guide']
        assert "Hiring Checklist" in results['checklist']

    def test_context_consistency_across_tools(self):
        """Test that the same context produces consistent information across tools"""
        
        hiring_context = {
            "role_title": "Data Scientist",
            "company_stage": "seed",
            "seniority_level": "mid",
            "urgency": "normal",
            "location": "Austin, TX",
            "original_request": "Looking for a data scientist to join our AI startup",
            "user_responses": {"skills": "Python, ML, TensorFlow"},
            "tech_stack": "Python, TensorFlow, AWS"
        }
        
        # Mock all LLMs to return context-aware responses
        with patch('tools.job_description_generator.ChatOpenAI') as mock_job_llm, \
             patch('tools.search_tool.ChatOpenAI') as mock_salary_llm, \
             patch('tools.timeline_calculator.ChatOpenAI') as mock_timeline_llm:
            
            # Setup mocks that echo back the context
            def create_context_echo(tool_name):
                def echo_context(context):
                    response = Mock()
                    response.content = f"{tool_name} - Role: {context['role_title']}, Stage: {context['company_stage']}"
                    return response
                return echo_context
            
            mock_job_llm.return_value.invoke.side_effect = create_context_echo("JOB_DESC")
            mock_salary_llm.return_value.invoke.side_effect = create_context_echo("SALARY")
            mock_timeline_llm.return_value.invoke.side_effect = create_context_echo("TIMELINE")
            
            # Run tools
            job_tool = JobDescriptionGeneratorTool()
            salary_tool = SearchSalaryTool()
            timeline_tool = TimelineCalculatorTool()
            
            job_result = job_tool._run(hiring_context)
            salary_result = salary_tool._run(hiring_context)
            timeline_result = timeline_tool._run(hiring_context)
            
            # Verify consistent context usage
            assert "Data Scientist" in job_result and "seed" in job_result
            assert "Data Scientist" in salary_result and "seed" in salary_result
            assert "Data Scientist" in timeline_result and "seed" in timeline_result


class TestRegressionChecks:
    """Test that refactored tools maintain or improve functionality"""
    
    def test_tools_use_llm_not_hardcoded_data(self):
        """Verify that tools are using LLM generation, not hardcoded templates"""
        
        # Test that tools have LLM instances and prompt templates
        tools = [
            JobDescriptionGeneratorTool(),
            SearchSalaryTool(), 
            TimelineCalculatorTool(),
            InterviewGeneratorTool(),
            ChecklistBuilderTool(),
            SkillsAnalyzerTool()
        ]
        
        for tool in tools:
            # Each tool should have an analyzer/generator with LLM
            analyzer_attrs = ['generator', 'market_analyzer', 'timeline_analyzer', 
                            'interview_generator', 'builder', 'skills_analyzer']
            
            has_analyzer = any(hasattr(tool, attr) for attr in analyzer_attrs)
            assert has_analyzer, f"{tool.__class__.__name__} should have an LLM-based analyzer component"
            
            # Find the analyzer
            analyzer = None
            for attr in analyzer_attrs:
                if hasattr(tool, attr):
                    analyzer = getattr(tool, attr)
                    break
            
            # Verify analyzer has LLM and prompt
            assert hasattr(analyzer, 'llm'), f"{tool.__class__.__name__} analyzer should have LLM instance"
            assert hasattr(analyzer, 'prompt') or any(hasattr(analyzer, f'{name}_prompt') 
                          for name in ['job_description', 'salary', 'timeline', 'interview', 'checklist', 'skills']), \
                   f"{tool.__class__.__name__} analyzer should have prompt template"

    def test_no_hardcoded_templates_remain(self):
        """Verify that no hardcoded templates or data structures remain in tools"""
        
        import inspect
        from tools import job_description_generator, search_tool, timeline_calculator, interview_generator
        
        modules = [job_description_generator, search_tool, timeline_calculator, interview_generator]
        
        for module in modules:
            source = inspect.getsource(module)
            
            # Should not contain large hardcoded data structures
            assert 'TEMPLATE_MAPPING' not in source
            assert 'HARDCODED_QUESTIONS' not in source
            assert 'SALARY_RANGES' not in source
            assert 'TIMELINE_MATRIX' not in source
            
            # Should contain LLM usage
            assert 'ChatOpenAI' in source
            assert 'ChatPromptTemplate' in source


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
