# EchoClash

### Put your startup through an AI investment committee.

**EchoClash** is an AI-powered adversarial pitch simulation and founder improvement platform that lets founders practice against configurable investor personas, identify weaknesses, detect contradictions, improve their pitch, and re-pitch.

> **Pitch live → Get challenged → Diagnose → Rewrite → Edit → Export → Re-pitch**

EchoClash is designed as the **simulation layer between founders and the real capital market**.

---

##  Why EchoClash?

Most pitch-practice tools generate questions or provide generic AI feedback.

EchoClash takes a different approach.

It maintains a structured understanding of:

* Startup claims
* Founder-provided evidence
* Investor objections
* Contradictions
* Risk areas
* Persona-specific evaluation criteria
* Investor belief states
* Unresolved gaps
* Pitch performance across multiple rounds

The same startup can therefore receive **different questions, objections, scores, and verdicts from different investor personas**.

---

## Core Innovation

### A persona is not just a prompt.

Each EchoClash investor persona is treated as a **structured decision-making system**.

A persona can have:

```text
Investment Thesis
       ↓
Evaluation Weights
       ↓
Risk Model
       ↓
Evidence Threshold
       ↓
Question Strategy
       ↓
Objection Escalation
       ↓
Belief State
       ↓
Decision Rules
       ↓
Investment Verdict
```

This allows different personas to reason about the same startup differently.

For example:

**Product-focused investor**

> Strong UX → Positive product assessment

**Finance-focused investor**

> Weak CAC evidence → Negative economics assessment

Both can evaluate the same pitch and arrive at different conclusions.

---

#  Core Features

## 1. Adversarial Pitch Simulation

Enter an immersive AI investment room instead of a traditional chatbot.

The founder can:

* Deliver a complete pitch
* Receive investor questions
* Answer verbally or through text
* Handle multi-turn questioning
* Face follow-up challenges
* End the session for a structured verdict

The pitch phase is intentionally uninterrupted—the panel waits until the pitch is complete before starting Q&A.

---

## 2. AI Investment Panels

Choose the type of committee you want to face.

### 🦈 Commercial Panel

Focused on:

* Revenue
* Customers
* Margins
* Willingness to pay
* Commercial opportunity
* Negotiation

### 📈 VC Investment Committee

Focused on:

* Market size
* Competition
* Moat
* Growth
* Unit economics
* Venture-scale potential

### ⚙️ Founder / Operator Panel

Focused on:

* Product
* Execution
* Distribution
* GTM
* Operations
* Founder-market fit

Each panel contains differentiated investor personas.

---

# 👤 Investor Personas

EchoClash includes differentiated investor archetypes such as:

| Persona                     | Primary Focus                           |
| --------------------------- | --------------------------------------- |
| Market Skeptic              | Market, competition, timing             |
| Economics Auditor           | CAC, LTV, margins, burn                 |
| Moat Investor               | Defensibility and competitive advantage |
| Commercial Investor         | Revenue and willingness to pay          |
| Traction Skeptic            | Customers, retention and growth         |
| Negotiator                  | Valuation and deal structure            |
| Product Operator            | Product and execution                   |
| GTM Operator                | Acquisition and distribution            |
| Founder-Market-Fit Operator | Founder insight and execution           |

Personas use different evaluation weights, evidence requirements, questioning priorities, risk thresholds and decision rules.

---

#  Claim & Evidence Intelligence

EchoClash extracts structured information from founder statements.

Each important claim can contain:

```text
Claim
Category
Numeric Value
Unit
Source
Confidence
Evidence Status
Timestamp
```

Evidence can be classified as:

* `SUPPORTED`
* `PARTIALLY_SUPPORTED`
* `UNSUPPORTED`
* `CONTRADICTED`
* `UNKNOWN`

This prevents the AI from treating every founder statement as established fact.

---

#  Contradiction Detection

EchoClash continuously compares new statements with previously established claims.

It can identify inconsistencies involving:

* CAC
* Revenue
* Customers
* Pricing
* Retention
* Market size
* Growth
* Traction
* Timelines
* Product claims
* Competitive claims

### Example

Founder previously says:

```text
CAC = ₹200
```

Later:

```text
₹20,000 spent acquiring 50 customers
```

EchoClash calculates:

