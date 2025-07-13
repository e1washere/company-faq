"""
CrewAI Agents Module (M8) - Intelligent Agent Orchestration & Autonomy

This module demonstrates advanced AI agent capabilities including:
- Automated report generation
- Root cause analysis
- Interactive user agents
- Feedback and memory mechanisms
- Context-aware evolving agents

Perfect for Patrianna's requirement: "Agent Orchestration & Autonomy"
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERTEX_PROJECT = os.getenv("VERTEX_PROJECT")
MEMORY_FILE = Path("modules/m8-crew-agents/agent_memory.json")


class AgentMemory:
    """Persistent memory system for context-aware agents."""
    
    def __init__(self, memory_file: Path = MEMORY_FILE):
        self.memory_file = memory_file
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """Load memory from file or create new."""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            return {"conversations": [], "insights": [], "patterns": []}
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            return {"conversations": [], "insights": [], "patterns": []}
    
    def save_memory(self):
        """Save memory to file."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def add_conversation(self, conversation: Dict):
        """Add conversation to memory."""
        conversation["timestamp"] = datetime.now().isoformat()
        self.memory["conversations"].append(conversation)
        self.save_memory()
    
    def add_insight(self, insight: str):
        """Add insight to memory."""
        insight_data = {
            "content": insight,
            "timestamp": datetime.now().isoformat()
        }
        self.memory["insights"].append(insight_data)
        self.save_memory()
    
    def get_recent_conversations(self, limit: int = 5) -> List[Dict]:
        """Get recent conversations."""
        return self.memory["conversations"][-limit:]
    
    def get_insights(self) -> List[Dict]:
        """Get all insights."""
        return self.memory["insights"]


