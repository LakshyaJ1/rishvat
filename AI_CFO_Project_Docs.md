```
================================================================================
AI CFO — PROJECT DOCUMENTATION
Internal Build Document v1.0
Team Size: 3 | Timeline: ~17 Weeks
================================================================================

-------------------------------------------------------------------------------TABLE OF CONTENTS
-------------------------------------------------------------------------------
1. Product Overview & Vision
2. Problem Being Solved
3. Target Users
4. Core Value Proposition
5. Full Feature Set
6. Technical Architecture
7. Tech Stack
8. Privacy & Security Model
9. Team Roles & Responsibilities
10. Build Stages (Stage 1 through Stage 4)
11. Integration Roadmap
12. Open Questions to Resolve
13. Key Rules for the Team

================================================================================
1. PRODUCT OVERVIEW & VISION
================================================================================

Product Name : AI CFO (working title)
Type     : B2B SaaS
Stage     : Pre-build / Foundation
Team     : 3 people (Person 1, Person 2, Person 3)

AI CFO is an AI-native financial operating system built for early-stage startups
that cannot afford a full-time Chief Financial Officer. It ingests a startup's
financial data from existing tools (Stripe, Plaid, QuickBooks, Xero, Razorpay),
runs an AI reasoning layer over that data, and gives founders CFO-grade insights
on demand — burn rate, runway, MRR, anomaly detection, compliance alerts, and
dynamic pricing recommendations.

The system is designed around three non-negotiable principles:

(a) Privacy-first: No sensitive financial data ever touches a public LLM API.
All AI inference runs on locally-deployed open-source models via Ollama.

(b) Human-in-the-loop: The AI advises by default. It only executes actions
autonomously when the founder explicitly configures it to do so, and only
within hard guardrails they set.

(c) Full auditability: Every recommendation the AI makes, every action it
takes, and every data point it used is logged immutably. The system is
designed to be investor-ready and auditor-ready from day one.

The product integrates a dynamic pricing intelligence engine directly into the
CFO layer — so the same system that monitors burn rate can also recommend when
and how to raise prices, run A/B pricing experiments, and optimize revenue.

================================================================================
2. PROBLEM BEING SOLVED
================================================================================

```

```
Early-stage startups (pre-seed through Series A) face a specific and painful
gap:

- They have real financial complexity: burn, runway, compliance obligations,
multiple revenue streams, vendor contracts, investor reporting.

- They cannot afford a full-time CFO, which costs $150,000–$300,000/year
(or Rs 30–50 lakh/year in India).

- Founders manage finances in spreadsheets, miss compliance deadlines, make
pricing decisions based on gut feel, and produce investor reports manually
at the end of every quarter — burning hours they should spend on product.

- Existing tools (QuickBooks, Xero) are bookkeeping tools, not intelligence
tools. They record what happened. They do not tell you what to do next.

- AI tools like ChatGPT cannot be used with real financial data due to privacy
and data residency concerns.

The result: founders fly blind financially until they hire someone, by which
point they have already made expensive mistakes.

AI CFO closes this gap. It gives a founder CFO-level intelligence from day one,
without a hire, without data leaving their environment, and without requiring
any financial expertise to operate.

================================================================================
3. TARGET USERS
================================================================================

PRIMARY USER
Founders at pre-seed, seed, and early Series A startups managing their own
finances. No finance hire yet. Overwhelmed by compliance and financial ops
while trying to build the product. Need answers fast without having to become
a financial expert.

SECONDARY USER
First finance hire at a startup — a part-time CFO, finance manager, or Head
of Finance who needs AI leverage to do the work of a full team. Uses the
platform to automate reporting, monitor anomalies, and get to decisions
faster.

TARGET COMPANY PROFILE
- Stage     : Pre-seed to Series A
- Revenue    : $0 to $5M ARR
- Team size   : 2 to 50 people
- Business model : SaaS, D2C, Agency, Marketplace
- Geography   : Global (India and US as primary launch markets)

SECONDARY SEGMENTS (future)
- D2C / E-commerce brands needing margin and CAC intelligence
- Agencies needing retainer transition modeling and client LTV ranking
- Series B+ companies needing entity consolidation and board deck automation

================================================================================
4. CORE VALUE PROPOSITION
================================================================================

-> CFO-grade financial intelligence without hiring one
(saves Rs 30–50 lakh/year for Indian startups; $150K+/year globally)

-> Privacy-first architecture: financial data never hits a public API

```