```text
₹20,000 / 50 = ₹400 CAC
```

and flags:

```text
CONTRADICTION DETECTED

Previous CAC: ₹200
Calculated CAC: ₹400
Severity: High
```

The panel can then cross-reference the earlier statement and challenge the founder.

---

#  Two-Phase Pitch Experience

EchoClash separates pitching from questioning.

### Phase 1 — Pitch

The founder delivers the complete pitch without interruptions.

The session supports:

* Microphone input
* Live transcription
* Text fallback
* 3-minute pitch countdown
* "Done Pitching"
* Automatic pitch completion

### Phase 2 — Q&A

The panel asks **one grounded question at a time**.

The founder can:

* Answer naturally
* Stay on the microphone
* Wait for automatic submission after approximately 5 seconds of genuine silence
* Press **Submit Answer** to immediately lock the response

The session timer pauses while the panel is asking or thinking and advances while the founder is answering.

---

#  Structured Belief State

Every investor maintains an evolving belief state.

Core dimensions include:

```text
Problem Severity
Market Attractiveness
Founder Credibility
Differentiation
Defensibility
Distribution
Unit Economics
Scalability
Novelty
Feasibility
```

Each dimension is scored from `0–10`.

A belief update records:

```text
Previous Score
New Score
Trigger
Evidence
Reason
Timestamp
```

So instead of simply saying:

> "Your pitch was good."

EchoClash can explain:

```text
Unit Economics
↓ 9 points

Reason:
CAC contradiction reduced investor confidence.
```

---

#  Investor Memory

EchoClash maintains multiple layers of memory.

### Session Memory

Everything said during the current pitch.

### Startup Memory

Claims, evidence, decisions and pitch versions across sessions.

### Persona Memory

What a specific investor has already challenged, accepted or requested.

This enables the re-pitch experience.

For example:

```text
Round 1
CAC issue identified

        ↓

Founder fixes CAC evidence

        ↓

Round 2

Investor remembers the previous issue
and moves to retention.
```

---

# ⚔️ Objection Escalation

EchoClash doesn't repeatedly ask the same question.

Investor objections can escalate through:

```text
Level 1 → Ask
Level 2 → Challenge
Level 3 → Cross-reference
Level 4 → Consequence
Level 5 → Decision
```

Example:

```text
ASK
What is your CAC?

        ↓

CHALLENGE
Show me how you calculated it.

        ↓

CROSS-REFERENCE
Earlier you said you spent ₹20,000 acquiring 50 customers.

        ↓

CONSEQUENCE
That implies a ₹400 CAC and creates a margin problem.

        ↓

DECISION
Until this is validated, I would not invest.
```

---

# 🏛️ Panel Deliberation

After the pitch, the committee conducts a structured deliberation.

The system generates:

* Final score
* Confidence
* Consensus
* Disagreements
* Strongest dimension
* Weakest dimension
* Investment conditions
* Critical unresolved questions
* Final verdict

Possible verdicts:

```text
Strong Interest
Interest
Conditional Interest
Needs More Evidence
Pass
```

---

# 📊 Pitch Debrief

After the pitch:

> **Pitch Complete**

EchoClash transitions from performance to improvement.

The debrief provides:

### Transcript

* Founder statements
* Investor questions
* Objections
* Follow-ups
* Evidence
* Contradictions
* Decision-changing moments

### Analysis

* Pitch score
* Previous score
* Improvement
* Panel verdict
* Prioritized gaps
* Scorecard
* Recommended actions

---

#  Gap Analysis

Weaknesses are converted into actionable gaps.

Each gap contains:

```text
Gap ID
Category
Severity
Panel Source
Transcript Evidence
Why It Matters
Recommended Action
Required Evidence
Status
```

Priority levels:

```text
P0 → Critical
P1 → Important
P2 → Lower Priority
```

Statuses:

```text
OPEN
IN_PROGRESS
RESOLVED
```

---

#  AI Pitch Rewrite

After identifying weaknesses, founders can select the gaps they want to fix.

Supported pitch lengths:

* 60 seconds
* 90 seconds
* 2 minutes
* 5 minutes
* Custom

The rewrite considers:

```text
Original Pitch
Startup Memory
Panel Objections
Gap Priorities
Recommended Actions
Founder Evidence
Panel Verdict
Target Length
```