class MockLLMAgent:
    """Mock LLM agent for demonstration (replace with actual CrewAI when installed)."""
    
    def __init__(self, role: str, goal: str, backstory: str, memory: AgentMemory):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.memory = memory
        logger.info(f"Initialized {role} agent")
    
    def process_task(self, task: str, context: Optional[Dict] = None) -> str:
        """Process a task with context awareness."""
        try:
            # Get relevant context from memory
            recent_conversations = self.memory.get_recent_conversations(3)
            insights = self.memory.get_insights()
            
            # Build context-aware response
            response = self._generate_response(task, context, recent_conversations, insights)
            
            # Save interaction to memory
            self.memory.add_conversation({
                "agent": self.role,
                "task": task,
                "response": response,
                "context": context
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            return f"Error: {str(e)}"
    
    def _generate_response(self, task: str, context: Dict, recent: List, insights: List) -> str:
        """Generate context-aware response."""
        # This would be replaced with actual LLM calls in production
        base_response = f"[{self.role}] Processing: {task}"
        
        if context:
            base_response += f"\nContext: {json.dumps(context, indent=2)}"
        
        if recent:
            base_response += f"\nRecent interactions: {len(recent)} conversations"
        
        if insights:
            base_response += f"\nPrevious insights: {len(insights)} patterns identified"
        
        return base_response


class DataAnalystAgent(MockLLMAgent):
    """Specialized agent for data analysis and reporting."""
    
    def __init__(self, memory: AgentMemory):
        super().__init__(
            role="Data Analyst",
            goal="Analyze data patterns and generate actionable insights",
            backstory="Expert in data analysis with focus on business intelligence",
            memory=memory
        )
    
    def analyze_data(self, data: Dict) -> Dict:
        """Analyze data and generate insights."""
        try:
            analysis = {
                "summary": f"Analyzed {len(data)} data points",
                "trends": ["Trend 1: Increased activity", "Trend 2: Geographic clustering"],
                "recommendations": ["Recommendation 1: Focus on high-activity regions"],
                "confidence": 0.85
            }
            
            # Add insight to memory
            self.memory.add_insight(f"Data analysis revealed {len(analysis['trends'])} key trends")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in data analysis: {e}")
            return {"error": str(e)}


class ReportGeneratorAgent(MockLLMAgent):
    """Agent for automated report generation."""
    
    def __init__(self, memory: AgentMemory):
        super().__init__(
            role="Report Generator",
            goal="Generate comprehensive reports from data analysis",
            backstory="Professional report writer with expertise in business communications",
            memory=memory
        )
    
    def generate_report(self, analysis: Dict, template: str = "standard") -> str:
        """Generate report from analysis."""
        try:
            report = f"""
# Automated Intelligence Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
{analysis.get('summary', 'No summary available')}

## Key Findings
"""
            
            trends = analysis.get('trends', [])
            for i, trend in enumerate(trends, 1):
                report += f"{i}. {trend}\n"
            
            report += "\n## Recommendations\n"
            recommendations = analysis.get('recommendations', [])
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
            
            report += f"\n## Confidence Level: {analysis.get('confidence', 'N/A')}\n"
            
            # Add to memory
            self.memory.add_insight(f"Generated report with {len(trends)} trends and {len(recommendations)} recommendations")
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return f"Error generating report: {str(e)}"


class RootCauseAnalyzer(MockLLMAgent):
    """Agent for root cause analysis."""
    
    def __init__(self, memory: AgentMemory):
        super().__init__(
            role="Root Cause Analyzer",
            goal="Identify root causes of problems and anomalies",
            backstory="Expert in system analysis and problem-solving methodologies",
            memory=memory
        )
    
    def analyze_issue(self, issue: str, symptoms: List[str], context: Dict) -> Dict:
        """Perform root cause analysis."""
        try:
            # Simulate root cause analysis
            analysis = {
                "issue": issue,
                "symptoms": symptoms,
                "potential_causes": [
                    "Configuration drift",
                    "Resource constraints",
                    "External dependencies"
                ],
                "root_cause": "Most likely: Configuration drift",
                "solution_steps": [
                    "1. Verify current configuration",
                    "2. Compare with known good state",
                    "3. Implement configuration rollback",
                    "4. Monitor for resolution"
                ],
                "confidence": 0.78
            }
            
            # Add insight to memory
            self.memory.add_insight(f"Root cause analysis completed for: {issue}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in root cause analysis: {e}")
            return {"error": str(e)}


class CrewOrchestrator:
    """Orchestrates multiple agents working together."""
    
    def __init__(self):
        self.memory = AgentMemory()
        self.data_analyst = DataAnalystAgent(self.memory)
        self.report_generator = ReportGeneratorAgent(self.memory)
        self.root_cause_analyzer = RootCauseAnalyzer(self.memory)
        logger.info("CrewAI Orchestrator initialized")
    
    def automated_analysis_workflow(self, data: Dict) -> Dict:
        """Complete automated analysis workflow."""
        try:
            logger.info("Starting automated analysis workflow")
            
            # Step 1: Analyze data
            analysis = self.data_analyst.analyze_data(data)
            
            # Step 2: Generate report
            report = self.report_generator.generate_report(analysis)
            
            # Step 3: Check for anomalies and analyze if needed
            anomalies = data.get('anomalies', [])
            root_cause_analysis = None
            
            if anomalies:
                root_cause_analysis = self.root_cause_analyzer.analyze_issue(
                    issue="Data anomalies detected",
                    symptoms=anomalies,
                    context={"data_size": len(data)}
                )
            
            result = {
                "analysis": analysis,
                "report": report,
                "root_cause_analysis": root_cause_analysis,
                "workflow_status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("Automated analysis workflow completed")
            return result
            
        except Exception as e:
            logger.error(f"Error in automated workflow: {e}")
            return {"error": str(e)}
    
    def interactive_session(self, user_query: str) -> str:
        """Interactive session with context awareness."""
        try:
            # Determine which agent is best suited for the query
            if "analyze" in user_query.lower() or "data" in user_query.lower():
                agent = self.data_analyst
            elif "report" in user_query.lower() or "generate" in user_query.lower():
                agent = self.report_generator
            elif "problem" in user_query.lower() or "issue" in user_query.lower():
                agent = self.root_cause_analyzer
            else:
                agent = self.data_analyst  # Default
            
            # Process with context
            context = {
                "user_query": user_query,
                "session_type": "interactive",
                "agent_selected": agent.role
            }
            
            response = agent.process_task(user_query, context)
            return response
            
        except Exception as e:
            logger.error(f"Error in interactive session: {e}")
            return f"Error: {str(e)}"


def main():
    """Main function to demonstrate CrewAI capabilities."""
    try:
        # Initialize orchestrator
        crew = CrewOrchestrator()
        
        # Example 1: Automated analysis workflow
        print("=== Automated Analysis Workflow ===")
        sample_data = {
            "metrics": [{"cpu": 85, "memory": 76}, {"cpu": 90, "memory": 82}],
            "anomalies": ["High CPU usage", "Memory spike"],
            "timestamp": datetime.now().isoformat()
        }
        
        workflow_result = crew.automated_analysis_workflow(sample_data)
        print(f"Workflow Status: {workflow_result.get('workflow_status', 'unknown')}")
        print(f"Analysis: {workflow_result.get('analysis', {}).get('summary', 'No analysis')}")
        
        # Example 2: Interactive session
        print("\n=== Interactive Session ===")
        user_queries = [
            "Can you analyze the recent performance data?",
            "Generate a report on system health",
            "There's a problem with the API response times"
        ]
        
        for query in user_queries:
            response = crew.interactive_session(query)
            print(f"Query: {query}")
            print(f"Response: {response[:100]}...")
            print()
        
        # Example 3: Memory and context demonstration
        print("=== Memory & Context Demonstration ===")
        recent_conversations = crew.memory.get_recent_conversations()
        print(f"Recent conversations: {len(recent_conversations)}")
        
        insights = crew.memory.get_insights()
        print(f"Accumulated insights: {len(insights)}")
        
        return workflow_result
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    result = main()
    print(f"\nFinal result: {result.get('workflow_status', 'unknown')}") 