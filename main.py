"""
AI SaaS Enterprise - a 5-agent corporate structure built on CrewAI.

Hierarchical process:
    Chief of Staff (manager) delegates to and reviews the work of
    the CTO, CMO, CRO, and CCO, then synthesizes a final plan.

Usage:
    export ANTHROPIC_API_KEY=...     # or put it in a .env file
    python main.py "Your SaaS product idea"
"""

import os
import sys

from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("CREW_MODEL", "anthropic/claude-opus-5")

# Single shared LLM. The manager gets more headroom for synthesis.
llm = LLM(model=MODEL, max_tokens=8000, temperature=0.4)
manager_llm = LLM(model=MODEL, max_tokens=16000, temperature=0.3)


# --------------------------------------------------------------------------- #
# Agents
# --------------------------------------------------------------------------- #

chief_of_staff = Agent(
    role="Chief of Staff",
    goal=(
        "Run the executive team. Break the company mandate into clear "
        "workstreams, delegate each to the right executive, review their "
        "output for quality and consistency, and produce one unified plan."
    ),
    backstory=(
        "You are the CEO's right hand at a fast-growing B2B SaaS company. "
        "You are decisive, allergic to vague answers, and you push each "
        "executive for concrete numbers, owners, and timelines."
    ),
    llm=manager_llm,
    allow_delegation=True,
    verbose=True,
)

cto = Agent(
    role="Chief Technology Officer (CTO)",
    goal=(
        "Define the technical architecture, build-vs-buy decisions, "
        "security posture, and engineering roadmap for the product."
    ),
    backstory=(
        "You have shipped multi-tenant SaaS platforms at scale. You favor "
        "boring, proven technology, strong observability, and SOC 2 "
        "readiness from day one."
    ),
    llm=llm,
    allow_delegation=False,
    verbose=True,
)

cmo = Agent(
    role="Chief Marketing Officer (CMO)",
    goal=(
        "Own positioning, ideal customer profile, messaging, pricing "
        "packaging, and the demand-generation plan."
    ),
    backstory=(
        "You built the marketing engine for two product-led SaaS companies. "
        "You think in funnels, CAC payback, and clear category narratives."
    ),
    llm=llm,
    allow_delegation=False,
    verbose=True,
)

cro = Agent(
    role="Chief Revenue Officer (CRO)",
    goal=(
        "Design the go-to-market motion, sales process, pipeline targets, "
        "quota model, and revenue forecast."
    ),
    backstory=(
        "You have taken SaaS companies from first dollar to $50M ARR. You "
        "obsess over sales cycle length, win rates, and net revenue retention."
    ),
    llm=llm,
    allow_delegation=False,
    verbose=True,
)

cco = Agent(
    role="Chief Compliance Officer (CCO)",
    goal=(
        "Identify legal, privacy, security, and regulatory obligations and "
        "turn them into a practical compliance roadmap."
    ),
    backstory=(
        "You have led compliance programs covering GDPR, CCPA, SOC 2, and "
        "ISO 27001 for cloud software vendors. You flag risks early and "
        "propose pragmatic controls rather than blockers."
    ),
    llm=llm,
    allow_delegation=False,
    verbose=True,
)


# --------------------------------------------------------------------------- #
# Tasks
# --------------------------------------------------------------------------- #

def build_tasks(product_idea: str) -> list[Task]:
    context = f"Company mandate: {product_idea}"

    technical_plan = Task(
        description=(
            f"{context}\n\n"
            "Produce the technical plan: system architecture, core stack, "
            "multi-tenancy and data model approach, security controls, "
            "hosting and cost estimate, and a 90-day engineering roadmap."
        ),
        expected_output=(
            "A structured technical plan with an architecture overview, "
            "stack choices with rationale, security controls, and a "
            "milestone-based 90-day roadmap."
        ),
        agent=cto,
    )

    marketing_plan = Task(
        description=(
            f"{context}\n\n"
            "Produce the marketing plan: ideal customer profile, positioning "
            "statement, three core messages, pricing tiers, and a launch "
            "demand-generation plan with channels and KPIs."
        ),
        expected_output=(
            "A marketing plan covering ICP, positioning, messaging, pricing "
            "packaging, launch channels, and measurable KPIs."
        ),
        agent=cmo,
    )

    revenue_plan = Task(
        description=(
            f"{context}\n\n"
            "Produce the revenue plan: go-to-market motion (self-serve, "
            "sales-led, or hybrid), sales process stages, first-year "
            "pipeline and ARR targets, hiring plan, and key sales metrics."
        ),
        expected_output=(
            "A revenue plan with GTM motion, sales stages, year-one ARR "
            "targets with assumptions, sales hiring plan, and metrics."
        ),
        agent=cro,
        context=[marketing_plan],
    )

    compliance_plan = Task(
        description=(
            f"{context}\n\n"
            "Produce the compliance plan: applicable regulations, data "
            "handling requirements, required policies and contracts, "
            "certification roadmap, and top risks with mitigations."
        ),
        expected_output=(
            "A compliance roadmap listing regulations, required policies, "
            "certifications with target dates, and a risk register."
        ),
        agent=cco,
        context=[technical_plan],
    )

    executive_summary = Task(
        description=(
            f"{context}\n\n"
            "Review every executive's plan for gaps and conflicts. Resolve "
            "inconsistencies, then write the unified company operating plan "
            "for the leadership team with owners and a quarter-by-quarter "
            "timeline."
        ),
        expected_output=(
            "A unified operating plan in Markdown with an executive summary, "
            "one section per function, a cross-functional timeline, and a "
            "list of open decisions for the CEO."
        ),
        agent=chief_of_staff,
        context=[technical_plan, marketing_plan, revenue_plan, compliance_plan],
        output_file="output/operating_plan.md",
    )

    return [
        technical_plan,
        marketing_plan,
        revenue_plan,
        compliance_plan,
        executive_summary,
    ]


# --------------------------------------------------------------------------- #
# Crew
# --------------------------------------------------------------------------- #

def build_crew(product_idea: str) -> Crew:
    return Crew(
        agents=[cto, cmo, cro, cco],
        tasks=build_tasks(product_idea),
        process=Process.hierarchical,
        manager_agent=chief_of_staff,
        verbose=True,
    )


def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set. Add it to your environment or a .env file.")

    product_idea = " ".join(sys.argv[1:]).strip() or (
        "An AI-powered contract review platform for mid-market legal teams, "
        "sold as a per-seat SaaS subscription."
    )

    os.makedirs("output", exist_ok=True)
    result = build_crew(product_idea).kickoff()

    print("\n" + "=" * 80)
    print("FINAL OPERATING PLAN")
    print("=" * 80)
    print(result)


if __name__ == "__main__":
    main()
