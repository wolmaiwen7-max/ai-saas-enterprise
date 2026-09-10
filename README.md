# AI SaaS Enterprise

A five-agent executive team built with [CrewAI](https://github.com/crewAIInc/crewAI) using the hierarchical process.

| Agent | Role |
|---|---|
| Chief of Staff | Manager. Delegates work, reviews output, writes the unified plan |
| CTO | Architecture, stack, security, engineering roadmap |
| CMO | Positioning, ICP, pricing, demand generation |
| CRO | Go-to-market motion, sales process, revenue targets |
| CCO | Regulations, policies, certifications, risk register |

## Setup

On Windows-on-ARM machines, create the venv with an x64 Python build. Some dependencies have no ARM64 wheels.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
copy .env.example .env        # then add your ANTHROPIC_API_KEY
```

## Run

```bash
python main.py "Your SaaS product idea"
```

The final operating plan is printed to the console and saved to `output/operating_plan.md`.