```
(unlike feeding data into ChatGPT or other cloud LLMs)

-> Configurable autonomy: AI advises by default, executes only when permitted
(founder stays in control at all times)

-> Immutable audit trail for every AI recommendation
(investor-ready and auditor-ready from day one)

-> Dynamic pricing engine built into the CFO layer
(not a separate tool — revenue optimization is part of financial health)

-> Proactive intelligence: the system surfaces problems before the founder
asks
(anomaly alerts, compliance calendar, runway warnings)

================================================================================
5. FULL FEATURE SET
================================================================================

--- FINANCIAL INTELLIGENCE CORE --
Financial Health Dashboard
- Live runway counter (cash / monthly burn), updated daily
- Burn rate card with month-over-month delta
- MRR and ARR with 6-month sparkline
- Cash position across all connected bank accounts
- Gross margin, CAC, LTV, NRR computed automatically

Natural Language Q&A
- Chat interface where founders ask financial questions in plain English
- Answers are sourced: every response shows which documents and data
points were used to produce it
- Examples: "What is our runway if we hire two engineers next month?"
"Which customer segment has the lowest churn?"
"Are we on track for our Q3 revenue target?"

Anomaly Detection
- Daily scan of all transactions for unusual patterns
- Flags: expense spikes, revenue drops, missed receivables, duplicate
charges
- Alerts surfaced in the notification panel and optionally via email

Scenario Modeling (What-If Engine)
- Founder inputs a change: hire N people, raise prices by X%, lose Y
customers
- System projects 3, 6, 12-month impact on runway and MRR
- Uses Monte Carlo simulation (1000 samples) to produce confidence intervals
- Output: optimistic, base, and pessimistic runway curves on a single chart

--- COMPLIANCE & REGULATORY --
Compliance Calendar
- Jurisdiction-specific filing deadlines loaded at onboarding
- India: GST quarterly filings, advance tax dates, TDS deadlines
- US: estimated tax dates, sales tax deadlines by state
- EU: VAT return dates, OSS filing
- Alerts at 30, 14, and 7 days before each deadline

Regulatory Guardrails
- Rules engine (deterministic code, not AI) validates every AI output
- Blocks recommendations that violate GAAP, FEMA, GST rules, or other
jurisdiction-specific regulations
- Flags gray-area recommendations for CA/lawyer review instead of blocking

```

```
Expense Categorization
- Every transaction automatically categorized into standard buckets:
payroll, infrastructure, marketing, legal, R&D, G&A
- Lightweight ML classifier (not the full LLM — fast and cheap)
- Categories are editable; corrections feed back as training signal

--- PRICING INTELLIGENCE ENGINE --
Willingness-to-Pay Analysis
- Uses Stripe cohort data to estimate price sensitivity by customer segment
- Low churn at current price = low sensitivity = safe to test higher price
- High churn at plan transition = pricing gap exists

Pricing Tier Gap Detection
- Identifies if customers are bunching at the top of a tier
- Signals they would pay for a higher tier if it existed

A/B Pricing Experiment Engine
- Create a pricing test: new price applies to new customers, existing are
grandfathered
- System monitors conversion and churn impact and reports outcome
- In autopilot mode, can execute the price change directly in Stripe
within founder-configured limits

Competitive Pricing Radar
- Monitors competitor pricing pages for changes
- Alerts founder when a competitor changes pricing with a side-by-side
analysis of how it affects your relative positioning

--- INVESTOR & BOARD LAYER --
Investor MIS Report Generator
- One-click generation of a monthly investor update
- Sections: Executive Summary, MRR and Revenue, Burn and Runway,
Key Metrics vs Last Quarter, Risks and Mitigations, Outlook
- AI writes the narrative sections using real data with citations
- Founder reviews and edits before export to PDF

Board Deck Data Package
- Structured JSON of all key metrics formatted for slide deck creation
- Not slide generation — a clean data package the founder uses to fill
their own template in minutes instead of hours

Benchmarking Engine
- Anonymized aggregate metrics across opt-in tenants
- Shows founder their percentile rank on: burn multiple, NRR, CAC payback,
gross margin vs. peers at same stage and sector
- Updates monthly

Fundraising Readiness Score
- Computed from: runway > 12 months, MoM growth > 10%, NRR > 100%,
complete financial documentation, clean audit trail
- Each criterion shown with pass/fail and specific action to improve it

--- VENDOR & COST INTELLIGENCE --
SaaS Spend Tracker
- Scans transactions for recurring charges to known SaaS vendors
- Groups by vendor, computes monthly cost, tracks trend
- Flags vendors with duplicate functionality or low usage signals

Vendor ROI Scoring
- If product analytics are connected, maps tool usage to cost

```

```
- Surfaces: "You are paying $X/month for Tool Y but usage dropped 80%
in the last 60 days"

Cost Optimization Recommendations
- Ranked list of cost cuts by runway extension impact
- Distinguishes between quick wins (cancel unused subscriptions) and
structural changes (consolidate overlapping tools)

--- AUTOPILOT & CONTROL --
Three-Tier Autonomy Model (configurable per action category)
- Advisory  : AI recommends, founder does everything manually (default)
- Semi-auto : AI executes pre-approved routine actions without asking;
escalates anything new
- Full auto : AI executes within founder-configured guardrails;
founder reviews a daily digest

Guardrails Configuration
- Max autonomous payment amount
- Revenue floor below which pricing changes are blocked
- Categories locked from autopilot (e.g., payments always require approval)
- Notification preferences (email, in-app, digest frequency)

Approvals Inbox
- All actions requiring founder sign-off appear here
- Each item shows: what the AI wants to do, why, what data triggered it,
expected outcome, and what happens if declined
- Approve / Reject with one click; rejection requires a reason

Daily Digest
- Summary email of all autonomous actions taken in the last 24 hours
- Each action: what ran, what outcome resulted, any exceptions

Reversibility Rule
- Any action that cannot be undone (wire transfer, price increase to
existing customers) is escalated to founder regardless of autopilot level
- Only reversible actions (categorization, draft generation, alert sending)
run fully autonomously

--- DOCUMENT INTELLIGENCE --
Document Vault
- Upload financial statements, past audits, invoices, contracts, cap table
- AI has access to all documents in the vault as its knowledge base
- Founder can toggle AI access per document (e.g., exclude a sensitive
investor side letter from AI context)

Structured Extraction
- Financial statement PDFs are parsed for structured data:
total revenue, total expenses, net income, key line items
- Extracted data is stored separately and queryable directly
(no retrieval needed for structured financial facts)

Proactive Context Requests
- If the AI needs a document it does not have, it surfaces a request:
"To analyze your Q3 burn accurately I need your payroll export.
Can you upload it or connect Gusto?"
- Requests appear in the vault screen with an inline upload button

Onboarding Intake
- Guided 5-step onboarding that generates a client-specific system prompt
- Steps: business basics, jurisdiction, integration connect, document
upload,
confirmation summary

```

