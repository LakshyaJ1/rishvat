# AI CFO — Project Overview

## Vision
AI-native financial operating system for pre-seed to Series A startups that cannot afford a full-time CFO. Delivers CFO-grade insights (burn rate, runway, MRR, anomaly detection, compliance alerts, pricing intelligence) while keeping all financial data private via local AI inference.

## Product Summary
- **Type**: B2B SaaS
- **Target**: Founders at pre-seed to Series A startups
- **Revenue Model**: Subscription tiers ($49 / $149 / $399 per month)
- **Key Differentiator**: Privacy-first (Ollama local inference), human-in-the-loop, fully auditable

## Core Architecture
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React + Vite + TypeScript | SPA with financial dashboards |
| API | FastAPI (Python) | REST API with tenant isolation |
| Data | PostgreSQL + Redis | Relational data + caching/queues |
| AI | Ollama + LangGraph + Qdrant | Local LLM + RAG pipeline |
| Guardrails | Python rules engine | Deterministic AI output validation |
| Integrations | Celery workers | Stripe, Plaid, QuickBooks, Xero, Razorpay |
| Infra | Docker + Terraform | Containerized deployment |

## Current System Status
- **Stage**: 1 — Foundation (in progress)
- **Backend**: Core structure created, auth, connectors, audit log
- **Frontend**: Not started (Person 3)
- **AI Layer**: Not started (Person 2)

## Team
- **Person 1**: Backend, integrations, financial engine, guardrails, infra
- **Person 2**: AI layer, LLM, RAG, LangGraph
- **Person 3**: Frontend, UI, product
