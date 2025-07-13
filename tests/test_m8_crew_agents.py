import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import tempfile
import sys
import os
from datetime import datetime

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "m8-crew-agents"))

from crew_agents import (
    AgentMemory,
    MockLLMAgent,
    DataAnalystAgent,
    ReportGeneratorAgent,
    RootCauseAnalyzer,
    CrewOrchestrator
)


class TestAgentMemory:
    def test_agent_memory_initialization(self):
        """Test AgentMemory initialization."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        
        assert memory.memory_file == memory_file
        assert isinstance(memory.memory, dict)
        assert "conversations" in memory.memory
        assert "insights" in memory.memory
        assert "patterns" in memory.memory
        
        # Cleanup
        memory_file.unlink()

    def test_memory_persistence(self):
        """Test memory save and load functionality."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        
        # Add test data
        test_conversation = {"agent": "test", "task": "test task"}
        memory.add_conversation(test_conversation)
        
        test_insight = "Test insight"
        memory.add_insight(test_insight)
        
        # Create new instance to test loading
        memory2 = AgentMemory(memory_file)
        
        assert len(memory2.memory["conversations"]) == 1
        assert len(memory2.memory["insights"]) == 1
        assert memory2.memory["conversations"][0]["agent"] == "test"
        assert memory2.memory["insights"][0]["content"] == test_insight
        
        # Cleanup
        memory_file.unlink()

    def test_get_recent_conversations(self):
        """Test getting recent conversations."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        
        # Add multiple conversations
        for i in range(10):
            memory.add_conversation({"agent": f"agent{i}", "task": f"task{i}"})
        
        recent = memory.get_recent_conversations(3)
        assert len(recent) == 3
        assert recent[0]["agent"] == "agent7"  # -3 from end
        assert recent[2]["agent"] == "agent9"  # last one
        
        # Cleanup
        memory_file.unlink()


class TestMockLLMAgent:
    def test_agent_initialization(self):
        """Test MockLLMAgent initialization."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        agent = MockLLMAgent("Test Agent", "Test goal", "Test backstory", memory)
        
        assert agent.role == "Test Agent"
        assert agent.goal == "Test goal"
        assert agent.backstory == "Test backstory"
        assert agent.memory == memory
        
        # Cleanup
        memory_file.unlink()

    def test_process_task(self):
        """Test task processing."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        agent = MockLLMAgent("Test Agent", "Test goal", "Test backstory", memory)
        
        task = "Test task"
        context = {"key": "value"}
        
        response = agent.process_task(task, context)
        
        assert "[Test Agent]" in response
        assert "Test task" in response
        assert len(memory.memory["conversations"]) == 1
        
        # Cleanup
        memory_file.unlink()

    def test_process_task_error_handling(self):
        """Test error handling in task processing."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        agent = MockLLMAgent("Test Agent", "Test goal", "Test backstory", memory)
        
        # Mock _generate_response to raise exception
        with patch.object(agent, '_generate_response', side_effect=Exception("Test error")):
            response = agent.process_task("test task")
            assert "Error: Test error" in response
        
        # Cleanup
        memory_file.unlink()


