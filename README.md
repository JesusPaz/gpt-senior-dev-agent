# 🧠 GPT understands your repo like a senior dev – CodeRAG-inspired pipeline

This project builds an end-to-end **code understanding system** that enables GPT-like models to deeply comprehend your codebase — with zero fine-tuning.

Inspired by [CodeRAG (2025)](https://arxiv.org/abs/2504.10046), the goal is to extract structure, semantics, and relationships from your repo and use them to build a smarter, retrieval-augmented code assistant.

---

## 🚀 What this repo does

We implement the following pipeline:

1. **Parse code structure** with [Tree-sitter](https://tree-sitter.github.io/)
2. **Extract all functions and classes** (with file paths and line ranges)
3. **Collect or generate descriptions** ("requirements") for each element  
   - We assume the repo already includes proper docstrings
4. **Build a Requirement Graph**
   - Nodes: descriptions of functions/classes
   - Edges: semantic similarity or parent-child relationship
5. **Build a DS-Code Graph**
   - Nodes: actual code elements (functions, classes, modules)
   - Edges: `calls`, `imports`, `contains`, `inherits`, `similar_to`
6. **Map the two graphs together** (bi-graph)
7. **Enable agentic reasoning**
   - Let GPT traverse the graph, ask subquestions, and retrieve relevant context
8. **Answer deep code questions** with full source-aware context (RAG-style)

---

## 🧰 Tech Stack

| Component         | Tool / Library                        |
|------------------|----------------------------------------|
| Parsing           | `tree-sitter-language-pack`            |
| Semantic Similarity | OpenAI / HuggingFace embeddings     |
| Graph DB (optional) | Neo4j                               |
| Reasoning Agent   | ReAct / LangChain (optional)          |
| Code Validation   | `black`, `pytest`, `mypy`             |
| UI (optional)     | Streamlit or Next.js                  |

---

## 🗂️ Repository structure

.
├── code_structure_graph_builder.ipynb     # Main notebook (Tree-sitter + graph building)
├── code_elements.json                     # Extracted functions and classes
├── code_elements_with_requirements.json   # (Optional) With docstrings or LLM descriptions
├── README.md

---

## 📋 Requirements

Install dependencies:

```bash
pip install tree-sitter-language-pack pandas

If using semantic search or agentic reasoning later, you may also need:

pip install openai sentence-transformers neo4j langchain


⸻

📍 Assumptions
	•	Your Python code already contains good docstrings
→ If not, you can generate them using GPT or DeepSeek via a prompt
	•	The goal is structure + meaning + connections, not just vector search

⸻

📈 Inspired by
	•	CodeRAG: Supportive Code Retrieval on Bigraph for Real-World Code Generation
	•	Self-RAG (Asai et al., 2023)
	•	DRAGIN: Dynamic RAG (2024)
	•	CoRAG: Chain-of-Retrieval for RAG (2025)

⸻

🧪 Try it

Open the notebook and run each cell.
Your output will include a full JSON map of your codebase, ready to power smarter retrieval and reasoning systems.

⸻

💬 Questions?

Open an issue or ping @jesuspaz on GitHub.