```
- Progress saved to backend — refreshing does not lose progress

================================================================================
6. TECHNICAL ARCHITECTURE
================================================================================

The system is composed of six distinct layers:

LAYER 1 — FRONTEND (React + Vite SPA)
The user-facing application. A single-page app served statically. All data
fetched from the FastAPI backend via REST. No sensitive logic in the client.

LAYER 2 — API LAYER (FastAPI)
The primary backend. Handles authentication, tenant isolation, all business
logic endpoints, and orchestrates calls to the AI layer and integrations.
Every request is scoped to a tenant_id enforced by middleware.

LAYER 3 — DATA LAYER (PostgreSQL + Redis)
PostgreSQL stores all structured data. Row-level security enforces tenant
isolation at the database level. Redis caches expensive computed metrics
(dashboard snapshot, forecasts) and manages the job queue.

LAYER 4 — AI LAYER (Ollama + LangGraph + Qdrant)
Ollama runs the LLM locally. LangGraph orchestrates the multi-step reasoning
agent. Qdrant stores per-tenant document embeddings for RAG retrieval.
Langfuse logs every LLM call for observability and debugging.

LAYER 5 — GUARDRAILS ENGINE (Python rules service)
A separate deterministic Python service. Every AI output passes through this
before reaching the API response. Checks thresholds, jurisdiction rules,
reversibility, and blacklisted action types. Not AI — deterministic code.

LAYER 6 — INTEGRATION CONNECTORS (Celery workers)
Each integration (Stripe, Plaid, QuickBooks, etc.) is an isolated Python
connector class with a fetch() method that normalizes output to the internal
financial schema. Celery runs sync jobs on a schedule (every 6 hours).
All connectors are read-only by default.

DATA FLOW (simplified)
Founder asks a question
-> Frontend sends POST /ai/ask to FastAPI
-> FastAPI calls LangGraph agent
-> Agent: classifies query type
-> Agent: retrieves relevant chunks from Qdrant (RAG)
-> Agent: fetches live computed metrics from financial computation layer
-> Agent: calls Ollama with combined context and system prompt
-> Agent: passes output to Guardrails Engine for validation
-> Agent: attaches citations (which documents, which data points)
-> FastAPI: writes recommendation to AuditLog table
-> FastAPI: returns response to frontend
-> Frontend: displays answer with expandable source citations

================================================================================
7. TECH STACK
================================================================================

FRONTEND
React 18 + Vite     Core framework (SPA, no SSR)
TypeScript        Type safety across all components and API contracts
React Router v6     Client-side routing (createBrowserRouter pattern)
Tailwind CSS       Utility-first styling
Shadcn/ui        Pre-built accessible component library

```

```
Recharts         Financial charts (line, bar, waterfall, sparkline)
TanStack Query v5    Data fetching and server state caching
Zustand         Lightweight global state (auth, tenant config,
autopilot settings)
Axios          HTTP client with auth header injection
React Hook Form + Zod  Form handling and schema validation
Vite Dev Proxy      Routes /api/* to localhost:8000 in development

BACKEND
FastAPI (Python)     Primary API framework
PostgreSQL        Primary relational database
Alembic         Database migrations
Redis          Caching and Celery broker
Celery          Async background task queue
Pydantic v2       Data validation and serialization
SQLAlchemy        ORM for database access

AI LAYER
Ollama          Local LLM runtime (no public API calls)
Mistral 7B / LLaMA 3 8B Base model (choose based on GPU availability)
LangChain        LLM primitives and tool integrations
LangGraph        Multi-step agent orchestration
Qdrant          Vector database for RAG (self-hosted, per-tenant)
sentence-transformers  Embedding model (all-MiniLM-L6-v2 to start)
Langfuse         LLM observability and prompt logging

DATA & DOCUMENTS
pypdf          PDF text extraction
python-docx       Word document extraction
pdfplumber        Structured data extraction from financial PDFs
reportlab / weasyprint  PDF generation for investor reports

INTEGRATIONS
Stripe Python SDK    Revenue, MRR, subscription data
Plaid Python SDK     Bank account connections, transaction history
QuickBooks SDK      P&L, balance sheet, AR/AP
Xero SDK         Same as QuickBooks (built in parallel)
Razorpay SDK       India-market billing and banking

INFRASTRUCTURE
Docker + Docker Compose Containerization of all services
Nginx          Reverse proxy in production
AWS or GCP Cloud Run   Cloud deployment (Cloud Run preferred for
auto-scaling to zero on idle)
Terraform        Infrastructure as code
GitHub Actions      CI/CD — test on every push, deploy on merge to main

SECURITY
JWT + OAuth2       Authentication
AES-256         Encryption at rest for all financial data
Row-level security    PostgreSQL tenant isolation at database level
AWS/GCP Secrets Manager Secret key storage (never in env files)

MONITORING
Sentry          Error tracking (frontend and backend)
Prometheus + Grafana   Infrastructure and API metrics
Langfuse         LLM-specific observability

================================================================================
8. PRIVACY & SECURITY MODEL
================================================================================

The privacy architecture is a core product feature, not an afterthought.

```

