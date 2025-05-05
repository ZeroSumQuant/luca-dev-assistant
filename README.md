# LUCA · Developer Assistant

*A plug‑and‑play agent‑orchestrator that turns any QuantConnect user into an effective quantitative engineer.* ✨🧠📈

---

## Mission

Empower traders, data scientists, and makers to build, test, and ship production‑grade code through **one conversational agent**. LUCA excels at Lean and QuantConnect Cloud, yet can just as easily scaffold Streamlit dashboards, FastAPI services, or pure‑Python data jobs. 🚀📊💻

---

## Key Features

| Feature                    | Description                                                                                                          |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| QuantConnect‑native brain  | Ships with Lean API docs and QC company context embedded for instant recall.                                         |
| Multi‑domain "packs"       | Plug‑in modules (`qc`, `web`, `data`, …) let LUCA swap toolsets based on your prompt.                                |
| Strategy & project planner | Translates plain requests (“Design an MNQ scalper” / “Spin up a Streamlit dashboard”) into step‑by‑step agent plans. |
| Teacher‑first UX           | Explains *why* as well as *what*; walks new devs through Git, LinkedIn, or Cloud deploys.                            |
| Safe local execution       | Runs unit tests and linting inside Docker before touching your repo.                                                 |
| QC Cloud back‑testing      | All strategy back‑tests execute on QuantConnect Cloud; LUCA streams results back to you.                             |
| Out‑of‑the‑box RAG         | Chroma DB + LightRAG + Graffiti pre‑wired—no extra setup.                                                            |
| Autogen orchestration      | Manages specialist agents (coder, tester, doc‑writer) and signs off only when checks pass. 🛠️🔍✅                    |

---

## Typical Workflow

| Step | What Happens                                                                                         |
| ---- | ---------------------------------------------------------------------------------------------------- |
| 1    | **Install LUCA**.                                                                                    |
| 2    | **Ask** → “LUCA, build an MNQ futures strategy.” or “LUCA, scaffold a Streamlit dashboard.”          |
| 3    | LUCA drafts a plan and dispatches agent jobs.                                                        |
| 4    | Code is generated, unit‑tested, lint‑clean, and committed.                                           |
| 5    | If it’s a trading strategy, LUCA triggers a Lean Cloud back‑test and streams stats to the dashboard. |
| 6    | Iterate; then deploy or go live. 🔄📤📊                                                              |

---

## Quick Start

### 1 · Install

```bash
pip install lucalab
```

### 2 · Set your model key (OpenAI, Claude, or local MCP endpoint)

```bash
export OPENAI_API_KEY="sk-..."
```

### 3 · Launch LUCA

```bash
luca
```

> LUCA detects missing config, boots a project scaffold, and opens the dashboard at `http://localhost:8501`. ⚙️📂🌐

---

## Inputs

| Required              | Notes                                                                     |
| --------------------- | ------------------------------------------------------------------------- |
| API key               | Any OpenAI‑compatible endpoint; Claude or local models via MCP also work. |
| Optional pack install | `pip install lucalab[web]` adds web‑dev helpers. 🗝️📦🔌                  |

---

## Outputs

| Output           | Example                                              |
| ---------------- | ---------------------------------------------------- |
| Git commits      | `feat(strategy): add MNQ momentum model`             |
| QC Cloud reports | JSON & equity curve image                            |
| Web builds       | Streamlit or FastAPI app scaffold                    |
| Guidance notes   | Stepwise instructions and best‑practice tips. 📈📝📬 |

---

## Super‑powers at a Glance

| Capability          | Engine                                           |
| ------------------- | ------------------------------------------------ |
| Code read/write     | AutoGen.FileTool + Docker sandbox                |
| Secure exec         | Pytest + custom runner with resource caps        |
| Data access         | QuantConnect APIs; optional local CSV/SQL mounts |
| Knowledge retrieval | Chroma DB + LightRAG + Graffiti 🔍🧠📚           |

---

## Guardrails

| Rule                        | Rationale                                              |
| --------------------------- | ------------------------------------------------------ |
| Never reads raw keys        | Keys stay in your env; LUCA pipes without logging.     |
| Never deletes data silently | Destructive ops require `--force` or Y/N confirm.      |
| Never commits red tests     | Build & unit tests must pass before `git push`. ⛔🛡️✔️ |

---

## Contributing

Pull requests welcome—run `make test && make lint` first. 🤝🔧📤

---

## License

MIT 📜✅⚖️
