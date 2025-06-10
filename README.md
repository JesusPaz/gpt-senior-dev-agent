# 🧠 GPT understands your repo like a senior dev — CodeRAG-inspired pipeline

This project builds an end-to-end **code-understanding system** that lets a GPT-style model grasp your whole codebase *without* fine-tuning.

Inspired by **[CodeRAG (2025)](https://arxiv.org/abs/2504.10046)**, we extract structure, semantics, and connections from your repo and feed them back to the model via retrieval-augmented generation (RAG).

---

## 🚀 Pipeline at a glance

| Step | What we do | Output |
|------|------------|--------|
| 1 | **Parse** code with Tree-sitter | AST for every `.py` file |
| 2 | **Extract** every function / class (file path + line range) | `code_elements.json` |
| 3 | **Collect descriptions**   (docstrings or LLM-generated) | each element now has a natural-language “requirement” |
| 4 | **Build Requirement Graph (RG)** | nodes = requirements <br>edges = Similarity / Parent–Child |
| 5 | **Build DS-Code Graph (CG)** | nodes = real code <br>edges = calls, imports, contain, inherit, similar |
| 6 | **Map RG ↔ CG** (Bigraph) | 1-to-1 ID map links each description to its code |
| 7 | **Agentic reasoning** (ReAct) | LLM walks the graphs + web search + code test |
| 8 | **Answer deep questions** with full, source-aware context |

---

## 🔍 Two graphs — explained simply

| Graph | Nodes | Main edges | How edges are created |
|-------|-------|------------|-----------------------|
| **Requirement Graph (RG)** | Short descriptions (docstrings) | **Parent-Child** (A calls B) <br>**Similar_to** (cos ≥ 0.8 via embeddings) | • Static call analysis<br>• Sentence embeddings |
| **DS-Code Graph (CG)** | Code objects (module / class / function) | **call**, **import**, **inherit**, **contain** (AST) <br>**similarity** (code-embedding) | • Tree-sitter AST<br>• Code embeddings |

**Mapping layer**

```

"Serialize JSON"  (RG-id-42)  ─────▶  to\_json()   (CG-id-42)

````

Once the LLM finds similar or child *requirements* in RG it can **jump** to the real code anchors in CG, follow structural edges, pull more context, and come back.

---

### Tiny toy example

```text
# code.py
def to_json(obj):
    """Serialize object to JSON"""
    return json.dumps(obj)

def dict_to_json(d):          # calls to_json()
    """Convert dict to JSON string"""
    return to_json(d)
````

*Requirement Graph*

```
R1 "Serialize object to JSON"
R2 "Convert dict to JSON string"

edges:
R1 —parent→ R2        (because dict_to_json calls to_json)
R1 —similar→ R2       (embedding similarity ≈ 0.87)
```

*DS-Code Graph*

```
C1 to_json()
C2 dict_to_json()

edges:
C2 —call→ C1
```

*Bigraph map*

```
R1 ▶ C1
R2 ▶ C2
```

The agent can now reason:

1. Start with user query → find R1.
2. Hop to C1, inspect code, see who calls it (C2).
3. Hop back to R2 for more semantic hints, etc.

---

## 🧰 Tech Stack

| Component           | Tool / Library                               |
| ------------------- | -------------------------------------------- |
| Parsing             | `tree-sitter-language-pack`                  |
| Semantic similarity | OpenAI / HuggingFace `sentence-transformers` |
| Graph DB (optional) | Neo4j                                        |
| Reasoning agent     | ReAct / LangChain                            |
| Code validation     | `black`, `pytest`, `mypy`                    |
| UI (optional)       | Streamlit • Next.js                          |

---

## 🗂️ Repo layout

```
.
├── code_structure_graph_builder.ipynb   # Main notebook (parsing + graphs)
├── code_elements.json                   # Raw functions/classes
├── code_elements_with_requirements.json # Same, but with docstrings / LLM summaries
└── README.md
```

---

## 📋 Requirements

```bash
pip install tree-sitter-language-pack pandas
# extras for embeddings / graphs / agent
pip install openai sentence-transformers neo4j langchain
```

> **Assumptions**
> • Your Python code already includes decent docstrings.
> • If not, you can auto-generate them with GPT/DeepSeek.

---

## 🧪 Quick start

1. Open `code_structure_graph_builder.ipynb`.
2. Run every cell – you’ll get a JSON map of your code plus two graphs ready for experiments.

---

## 🙋‍♂️ Questions & feedback

Open an issue or ping **@jesuspaz** on GitHub. Happy hacking!

```