class TestDataAnalystAgent:
    def test_data_analyst_initialization(self):
        """Test DataAnalystAgent initialization."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        agent = DataAnalystAgent(memory)
        
        assert agent.role == "Data Analyst"
        assert "data analysis" in agent.goal.lower()
        
        # Cleanup
        memory_file.unlink()

    def test_analyze_data(self):
        """Test data analysis functionality."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        agent = DataAnalystAgent(memory)
        
        test_data = {"metric1": 100, "metric2": 200, "metric3": 300}
        result = agent.analyze_data(test_data)
        
        assert "summary" in result
        assert "trends" in result
        assert "recommendations" in result
        assert "confidence" in result
        assert isinstance(result["trends"], list)
        assert isinstance(result["recommendations"], list)
        
        # Check memory was updated
        assert len(memory.memory["insights"]) == 1
        
        # Cleanup
        memory_file.unlink()

    def test_analyze_data_error_handling(self):
        """Test error handling in data analysis."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        agent = DataAnalystAgent(memory)
        
        # Mock memory.add_insight to raise exception
        with patch.object(memory, 'add_insight', side_effect=Exception("Memory error")):
            result = agent.analyze_data({"test": "data"})
            assert "error" in result
        
        # Cleanup
        memory_file.unlink()


class TestReportGeneratorAgent:
    def test_report_generator_initialization(self):
        """Test ReportGeneratorAgent initialization."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        agent = ReportGeneratorAgent(memory)
        
        assert agent.role == "Report Generator"
        assert "report" in agent.goal.lower()
        
        # Cleanup
        memory_file.unlink()

    def test_generate_report(self):
        """Test report generation functionality."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        agent = ReportGeneratorAgent(memory)
        
        analysis = {
            "summary": "Test summary",
            "trends": ["Trend 1", "Trend 2"],
            "recommendations": ["Rec 1", "Rec 2"],
            "confidence": 0.95
        }
        
        report = agent.generate_report(analysis)
        
        assert "# Automated Intelligence Report" in report
        assert "Test summary" in report
        assert "Trend 1" in report
        assert "Trend 2" in report
        assert "Rec 1" in report
        assert "Rec 2" in report
        assert "0.95" in report
        
        # Check memory was updated
        assert len(memory.memory["insights"]) == 1
        
        # Cleanup
        memory_file.unlink()


class TestRootCauseAnalyzer:
    def test_root_cause_analyzer_initialization(self):
        """Test RootCauseAnalyzer initialization."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        agent = RootCauseAnalyzer(memory)
        
        assert agent.role == "Root Cause Analyzer"
        assert "root cause" in agent.goal.lower()
        
        # Cleanup
        memory_file.unlink()

    def test_analyze_issue(self):
        """Test root cause analysis functionality."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            memory_file = Path(tmp.name)
        
        memory = AgentMemory(memory_file)
        agent = RootCauseAnalyzer(memory)
        
        issue = "API timeout"
        symptoms = ["High latency", "Connection errors"]
        context = {"load": "high"}
        
        result = agent.analyze_issue(issue, symptoms, context)
        
        assert result["issue"] == issue
        assert result["symptoms"] == symptoms
        assert "potential_causes" in result
        assert "root_cause" in result
        assert "solution_steps" in result
        assert "confidence" in result
        
        # Check memory was updated
        assert len(memory.memory["insights"]) == 1
        
        # Cleanup
        memory_file.unlink()


class TestCrewOrchestrator:
    def test_crew_orchestrator_initialization(self):
        """Test CrewOrchestrator initialization."""
        with patch('crew_agents.MEMORY_FILE', Path(tempfile.mkdtemp()) / "test_memory.json"):
            orchestrator = CrewOrchestrator()
            
            assert hasattr(orchestrator, 'memory')
            assert hasattr(orchestrator, 'data_analyst')
            assert hasattr(orchestrator, 'report_generator')
            assert hasattr(orchestrator, 'root_cause_analyzer')
            assert isinstance(orchestrator.data_analyst, DataAnalystAgent)
            assert isinstance(orchestrator.report_generator, ReportGeneratorAgent)
            assert isinstance(orchestrator.root_cause_analyzer, RootCauseAnalyzer)

    def test_automated_analysis_workflow(self):
        """Test automated analysis workflow."""
        with patch('crew_agents.MEMORY_FILE', Path(tempfile.mkdtemp()) / "test_memory.json"):
            orchestrator = CrewOrchestrator()
            
            test_data = {
                "metrics": [{"cpu": 85, "memory": 76}],
                "anomalies": ["High CPU usage"],
                "timestamp": datetime.now().isoformat()
            }
            
            result = orchestrator.automated_analysis_workflow(test_data)
            
            assert "analysis" in result
            assert "report" in result
            assert "root_cause_analysis" in result
            assert "workflow_status" in result
            assert "timestamp" in result
            assert result["workflow_status"] == "completed"

    def test_automated_analysis_workflow_no_anomalies(self):
        """Test automated analysis workflow without anomalies."""
        with patch('crew_agents.MEMORY_FILE', Path(tempfile.mkdtemp()) / "test_memory.json"):
            orchestrator = CrewOrchestrator()
            
            test_data = {
                "metrics": [{"cpu": 50, "memory": 60}],
                "timestamp": datetime.now().isoformat()
            }
            
            result = orchestrator.automated_analysis_workflow(test_data)
            
            assert result["root_cause_analysis"] is None
            assert result["workflow_status"] == "completed"

    def test_interactive_session(self):
        """Test interactive session functionality."""
        with patch('crew_agents.MEMORY_FILE', Path(tempfile.mkdtemp()) / "test_memory.json"):
            orchestrator = CrewOrchestrator()
            
            # Test data query
            response = orchestrator.interactive_session("Can you analyze the recent data?")
            assert "[Data Analyst]" in response
            
            # Test report query
            response = orchestrator.interactive_session("Generate a report please")
            assert "[Report Generator]" in response
            
            # Test problem query
            response = orchestrator.interactive_session("There's a problem with the system")
            assert "[Root Cause Analyzer]" in response
            
            # Test default query
            response = orchestrator.interactive_session("Hello")
            assert "[Data Analyst]" in response  # Default agent

    def test_workflow_error_handling(self):
        """Test error handling in workflow."""
        with patch('crew_agents.MEMORY_FILE', Path(tempfile.mkdtemp()) / "test_memory.json"):
            orchestrator = CrewOrchestrator()
            
            # Mock data_analyst.analyze_data to raise exception
            with patch.object(orchestrator.data_analyst, 'analyze_data', side_effect=Exception("Test error")):
                result = orchestrator.automated_analysis_workflow({"test": "data"})
                assert "error" in result


class TestIntegration:
    def test_full_workflow_integration(self):
        """Test complete workflow integration."""
        with patch('crew_agents.MEMORY_FILE', Path(tempfile.mkdtemp()) / "test_memory.json"):
            orchestrator = CrewOrchestrator()
            
            # Run complete workflow
            test_data = {
                "metrics": [{"cpu": 85, "memory": 76}, {"cpu": 90, "memory": 82}],
                "anomalies": ["High CPU usage", "Memory spike"],
                "timestamp": datetime.now().isoformat()
            }
            
            result = orchestrator.automated_analysis_workflow(test_data)
            
            # Verify all components worked
            assert result["workflow_status"] == "completed"
            assert "analysis" in result
            assert "report" in result
            assert result["root_cause_analysis"] is not None
            
            # Verify memory was updated
            assert len(orchestrator.memory.memory["conversations"]) > 0
            assert len(orchestrator.memory.memory["insights"]) > 0
            
            # Test interactive session uses the accumulated memory
            response = orchestrator.interactive_session("What patterns do you see?")
            assert "Previous insights" in response or "Recent interactions" in response

    def test_memory_persistence_across_sessions(self):
        """Test memory persistence across multiple sessions."""
        memory_file = Path(tempfile.mkdtemp()) / "test_memory.json"
        
        with patch('crew_agents.MEMORY_FILE', memory_file):
            # First session
            orchestrator1 = CrewOrchestrator()
            orchestrator1.interactive_session("First query")
            
            # Second session
            orchestrator2 = CrewOrchestrator()
            orchestrator2.interactive_session("Second query")
            
            # Memory should persist
            assert len(orchestrator2.memory.memory["conversations"]) == 2 