```
It is the primary reason a founder can trust this system with real financial
data.

LOCAL LLM DEPLOYMENT
All AI inference runs via Ollama on a server within the client's environment
boundary. Financial data never reaches OpenAI, Anthropic, Google, or any
other public LLM API. This is non-negotiable and must be preserved in all
future technical decisions.

TENANT ISOLATION
Every database table includes a tenant_id column. A FastAPI middleware
dependency injects the authenticated tenant_id into every request context.
Every database query is automatically scoped to this tenant_id.
Row-level security in PostgreSQL provides a second enforcement layer.
A separate Qdrant collection is created for each tenant on signup.
No cross-tenant data access is possible by design.

READ-ONLY INTEGRATIONS
All integration connectors are read-only by default. Write access (e.g.,
executing a price change in Stripe) is a separate permission the founder
explicitly grants per integration category in the autopilot config panel.
Read-only and write-enabled API keys are stored separately.

IMMUTABLE AUDIT LOG
The AuditLog table is append-only. No record is ever updated or deleted.
Every AI recommendation, every autonomous action, every guardrails decision,
and every founder approval or rejection is written here with:
- Timestamp
- Tenant ID
- Action type
- Data sources used
- AI reasoning summary
- Outcome

This log is the foundation for investor due diligence and external audits.

SECRETS MANAGEMENT
No API keys, database credentials, or secrets are stored in environment files
in production. All secrets are stored in AWS Secrets Manager or GCP Secret
Manager and injected at runtime.

SHADOW MODE
For the first 30 days of any new client, the autopilot runs in shadow mode
regardless of configuration. It logs what it would have done autonomously
without executing. The founder reviews this log to calibrate comfort before
unlocking any real autonomous execution.

================================================================================
9. TEAM ROLES & RESPONSIBILITIES
================================================================================

The team of three works in parallel stages. Each person owns a distinct domain
across all four stages. Within each stage, all three work simultaneously.

-----------------------------------------------------------------------PERSON 1 — Data, Backend & Integrations
-----------------------------------------------------------------------
This person owns everything related to data infrastructure, the API layer,
integration connectors, the guardrails engine, and the autopilot execution
system. They are the foundation everything else sits on.

Core Ownership Areas:

```

```
- FastAPI backend: all API routes, middleware, authentication, tenant scoping
- PostgreSQL schema design and Alembic migrations
- Redis setup and Celery task queue configuration
- All integration connectors (Stripe, Plaid, QuickBooks, Xero, Razorpay)
- Data normalization pipeline: raw integration data -> internal schema
- Financial computation layer: burn rate, runway, MRR, ARR, CAC, NRR
(deterministic Python functions, not AI)
- Guardrails engine: the Python rules service that validates every AI output
- Autopilot execution engine: action queue, executor, per-action permissions
- Audit log writer: append-only log of every AI action and recommendation
- Expense categorization job: Celery task using ML classifier
- Compliance calendar: jurisdiction-specific deadline database and alerts
- Vendor/SaaS spend tracker: recurring charge detection and ROI scoring
- Load testing and reliability: retry logic, dead letter queues, failure
alerts
- Docker and docker-compose for all backend services
- Terraform infrastructure definitions

Key Interfaces (agreed with other team members on Day 1):
- API response schemas defined as Pydantic models and shared as TypeScript
types with Person 3
- Financial computation function signatures shared with Person 2 so the
AI layer can call them directly
- Guardrails engine input/output contracts shared with Person 2

-----------------------------------------------------------------------PERSON 2 — AI Layer, LLM & Intelligence
-----------------------------------------------------------------------
This person owns everything the AI does: the LLM setup, the reasoning agent,
the RAG pipeline, the scenario modeling engine, the pricing intelligence module,
and the investor report generator.

Core Ownership Areas:
- Ollama setup and model selection (Mistral 7B or LLaMA 3 8B)
- LangGraph agent architecture: query classification, RAG retrieval,
reasoning,
guardrails node, citation builder
- Qdrant setup: per-tenant collection creation, embedding storage, retrieval
- Document ingestion pipeline: file upload -> extraction -> chunking ->
embedding -> Qdrant storage
- Structured financial data extraction from PDFs (pdfplumber + LLM prompts)
- Proactive context request system: detecting missing documents and surfacing
requests to the founder
- System prompt design: per-tenant system prompt generation from intake data,
versioned and tested
- Scenario modeling engine: Monte Carlo simulation for what-if projections
- Anomaly detection: daily Celery task scanning transactions for unusual
patterns
- Pricing intelligence module: WTP analysis, tier gap detection, experiment
engine as a LangGraph subgraph
- Investor report generator: LangGraph chain producing structured MIS reports
with AI-written narrative sections
- Benchmarking engine: anonymized peer comparison metrics
- Langfuse integration: every LLM call logged from day one
- Prompt engineering iteration: continuous improvement of answer quality
and citation accuracy

Key Interfaces (agreed with other team members on Day 1):
- POST /ai/ask, POST /ai/scenario, GET /ai/pricing-recommendation,
GET /ai/anomalies, GET /ai/context-requests endpoint contracts shared with
Person 1 for routing and Person 3 for UI integration
- Financial computation functions called directly from the LangGraph agent
(provided by Person 1)

```

