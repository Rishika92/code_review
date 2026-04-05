# 🧠 Code Review Agent (OpenEnv)

## 🚀 Overview

This project implements an AI-driven code review environment where an agent analyzes code and identifies issues such as:

* Security vulnerabilities
* Logical bugs
* Performance inefficiencies

The system follows the OpenEnv framework and simulates real-world developer workflows.

---

## 🏗️ Architecture

Dataset → Agent → Action → Evaluation → Output

### Components:

* Dataset: Easy, Medium, Hard samples
* Agent: Rule-based analyzer
* Inference: Runs agent on tasks
* Deployment: FastAPI + Docker

---

## 🧠 Approach

We built a rule-based static analysis agent with context-aware detection to reduce false positives and improve accuracy.

### Techniques:

* Pattern detection (eval, range(len), etc.)
* Context filtering
* Multi-issue detection

---

## 🔍 Features

### 🔐 Security

* eval() detection
* SQL injection patterns
* Hardcoded passwords

### 🐞 Bugs

* Bare except
* Missing validation
* Silent failure
* Type mismatch

### ⚡ Optimization

* Nested loops
* Inefficient iteration
* List comprehension suggestions

---

## 📊 Dataset

| Level  | Description           |
| ------ | --------------------- |
| Easy   | Basic patterns        |
| Medium | Logical issues        |
| Hard   | Security + complexity |

---

## 🧪 Run

python inference.py

---

## 📈 Results

* Easy: ~90%+
* Medium: ~85–95%
* Hard: ~70–85%

---

## 🐳 Docker

docker build -t code-review .
docker run -p 7860:7860 code-review

---

## 🌐 API

* `/` → health check
* `/run` → run agent

---

## 🧩 Structure

code_review/
├── agent/
├── data/
├── scripts/
├── app/
├── inference.py
├── Dockerfile
├── README.md

---

## ⚠️ Limitations

* Rule-based system
* Limited patterns

---

## 🔮 Future Work

* LLM integration
* Multi-language support

---

## 👥 Team

* Dev A → Environment + Reward
* Dev B → Agent + Dataset + Deployment

---

## 🏁 Conclusion

A structured code review system with strong detection and low false positives.