### Evidence-Honest AI

EchoClash **never invents**:

* Customers
* Revenue
* Traction
* Statistics
* Partnerships
* Market validation
* Evidence

When information is missing, it uses placeholders such as:

```text
[PLACEHOLDER: insert your customer retention data here]
```

The founder remains the final author.

---

#  Pitch Editor

Generated pitches can be edited before being used again.

Supported sections include:

* Opening
* Problem
* Customer
* Solution
* Market
* Traction
* Business Model
* Differentiation
* Moat
* GTM
* Team
* Ask
* Closing

Features include:

* Direct editing
* AI suggestions
* Accept / reject changes
* Undo / redo
* Section regeneration
* Pitch length selection
* Preview
* Version saving

---

#  Re-Pitch

EchoClash is built around iterative improvement.

Example:

```text
Round 1     61
     ↓
Fix critical gaps
     ↓
Round 2     74
     ↓
Resolve remaining risks
     ↓
Round 3     82
```

Founders can compare:

* Improved dimensions
* Regressions
* New risks
* Resolved gaps
* Persistent gaps
* Previous scores
* New verdicts

---

#  Demo Mode

EchoClash includes a deterministic fictional startup:

## FlowPay

Demo Mode allows the complete product experience to run without external AI credentials.

It demonstrates:

* Live pitching
* Claim extraction
* Follow-up questioning
* Numerical contradiction
* Evidence requests
* Belief updates
* Persona disagreement
* Final verdict
* Debrief
* AI rewrite
* Export

This makes the project suitable for **hackathon demos and offline demonstrations**.

---

#  Architecture

```text
                    ┌─────────────────────┐
                    │      React UI       │
                    │ TypeScript + Tailwind│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌──────────────┐ ┌────────────┐ ┌──────────────┐
        │ Conversation │ │ Structured │ │   Export     │
        │ Orchestrator │ │   State    │ │   Services   │
        └──────┬───────┘ └─────┬──────┘ └──────────────┘
               │               │
               ▼               ▼
        ┌──────────────┐ ┌──────────────┐
        │  AI Provider │ │   Supabase   │
        │ Claude / LLM │ │ PostgreSQL   │
        └──────────────┘ └──────────────┘
```

The architecture keeps AI reasoning separate from canonical structured application state.

---

# 🛠️ Tech Stack

| Layer          | Technology                                   |
| -------------- | -------------------------------------------- |
| Frontend       | React + TypeScript                           |
| Styling        | Tailwind CSS                                 |
| Animation      | Framer Motion                                |
| Backend        | FastAPI + Python                             |
| Database       | Supabase PostgreSQL                          |
| AI             | Claude via configurable server-side provider |
| Speech-to-Text | Browser Web Speech API                       |
| Text-to-Speech | Browser SpeechSynthesis                      |
| PDF Export     | jsPDF                                        |
| DOCX Export    | docx.js                                      |
| Deployment     | Emergent.sh                                  |

The documented implementation uses React/TypeScript, FastAPI, Supabase PostgreSQL, browser speech APIs and client-side PDF/DOCX generation.

---

#  Core Data Model

The application uses structured relational entities including:

```text
users
startups
startup_claims
evidence
panel_configs
panel_personas
pitch_sessions
transcript_messages
belief_states
panel_verdicts
gaps
action_items
pitch_versions
exports
```

These entities preserve the startup's evolving state rather than relying solely on conversation history.

---

#  Safety & Trust

EchoClash is designed to clearly distinguish:

```text
Founder Facts
      ≠
Founder Claims
      ≠
Evidence
      ≠
Panel Opinions
      ≠
AI Inferences
```

The system:

* Clearly labels AI simulations
* Does not imply endorsement by real investors
* Does not clone real investor voices
* Does not generate authentic statements attributed to real people
* Never invents founder evidence
* Keeps AI API credentials server-side
* Allows founders to inspect and edit generated content

---

#  Design Philosophy

EchoClash uses a **cinematic AI investment war-room aesthetic**.

### Visual language

* Near-black backgrounds
* Charcoal surfaces
* Subtle glass effects
* Thin borders
* Premium typography
* Electric violet / indigo accents
* Red for risks and contradictions
* Green for validated evidence
* Restrained gradients
* Purposeful motion