```
- Guardrails engine called as a node in every LangGraph graph
(provided by Person 1)

-----------------------------------------------------------------------PERSON 3 — Frontend, UI & Product
-----------------------------------------------------------------------
This person owns everything the founder sees and interacts with. They are
responsible for the entire React + Vite application, all screens, all data
visualization, and the onboarding experience. They also own user testing and
product feedback loops.

Core Ownership Areas:
- React + Vite project setup: TypeScript, Tailwind, Shadcn/ui, React Router
v6,
TanStack Query, Zustand, Axios, React Hook Form + Zod, Vite dev proxy
- Global layout: sidebar navigation, topbar, main content area
- Auth screens: login, register, wired to Person 1's auth endpoints
- Zustand stores: authStore, tenantStore, autopilotStore
- Mock data file: realistic dummy data for every screen used during
development
before real API endpoints are ready
- Financial health dashboard: runway counter, burn card, MRR sparkline,
cash position, all KPI cards
- AI Q&A interface: chat-style input, streamed responses, expandable
citations,
thumbs up/down feedback
- Scenario modeling UI: input panel, Recharts output with three-line
projection
- Notifications panel: anomaly alerts with severity and dismiss
- Autopilot configuration panel: per-category autonomy sliders, guardrail
inputs,
live preview of what runs automatically vs. what asks for approval
- Approvals inbox: pending actions list, approve/reject with reason
- Onboarding flow: 5-step guided intake with Zod validation, OAuth popup for
integrations, drag-and-drop document upload, progress persistence
- Document vault screen: file list, access toggles, context requests panel,
PDF preview
- Investor and board screen: report generation, report history, benchmark
charts,
fundraising readiness score card
- Final polish: empty states, skeleton loaders, error boundaries, mobile
responsiveness, keyboard navigation, accessibility
- User testing: recruit 3–5 early founders, observe full onboarding without
assistance, document friction points, feed back into product decisions

Key Interfaces (agreed with other team members on Day 1):
- TypeScript types for all API responses received from Person 1
- AI endpoint request/response contracts received from Person 2
- All API calls go through /src/lib/api.ts (the Axios instance)
so base URL and auth headers are managed in one place

================================================================================
10. BUILD STAGES
================================================================================

The project is divided into four sequential stages. Within each stage, all three
team members work simultaneously on their respective domains. Each stage ends
with a full end-to-end test before the next stage begins.

-------------------------------------------------------------------------------STAGE 1 — FOUNDATION (Weeks 1–4)
-------------------------------------------------------------------------------
```

```
Goal: Get infrastructure up, services talking to each other, and auth working.
Nothing user-facing is complete yet, but every foundation is in place.

Person 1 (Backend)
- Initialize FastAPI with folder structure, middleware, CORS, Alembic
- PostgreSQL schema: Tenant, User, FinancialRecord, AuditLog, ConnectorConfig
- JWT auth endpoints: register, login, refresh
- Redis + Celery setup with a health check job
- Stripe connector: connect account, fetch and normalize transactions
- Plaid connector: same pattern
- Docker Compose: backend, PostgreSQL, Redis, Celery all containerized
- GET /health and GET /metrics stub endpoints

Deliverable: Backend running. A tenant can register, connect Stripe and Plaid,
and normalized transaction data lands in PostgreSQL.

Person 2 (AI)
- Ollama running locally with Mistral 7B responding to a basic prompt
- Qdrant: per-tenant collection creation, collection init on new tenant signup
- Document ingestion pipeline: upload -> extraction -> chunking -> embedding
->
Qdrant storage
- Basic RAG retrieval function: query + tenant ID -> top-k relevant chunks
- Base system prompt template with tenant-specific placeholders
- Single-node LangGraph: question -> RAG retrieval -> Ollama -> answer with
citations
- Langfuse running locally, every LLM call logged
- Test script using dummy data: "What is our current burn rate?" returns a
sourced answer

Deliverable: Working AI pipeline. Question in, context retrieved, Ollama
answers with citations, call logged in Langfuse.

Person 3 (Frontend)
- React + Vite project initialized with all dependencies configured
- Tailwind + Shadcn/ui working (manual setup for Vite, not Next.js CLI)
- Vite dev proxy routing /api/* to localhost:8000
- React Router v6 with all page stubs (empty screens for every section)
- Login and register screens wired to Person 1's auth endpoints
- Zustand stores: authStore, tenantStore, autopilotStore
- Axios instance: base URL, auth header injection, 401 interceptor
- Mock data file with realistic dummy data for every future screen
- useHealth hook: pings /health, shows green/red dot in sidebar

Deliverable: Fully navigable app shell. Auth works. Sidebar routes between
page stubs. Mock data ready.

End of Stage 1 Sync:
- Person 3's login calls Person 1's auth endpoint successfully
- Person 1's new tenant creation triggers Person 2's Qdrant collection
creation
- Run full flow once: register -> connect Stripe -> ask a question -> get
answer

-------------------------------------------------------------------------------STAGE 2 — CORE PRODUCT (Weeks 4–9)
-------------------------------------------------------------------------------
Goal: The product becomes usable for the first time. A founder can connect their
data, ask financial questions, and see their financial health.

Person 1 (Backend)

```

