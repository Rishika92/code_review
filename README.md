# Code Review Agent (OpenEnv)

##  Overview

This project implements an AI-driven code review environment where an agent analyzes code and identifies issues such as:

- Security vulnerabilities  
- Logical bugs  
- Performance inefficiencies  

The system follows the OpenEnv framework and simulates real-world developer workflows.

---

##  Architecture

Dataset → Agent → Action → Evaluation → Output

### Components:

- Dataset: Easy, Medium, Hard samples  
- Agent: Rule-based analyzer  
- Inference: Runs agent on tasks  
- Deployment: FastAPI + Docker  

---

## Approach

We built a rule-based static analysis agent with context-aware detection to reduce false positives and improve accuracy.

### Techniques:

- Pattern detection (eval, range(len), etc.)  
- Context filtering  
- Multi-issue detection  

---

##  Features

###  Security

- eval() detection  
- SQL injection patterns  
- Hardcoded passwords  

### Bugs

- Bare except  
- Missing validation  
- Silent failure  
- Type mismatch  

### Optimization

- Nested loops  
- Inefficient iteration  
- List comprehension suggestions  

---

##  Dataset

| Level  | Description           |
|--------|----------------------|
| Easy   | Basic patterns       |
| Medium | Logical issues       |
| Hard   | Security + complexity |

---

##  Observation Space

The agent receives:

- `code`: source code snippet  
- `language`: programming language  
- `context`: optional metadata  

---

##  Action Space

The agent outputs:

- `type`: issue category (security, bug, optimization)  
- `line`: line number of issue  
- `message`: description of issue  

---

##  Reward Function

Reward is computed by comparing predicted issues with expected issues:

- Matching criteria: **type + line**
- Score range: **0.0 to 1.0**
- Final score: average across all tasks  

---

##  Run

```bash
python inference.py
