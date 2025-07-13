# CrewAI Agents Module (M8)

**Intelligent Agent Orchestration & Autonomy System**

This module demonstrates advanced AI agent capabilities perfectly aligned with Patrianna's requirements for:
- Agent Orchestration & Autonomy
- Feedback and memory mechanisms
- Context-aware, evolving agents
- Automated report generation
- Root cause analysis

---

## Features

### 🤖 **Multi-Agent System**
- **Data Analyst Agent**: Analyzes data patterns and generates actionable insights
- **Report Generator Agent**: Creates comprehensive reports from analysis
- **Root Cause Analyzer**: Identifies root causes of problems and anomalies
- **CrewOrchestrator**: Coordinates multiple agents working together

### 🧠 **Memory & Context System**
- **Persistent Memory**: Stores conversations, insights, and patterns
- **Context-Aware Responses**: Agents use historical context for better decisions
- **Learning & Evolution**: Agents improve over time through accumulated insights

### 🔄 **Automated Workflows**
- **Automated Analysis Pipeline**: Data → Analysis → Report → Root Cause (if needed)
- **Interactive Sessions**: Context-aware conversations with appropriate agent selection
- **Feedback Loops**: Continuous improvement through memory and insights

---

## Quick Start

```bash
cd modules/m8-crew-agents
python crew_agents.py
```

### Example Output
```
=== Automated Analysis Workflow ===
Workflow Status: completed
Analysis: Analyzed 3 data points

=== Interactive Session ===
Query: Can you analyze the recent performance data?
Response: [Data Analyst] Processing: Can you analyze the recent performance data?...

=== Memory & Context Demonstration ===
Recent conversations: 4
Accumulated insights: 3
```

---

## Architecture

### Agent Classes
```python
class MockLLMAgent:
    """Base agent with memory and context awareness"""
    
class DataAnalystAgent(MockLLMAgent):
    """Specialized for data analysis and insights"""
    
class ReportGeneratorAgent(MockLLMAgent):
    """Automated report generation"""
    
class RootCauseAnalyzer(MockLLMAgent):
    """Problem analysis and solution recommendations"""
```

### Memory System
```python
class AgentMemory:
    """Persistent memory with JSON storage"""
    - conversations: List[Dict]
    - insights: List[Dict]
    - patterns: List[Dict]
```

### Orchestration
```python
class CrewOrchestrator:
    """Coordinates multiple agents"""
    - automated_analysis_workflow()
    - interactive_session()
    - memory management
```

---

## Key Capabilities

### 1. **Automated Analysis Workflow**
```python
crew = CrewOrchestrator()
result = crew.automated_analysis_workflow({
    "metrics": [{"cpu": 85, "memory": 76}],
    "anomalies": ["High CPU usage"]
})
```

### 2. **Interactive Sessions**
```python
response = crew.interactive_session("Analyze the recent performance data")
# Automatically selects appropriate agent based on query
```

### 3. **Memory & Context**
```python
# Agents remember previous conversations
# Context influences future responses
# Insights accumulate over time
```

### 4. **Root Cause Analysis**
```python
analysis = root_cause_analyzer.analyze_issue(
    issue="API response times",
    symptoms=["High latency", "Timeout errors"],
    context={"load": "high"}
)
```

---

## Production Readiness

### Error Handling
- Comprehensive try/catch blocks
- Graceful degradation
- Detailed logging

### Logging
- Structured logging with timestamps
- Debug, info, error levels
- Performance tracking

### Memory Management
- Persistent JSON storage
- Automatic cleanup
- Context window management

---

## Integration Examples

### With M2 API Gateway
```python
# Enhanced API responses with agent insights
@app.post("/analyze")
async def analyze_endpoint(data: Dict):
    crew = CrewOrchestrator()
    result = crew.automated_analysis_workflow(data)
    return result
```

### With M3 Auto-Reporter
```python
# Intelligent report enhancement
def enhanced_report(events):
    crew = CrewOrchestrator()
    analysis = crew.data_analyst.analyze_data(events)
    return crew.report_generator.generate_report(analysis)
```

---

## Patrianna Alignment

### ✅ **Perfect Match for Job Requirements**

| Requirement | Implementation |
|-------------|----------------|
| **Agent Orchestration** | `CrewOrchestrator` class |
| **Feedback Mechanisms** | `AgentMemory` with insights |
| **Context-Aware Agents** | Memory-based context |
| **Automated Report Generation** | `ReportGeneratorAgent` |
| **Root Cause Analysis** | `RootCauseAnalyzer` |
| **Interactive User Agents** | `interactive_session()` |

### 🎯 **Demonstrates Key Skills**
- Multi-agent coordination
- Memory and context management
- Automated workflow orchestration
- Error handling and logging
- Production-ready code structure

---

## Future Enhancements

### Real CrewAI Integration
```python
# Replace MockLLMAgent with actual CrewAI
from crewai import Agent, Task, Crew
```

### Advanced Features
- **Reward tuning**: Agent performance optimization
- **Action planning loops**: Multi-step reasoning
- **Autonomous agent memory**: Self-improving agents
- **Real-time collaboration**: Live agent interaction

---

## Files

| File | Purpose |
|------|---------|
| `crew_agents.py` | Main agent implementation |
| `README.md` | Documentation |
| `requirements.txt` | Dependencies |
| `agent_memory.json` | Persistent memory storage | 