```
- Data normalization pipeline: raw Stripe/Plaid data -> FinancialRecord
objects
- Celery scheduled sync job: fresh data every 6 hours, upserts to PostgreSQL
- Financial computation layer: burn rate, runway, MRR, ARR, churn rate, CAC
(deterministic Python functions, not AI)
- Guardrails engine:
-> Pydantic models for every action type (PricingChangeAction,
PaymentAction, ReportAction, AlertAction)
-> Threshold checker (does this exceed configured financial limits?)
-> Reversibility checker (can this be undone? if not, escalate)
-> Jurisdiction rules (India: GST, FEMA; US: Sales Tax)
-> Every AI output passes through before hitting API response
- Audit log writer: every recommendation and action written with timestamp,
tenant_id, data sources, and reasoning summary
- Endpoints: GET /financials/snapshot, GET /financials/burn,
GET /financials/runway, POST /integrations/connect, GET /audit-log

Deliverable: Real financial metrics from real data. Every AI output validated
by guardrails. Every action logged immutably.

Person 2 (AI)
- Expand LangGraph to multi-node agent:
Node 1: Query classifier (burn / runway / pricing / compliance / general)
Node 2: Data retriever (Qdrant RAG + live metrics from Person 1's
functions)
Node 3: Reasoning node (combined context + Ollama call)
Node 4: Guardrails node (Person 1's rules engine)
Node 5: Citation builder (which documents and data points were used)
- Scenario modeling engine: what-if input -> Monte Carlo projection ->
3/6/12 month runway and MRR curves with confidence intervals
- Anomaly detection job: daily Celery task, scans transactions for
spikes/drops,
writes to Notification table
- System prompt tuning: iterate on prompt quality with real tenant intake data
- Endpoints: POST /ai/ask, POST /ai/scenario, GET /ai/anomalies

Deliverable: Working financial Q&A agent using real data, scenario
projections,
anomaly detection, all with citations and guardrails.

Person 3 (Frontend)
- Financial health dashboard:
-> Runway counter (red if under 90 days)
-> Burn rate card with MoM delta
-> MRR card with 6-month sparkline
-> Cash position card
-> All wired to GET /financials/snapshot (swap mock data for real data)
- AI Q&A interface:
-> Chat-style input and response display
-> Expandable source citations below each answer
-> Loading state (streaming optional using EventSource)
-> Thumbs up/down feedback per response
-> Wired to POST /ai/ask
- Scenario modeling UI:
-> Input panel: what changes, by how much, starting when
-> Recharts line chart: 3 curves (optimistic/base/pessimistic)
-> Wired to POST /ai/scenario
- Notifications panel: anomaly alerts with severity and dismiss button

Deliverable: Working dashboard showing real financial health, AI Q&A with
citations, scenario modeling UI, anomaly alerts.

End of Stage 2 Sync:
- Full end-to-end test with one real (or Stripe test mode) startup's data

```