The goal is to make a pitch session feel like entering a **real investment committee**, rather than opening another generic SaaS dashboard.

---

#  Local Development

## Prerequisites

Make sure you have:

* Node.js
* Python 3.10+
* Supabase project
* AI provider credentials if using Live AI Mode

---

## Clone

```bash
git clone https://github.com/<your-username>/echoclash.git
cd echoclash
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Backend

```bash
cd backend

python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn main:app --reload
```

---

#  Environment Variables

Create the required environment files based on your deployment configuration.

Example:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

AI_PROVIDER_API_KEY=your_server_side_api_key

DATABASE_URL=your_database_url
```

**Never commit API keys, database credentials or private secrets to GitHub.**

---

#  Demo Flow

The recommended demonstration flow is:

```text
Landing Page
     ↓
Create / Select Startup
     ↓
Choose Investment Panel
     ↓
Enter Pitch Room
     ↓
Deliver Pitch
     ↓
AI Panel Questions
     ↓
Answer / Submit Answer
     ↓
Contradiction Detection
     ↓
Belief Updates
     ↓
Panel Deliberation
     ↓
Final Verdict
     ↓
Debrief
     ↓
Identify Gaps
     ↓
AI Rewrite
     ↓
Edit Pitch
     ↓
Export
     ↓
Re-Pitch
```

---

#  Current Demo Scenario

The included fictional **FlowPay** scenario demonstrates the core intelligence loop.

Example progression:

```text
Pitch Claim
    ↓
Evidence Analysis
    ↓
Contradiction
    ↓
Investor Challenge
    ↓
Founder Response
    ↓
Belief Update
    ↓
Panel Deliberation
    ↓
Verdict
```

Seeded demo sessions include an initial score of **61 / Needs More Evidence** and an improved session of **74 / Conditional Interest**. All seeded information is intended to be clearly marked as demo data.

---

#  Product Roadmap

### V1 — Core Intelligence

* [x] Adversarial pitch simulation
* [x] Multi-turn questioning
* [x] Structured startup memory
* [x] Claim extraction
* [x] Evidence tracking
* [x] Contradiction detection
* [x] Belief updates
* [x] Panel deliberation
* [x] Gap analysis
* [x] AI rewrite
* [x] Pitch editing
* [x] PDF/DOCX export
* [x] Re-pitch flow
* [x] Demo Mode

### Future

* [ ] Real authentication
* [ ] Persona Studio UI
* [ ] Persona versioning UI
* [ ] Shareable verdict cards
* [ ] Founder experiments
* [ ] Expert marketplace
* [ ] Accelerator discovery
* [ ] Expanded real-time capabilities

The project documentation explicitly prioritizes the core simulation and improvement loop over secondary marketplace/CRM-style functionality.

---

#  What Makes EchoClash Different?

| Traditional Pitch Practice    | EchoClash                         |
| ----------------------------- | --------------------------------- |
| Generic AI questions          | Persona-specific questioning      |
| Stateless conversation        | Persistent startup memory         |
| Feedback after pitch          | Continuous belief updates         |
| No evidence model             | Claim + evidence intelligence     |
| Manual contradiction spotting | Automated contradiction detection |
| One generic score             | Multi-dimensional belief state    |
| Static investor persona       | Structured decision system        |
| Practice once                 | Diagnose → fix → re-pitch         |
| AI-generated pitch            | Evidence-aware rewrite            |

---

# 🎯 Target Users

EchoClash is designed for:

* Early-stage startup founders
* Student founders
* Startup teams
* Accelerator cohorts
* Incubators
* Pitch competition participants
* Founders without access to regular investor feedback

---

#  Product Vision

> **The best pitch practice isn't practicing the same pitch again.**
>
> **It's discovering exactly where your startup breaks—and fixing it before an investor does.**

EchoClash aims to become the **simulation layer between founders and the real capital market**.

---

#  Disclaimer

EchoClash is an AI simulation platform.

It is **not affiliated with, endorsed by, or representative of any real investor, venture capital firm, television program, or investment committee**.

Investor personas are fictional simulations designed for pitch practice.

---

#  License
```
MIT License
```

---

**EchoClash — Don't just practice your pitch. Stress test it.**