```
- Ask 20 different financial questions, grade answers, fix the worst failures

-------------------------------------------------------------------------------STAGE 3 — AUTOPILOT + ONBOARDING (Weeks 9–13)
-------------------------------------------------------------------------------
Goal: The product becomes configurable and self-serve. A new startup can sign up
and get value without anyone from the team helping them.

Person 1 (Backend)
- Autopilot execution engine:
-> Action queue: approved actions wait here before execution
-> Executor: reads queue, calls right integration API per action type
-> Per-action permission model: each action requires minimum autonomy
level
-> Actions below tenant's config level execute automatically
-> Actions above config level go to approvals inbox
- Daily digest Celery job: compiles all autonomous actions, sends summary
email
- QuickBooks connector (using same pattern as Stripe/Plaid)
- Xero connector (built in parallel with QuickBooks)
- Razorpay connector (for India-market clients)
- Expense categorization job: Celery task, ML classifier (fine-tuned
sentence-transformer), categories editable by founder
- Endpoints: POST /autopilot/configure, GET /approvals,
POST /approvals/{id}/approve, POST /approvals/{id}/reject

Deliverable: Autopilot runs real actions, approvals inbox works, two more
integrations available.

Person 2 (AI)
- Pricing intelligence module as LangGraph subgraph:
-> Pulls Stripe plan data and usage patterns
-> WTP estimation using cohort churn rates by plan
-> Tier gap detection: are customers bunching at top of a tier?
-> Produces PricingRecommendation object through guardrails engine
- Document intelligence upgrade:
-> Financial statement parsing: extract structured data from P&L PDFs
using pdfplumber + LLM extraction prompt
-> Structured data stored separately for direct querying (no RAG needed)
-> Proactive context request system: missing document -> ContextRequest
written to table -> surfaces as prompt to founder
- Add pricing reasoning node to main LangGraph agent
- Endpoints: GET /ai/pricing-recommendation, GET /ai/context-requests

Deliverable: AI surfaces pricing recommendations, proactively asks for missing
documents, structured financial data extracted from PDFs.

Person 3 (Frontend)
- Full 5-step onboarding flow:
Step 1: Business basics (name, business model, revenue type, funding
stage)
Step 2: Geography and jurisdiction (countries, foreign revenue %)
Step 3: Integration connect (OAuth popup per integration, turns green on
success)
Step 4: Document upload (drag-and-drop, progress bar per file, AI
recommends what to upload based on business model)
Step 5: Confirmation (summary of what is connected, what AI can do)
-> All steps validated with Zod
-> Progress saved to backend; refresh does not lose progress
- Autopilot configuration panel:
-> Per-category autonomy sliders (Expense Categorization, Report
Generation,

```

```
Alerts, Pricing Changes, Payments)
-> Guardrail inputs (max autonomous amount, revenue floor, notification
preferences)
-> Live preview of what runs automatically vs. what asks for approval
- Approvals inbox:
-> Pending actions list with reasoning, data trigger, expected outcome
-> Approve / Reject (reject requires reason)
-> Completed actions tab showing what ran automatically
- Pricing recommendation card: surfaces on dashboard, shows analysis,
Apply to Stripe button creates an approval action

Deliverable: New founder can sign up, complete onboarding, connect tools,
configure autopilot, and use the product entirely without team assistance.

End of Stage 3 Sync:
- Recruit 3–5 early-stage founders for unassisted onboarding observation
- Do not help them during the session
- Note every point of confusion; fix top 5 before Stage 4

-------------------------------------------------------------------------------STAGE 4 — POLISH, INVESTOR LAYER & LAUNCH PREP (Weeks 13–17)
-------------------------------------------------------------------------------
Goal: The product goes from working to sellable. Every screen has a proper
state,
the investor layer is complete, and the backend is reliable under load.

Person 1 (Backend)
- Comprehensive error handling: retry logic with exponential backoff, dead
letter queue for failed jobs, alerting when sync fails 3 times in a row
- Vendor intelligence:
-> Scan transactions for recurring charges to known SaaS vendors
-> Group by vendor, compute monthly cost, flag duplicates and low usage
-> GET /vendors endpoint with cost and ROI scoring
- Compliance calendar: jurisdiction-specific deadline database, Celery job
checking deadlines at 30/14/7 days, writes to Notification table
- Load testing: simulate 50 concurrent tenants running syncs and AI queries,
find and fix bottlenecks before launch

Deliverable: Backend reliable under load, handles failures gracefully, vendor
intelligence and compliance deadlines surfaced.

Person 2 (AI)
- Investor report generator:
-> LangGraph chain consuming 3 months of financial data
-> Sections: Executive Summary, MRR/Revenue, Burn/Runway, Key Metrics vs
Last Quarter, Risks, Outlook
-> Narrative sections AI-written with citations, founder reviews before
PDF
-> PDF generation using reportlab or weasyprint
- Board deck data package: structured JSON of all key metrics formatted for
slide creation (not slide generation — the data package a founder fills
their own template with)
- Benchmarking engine:
-> Anonymized aggregate metrics across opt-in tenant base
-> Percentile rank on burn multiple, NRR, CAC payback, gross margin
-> GET /benchmarks/me
- Endpoints: POST /reports/generate, GET /reports/{id}, GET /reports/{id}/pdf

Deliverable: AI auto-generates investor-ready MIS reports, board deck data
package, peer benchmarking.

Person 3 (Frontend)

```

```
- Investor and board intelligence screen:
-> Report generation button with progress indicator
-> In-app preview before PDF download
-> Report history with download links
-> Benchmark comparison charts (your metrics vs. peer median)
-> Fundraising readiness score card with per-criterion pass/fail
- Document vault screen:
-> Full document list with upload date, type, AI access toggle
-> Context requests panel with inline upload button
-> PDF preview
- Final polish across all screens:
-> Empty states: helpful message + action for every screen (not blank)
-> Skeleton loaders instead of spinners for data-heavy screens
-> Error boundaries on every page
-> Mobile responsiveness check
-> Keyboard navigation and basic accessibility pass

Deliverable: Product looks and feels finished. Every screen has working state,
empty state, loading state, and error state. Ready to show to customers.

End of Stage 4 Sync:
- Full product walkthrough as if pitching to a new customer
- Every screen, every flow, every edge case
- List the top 10 issues found and resolve before any external demo

================================================================================
11. INTEGRATION ROADMAP
================================================================================

Build integrations in this exact order. Each is an isolated Python connector
class with a fetch() method that normalizes output to the internal schema.

PHASE 1 (Stage 1 — required to start)
Stripe     Revenue, MRR, subscriptions, refunds, failed payments
Plaid      Bank account connections, transaction history, cash position

PHASE 2 (Stage 3 — needed for broader coverage)
QuickBooks   P&L, balance sheet, accounts payable/receivable
Xero      Same as QuickBooks (built in parallel, shared test suite)
Razorpay    India-market billing and RazorpayX for banking

PHASE 3 (post-launch — based on customer demand)
Gusto      Payroll (US) — needed for fully-loaded burn calculation
Deel / Remote  International payroll
Chargebee    Subscription billing (for non-Stripe customers)
Paddle     Billing + merchant of record
HubSpot     CRM data for CAC and sales pipeline analysis
PostHog     Product analytics for feature-to-revenue attribution
Darwinbox    India HR and payroll

ALL INTEGRATIONS ARE READ-ONLY BY DEFAULT.
Write access is a separate permission, explicitly granted per category, per
integration, in the autopilot configuration panel.

================================================================================
12. OPEN QUESTIONS TO RESOLVE (Before or During Stage 1)
================================================================================

These need a team decision before building, not after.

Q1: Pricing model
Subscription per startup, or percentage of operations processed?

```

```
The local LLM deployment is compute-intensive. Suggested starting point:
$49/month Starter (Stripe + Plaid only, advisory mode),
$149/month Growth (all integrations, semi-auto),
$399/month Scale (full autopilot, investor layer, benchmarking).

Q2: Multi-tenant vs. dedicated per-client infrastructure
Shared compute with strict data isolation (separate Qdrant collections
and system prompts per tenant) is cheaper and scalable.
Dedicated per-client Ollama instances are more private but expensive.
Recommendation: start shared-compute, offer dedicated as an enterprise
add-on only.

Q3: Minimum viable integration set for launch
Stripe + Plaid + CSV upload covers 80% of seed-stage startups.
Do not delay launch waiting for QuickBooks or Xero.
Ship with two integrations and a CSV fallback.

Q4: Handling clients with messy books
Many early-stage startups have uncategorized transactions, mixed
personal/business expenses, no consistent accounting. The AI needs a
data cleaning pass before it can give accurate advice. This is a product
feature (a "books cleanup wizard") that should be planned for Stage 2.

Q5: Legal liability for financial recommendations
Before any external user touches the product, get a lawyer to review the
terms of service. The AI is explicitly a recommendation tool, not a
licensed financial advisor. Disclaimers alone are insufficient —
the terms need to be correct before launch, not after a problem occurs.

Q6: GPU infrastructure cost
Running Mistral 7B on an A10G GPU costs approximately $0.75/hour on GCP.
At 50 active tenants making 10 AI queries/day average, estimate compute
cost and ensure it is covered by subscription revenue at launch pricing.
Run this calculation before finalizing pricing in Q1.

================================================================================
13. KEY RULES FOR THE TEAM
================================================================================

RULE 1 — Interface contracts on Day 1
Before anyone writes a line of feature code, all three people agree on:
- API response schemas (Pydantic models + TypeScript types)
- AI endpoint request/response contracts
- Financial computation function signatures
Write these down. Commit them to the repo. Change them only by mutual
agreement.
This is what allows three people to build simultaneously without blocking.

RULE 2 — Mock data before real data
Person 3 always builds against mock data until Person 1's real endpoints
are ready. Person 2 always tests against dummy financial data until Person 1's
integration connectors are pulling real data. Never block each other.

RULE 3 — Guardrails before AI output is visible
The guardrails engine must be complete and tested before any AI recommendation
is shown to an external user. Do not cut this under time pressure.
One bad AI recommendation shown to a founder — even in beta — loses that
client permanently.

RULE 4 — Shadow mode for 30 days
Every new client's autopilot runs in shadow mode for 30 days regardless of
their configuration. Logs what it would have done without doing it.
Founder reviews and calibrates before any real autonomous execution.

```

```
RULE 5 — Weekly sync, one hour
Every week, one 1-hour sync. Each person covers:
- What they shipped this week
- What is blocking them
- What they need from the other two
Keep it short and specific. Do not use this time for design discussions
(handle those async in writing).

RULE 6 — End-of-stage test is non-negotiable
Each stage ends with all three people doing a full end-to-end test together
before the next stage starts. Not a code review. Actually using the product
as a founder would. Nothing from the current stage carries forward broken
into the next stage.

RULE 7 — First milestone before building more
The first milestone is narrow and specific: a founder connects their Stripe
account, uploads one financial document, asks "what is my current burn rate?"
and gets a sourced answer. Get this working completely before building
anything else. Show it to 5 founders. Get feedback. Then proceed.

================================================================================
END OF DOCUMENT
Version  : 1.0
Status  : Internal — Pre-Build
Last Updated : May 2026
================================================================================

```

