# 📋 FUTUREEX AI — MASTER PROMPT v6.0

**Version:** 6.0
**Date:** 2026
**Status:** Active — Sprint 2.5 In Progress
**Author:** FutureEx Architecture Team
**Companion Doc:** `GTM_PLAYBOOK_v1.0.md`

---

## SECTION 0: WHAT THIS DOCUMENT IS

```
THIS IS THE CODING CONTEXT DOCUMENT.

USE THIS WHEN:
  → Writing code
  → Designing architecture
  → Reviewing technical decisions
  → Onboarding new engineers
  → Debugging or refactoring

DO NOT USE THIS FOR:
  → Sales conversations    → Use GTM_PLAYBOOK_v1.0.md
  → Pitch deck content     → Use GTM_PLAYBOOK_v1.0.md
  → Marketing copy         → Use GTM_PLAYBOOK_v1.0.md
  → Investor narratives    → Use GTM_PLAYBOOK_v1.0.md

WHEN STARTING A SESSION:
"Load FutureEx Master Prompt v6.0.
 Current sprint: [N].
 Current track: [X].
 Current task: [specific].
 [Paste relevant existing files]"
```

---

## SECTION 1: WHAT FUTUREEX IS

### Product Identity
```
Name:     FutureEx AI
Category: Executive AI (a new category)
Tagline:  "Dream. Chat. Build. Launch. Manage. Market."
Type:     Programmable Economic Operating System
Market:   India-first, Global-ready
URLs:     futureex.ai (main)
          *.futureex.store (customer storefronts)
          store-builder.futureex.ai (design studio)
          symbiote.futureex.ai (customer PWA)
          pos.futureex.ai (Point of Sale)
          kds.futureex.ai (Kitchen Display)
          wa.me/futureex (WhatsApp entry)
```

### The One-Line Truth
```
FutureEx is an Executive AI platform that gives any
business — from a chaiwala to a mid-market D2C brand —
a complete team of AI executives who don't just chat,
they execute. The platform is also the economic
operating system on which any two businesses can
transact, the governance layer that creates financial
truth, and the launchpad where new businesses can
be dreamed up and brought to life — all without
leaving the system.
```

### What FutureEx Is NOT vs IS
```
NOT:                          IS:
❌ A chatbot                  ✅ Executive AI (decisions + execution)
❌ Generative AI only         ✅ Operational AI (acts, not just generates)
❌ A store builder            ✅ Programmable Economic OS
❌ A marketplace              ✅ Infrastructure for any business model
❌ A rigid ERP                ✅ 262 atomic neurons composing any flow
❌ A SaaS tool                ✅ The internet layer for Indian business
❌ Single-tenant              ✅ Inter-tenant economic system
❌ Industry-specific          ✅ Any industry via configuration
❌ For operators only         ✅ For dreamers, builders, AND operators
```

### The 6-Stage User Journey (The Tagline Made Real)
```
The tagline is not marketing — it is a literal
description of the 6 stages a user passes through.

DREAM    → User has an idea
           Sandbox + Ideas (Sprint 4 Workspaces)

CHAT     → User talks to AI to clarify
           CoFounderExonion + WorkspaceExonion

BUILD    → User configures business
           OnboardingExonion + CatalogExonion

LAUNCH   → Store goes live
           StoreExonion + Store Builder + handle

MANAGE   → Daily operations
           Main Office + 22 exonions + ExecutionFeed

MARKET   → Growth + optimization
           Analytics + BCX + Proactive Agents
           (Sprint 4-5)

This journey is the architectural backbone.
Every feature must answer: "which stage does this serve?"
```

### The Expanded Vision (4 Layers + Engine + Brain)
```
SYMBIOTE (end-customer app — PWA in Sprint 4, native Sprint 6+)
  ↕ connects buyers ↔ businesses

┌─────────────────────────────────────────────────────┐
│ THE BRAIN (Sprint 5)                                │
│ BCX (Business Context Engine)                       │
│ Prompt Architecture Layer                           │
│ Proactive Agents + Autonomous Execution             │
│ Learning Loop                                       │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ THE THINKING LAYER (Sprint 4)                       │
│ Workspaces: Sandbox + Ideas + Living Docs           │
│ WorkspaceExonion + Cross-Exonion Consultation       │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ LAYER 4: GROUP OPERATING LAYER                      │
│ Holding companies, franchises, consolidation        │
│ Status: Post Sprint 3                               │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ LAYER 3: PLATFORM GOVERNANCE LAYER                  │
│ Commission, GST, risk, disputes, audit              │
│ Status: Sprint 3                                    │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ LAYER 2: INTER-TENANT ECONOMIC LAYER                │
│ B2B transactions, double-entry ledgers              │
│ Settlements, escrow, economic truth                 │
│ Status: Sprint 3                                    │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ LAYER 1: TENANT OPERATIONS LAYER                    │
│ Products, orders, customers, payments               │
│ WhatsApp, AI exonions, store, POS, KDS              │
│ Status: Sprint 1-2.5                                │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ EXECUTION ENGINE                                    │
│ 262 Neurons + 22 Exonions + 29 Capabilities         │
│ Powers all layers above                             │
└─────────────────────────────────────────────────────┘
```

---

## SECTION 2: BUSINESS MODEL

### Three Doors, One Platform
```
FutureEx serves three buyer segments through three
distinct surfaces — but ONE underlying platform.

DOOR 1: Mid-Market D2C / SMB (futureex.ai homepage)
  Self-serve + sales-assist
  Pricing: per-AI-Executive (₹1.5L–₹6L/month)
  Target: ₹50–500 Cr revenue brands
  Wedge: AI Head of Operations

DOOR 2: Enterprise (futureex.ai/enterprise — gated)
  Sales-led, RFP, security review
  Pricing: ₹50L–₹2Cr/year custom
  Target: Brands ₹500 Cr+
  Requires: SOC2, audit logs, RBAC, integrations

DOOR 3: Kirana / Micro Business (wa.me/futureex)
  WhatsApp-only, viral
  Pricing: FREE → ₹499 → ₹1,999/month
  Target: Chaiwalas, home bakers, local retail
  Powered by: Sprint 2.6 micro-exonions (cost optimized)

ARCHITECTURALLY: same neurons, same exonions, same
economic layer. Different surfaces, pricing, and
model selection per door.

GTM details: see GTM_PLAYBOOK_v1.0.md
```

### Subscription Tiers (Kirana / SMB Door)
```
┌────────────┬──────────┬──────────┬──────────────────────┐
│ Plan       │ Monthly  │ Txn Fee  │ Key Features         │
├────────────┼──────────┼──────────┼──────────────────────┤
│ FREE       │ ₹0       │ 8%       │ 1 store, 25 items    │
│            │          │          │ Monthly payouts      │
├────────────┼──────────┼──────────┼──────────────────────┤
│ PREMIUM    │ ₹499     │ 5%       │ 3 stores, 100 items  │
│            │          │          │ Weekly payouts       │
│            │          │          │ 14-day free trial    │
├────────────┼──────────┼──────────┼──────────────────────┤
│ BUSINESS   │ ₹1,999   │ 3%       │ 10 stores, 1K items  │
│            │          │          │ Daily payouts        │
│            │          │          │ API access           │
└────────────┴──────────┴──────────┴──────────────────────┘
```

### AI Executive Pricing (Mid-Market Door)
```
Sold as "team members" not features.
Price feels like salary, not subscription.

🎛️  AI Head of Operations          ₹2L/month
📱  AI Head of Growth & Retention   ₹1.5L/month
📦  AI Head of Merchandising        ₹2L/month
💰  AI CFO                          ₹1.5L/month
🎯  AI Chief of Staff               ₹1L/month
                                    (required if 2+ executives)

THE FULL C-SUITE                    ₹6L/month
(All 5 + AI Chief of Staff. Save ₹2L vs individual.)

Each "AI Executive" maps to one or more exonions
running with full BCX context (Sprint 5).
```

### Enterprise Pricing (Top Door)
```
Custom contracts, structured as:

Platform license:    ₹25 L/year
Per-agent fee:       ₹50 K/agent/year × N agents
Outcome bonus:       0.1% of incremental revenue
Implementation:      ₹50 L one-time

Total typically:     ₹50 L – ₹2 Cr/year
Sales cycle:         6–9 months
Requirements:        SOC2, SSO, RBAC, audit logs,
                     guardrails, custom connectors
```

### Revenue Streams
```
Stream 1: Subscription MRR (per-tier or per-executive)
Stream 2: Transaction Commission (B2C: 5-8%, B2B: 1-3%)
Stream 3: Message Markup (~10% on Meta WhatsApp costs)
Stream 4: Logistics Commission (10% on delivery fees)
Stream 5: Partner Revenue Share (agency subscriptions)
Stream 6: Enterprise Implementation + Outcome Bonus
```

### Business Models Supported
```
SIMPLE:
✅ B2C Retailer → Customer
✅ Service Business → Customer
✅ Freelancer → Client

COMPLEX SUPPLY CHAIN:
✅ Manufacturer → Distributor → Retailer → Customer
✅ Manufacturer → D2C Customer

PLATFORM MODELS:
✅ Aggregator ↔ Vendors ↔ Customers

AGENCY MODELS:
✅ Agency manages own business
✅ Agency manages client businesses on FutureEx
✅ Agency builds stores for clients
✅ Freelancer delivers projects via FutureEx
✅ MSP manages 50+ businesses

CORPORATE:
✅ Franchise network (HQ → outlets)
✅ Holding company (parent → subsidiaries)
✅ Conglomerate (group → diverse businesses)

LAUNCH MODELS (unique to FutureEx):
✅ Aspirant with idea → built business via Workspaces
✅ Side hustle → full business via gradual upgrade
✅ Existing offline → digitized + AI-run
```

---

## SECTION 3: TECHNICAL ARCHITECTURE

### What A Neuron Is
```
NEURON = Atomic unit of real-world business action

Every neuron has:
📥 INPUT SCHEMA    — Zod validated
⚙️  PROCESSING     — Pure logic
📤 OUTPUT SCHEMA   — Typed return
📡 EVENTS EMITTED  — string[]
🔒 PERMISSIONS     — Who can use it
♻️  IDEMPOTENT     — Safe to retry

Rules:
1. Every neuron works independently
2. Clear input/output contract
3. Communicate through events only
4. Stateless (state lives in data layer)
5. Triggered by events, APIs, schedules, or AI
6. Never knows about other neurons
7. Never imports from other modules
```

### Neuron Ontology (4 Layers)
```
L1: UNIVERSAL PRIMITIVES (stable forever)
    ENT, STA, REL, EVT, TIM, RUL

L2: BUSINESS CAPABILITIES
    CAT, COM, PAY, INV, FUL, MSG, PPL, FIN
    BKG, WRK, MKT, ANL, STR, VND, PLT

L3: DOMAIN EXTENSIONS (industry-specific)
    MFG (manufacturing), DST (distribution)
    AGG (aggregator), PRT (partner/agency)
    PRJ (project management)

L4: ECONOMIC LAYER (inter-tenant)
    ECO, LDG, STL, ESC, GOV, GRP
```

### Complete Neuron Count
```
LAYER 1 PRIMITIVES:           25 neurons
LAYER 2 BUSINESS:            160 neurons
LAYER 3 DOMAIN:               42 neurons
LAYER 4 ECONOMIC:             35 neurons
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:                       262 neurons
Built in Sprint 1:            13 neurons
Built in Sprint 2:            28 neurons (cumulative)
Sprint 2.5 adds:              17 + 4 wired (Razorpay)
Sprint 3 completes:          all 262
```

### What An Exonion Is
```
EXONION = Isolated AI persona with its own:
  → Chat history and memory namespace
  → Capability set (only what it needs)
  → Neuron access (only its domain)
  → Personality + system prompt
  → LLM config (model, temperature)
  → Trigger events (what wakes it up)
  → Handoff rules (when to escalate)
  → Runtime type (cloud-llm | micro-model)
  → BCX field selection (Sprint 5+)

SCOPE LEVELS:
  org      → sees one organisation only
  platform → sees all orgs (EconomicExonion)
  group    → sees all orgs in a group

User-facing name: "AI Executive" or by role
                  (e.g., "AI Head of Operations")
Internal term:    Exonion (preserved in code)

EVOLUTION:
Sprint 1: 11 role-string agents (shared memory)
Sprint 2: 6 isolated exonions running, 14 stubs
Sprint 2.5: +1 (StoreExonion) = 21 total
Sprint 4: +1 (WorkspaceExonion) = 22 total
Sprint 3-5: All 22 active and reasoning with BCX
```

### Complete Exonion List (22)
```
CORE BUSINESS (Sprint 2 — running):
  CoFounderExonion    → orchestrator, strategist
                        Public: "AI Chief of Staff"
  OnboardingExonion   → business setup guide
  CatalogExonion      → products & inventory
                        Public: "AI Head of Merchandising"
  SalesExonion        → orders & revenue
                        Public: "AI Head of Sales"
  FinanceExonion      → money & payments
                        Public: "AI CFO"
  OperationsExonion   → day-to-day execution
                        Public: "AI Head of Operations"

ADDED IN SPRINT 2.5:
  StoreExonion        → store designer
                        Public: "AI Store Designer"

ADDED IN SPRINT 4:
  WorkspaceExonion    → strategy advisor + idea evaluator
                        Public: "AI Strategy Advisor"
                        ONLY exonion that consults others

EXPANDED (Sprint 3 — activate):
  MarketingExonion    → growth & campaigns
                        Public: "AI Head of Growth"
  SupportExonion      → customer happiness
                        Public: "AI Customer Success Lead"
  LogisticsExonion    → delivery & supply
  HRExonion           → people & workforce
  ProcurementExonion  → buying & vendors
  AnalyticsExonion    → intelligence & insights
                        Public: "AI Head of Analytics"

SPECIALIST (Sprint 3 — activate):
  ManufacturingExonion → production planning
  DistributionExonion  → supply chain & territory
  AggregatorExonion    → marketplace coordination
  PartnerExonion       → agency & client management
  ProjectExonion       → deliverable management

PLATFORM LEVEL (Sprint 3 — activate):
  EconomicExonion      → financial truth keeper
  ComplianceExonion    → tax & regulatory guardian
  GroupExonion         → holding company brain
```

### What A Capability Is
```
CAPABILITY = Named outcome that maps to neuron flows

  User/AI → Capability → Neurons → Events → Result

Examples:
  setup_catalog    → [CAT-001, CAT-008, EVT-001]
  place_order      → [TRX-003, PAY-001, MSG-001]
  make_payment     → [PAY-001, PAY-002, EVT-001]
  transact_b2b     → [ECO-001, LDG-001, STL-001]
  generate_store   → [STR-001, CAT-008, EVT-001]
  evaluate_idea    → [ANL-001, ANL-002, EVT-001]
                     (cross-exonion consultation)

Total capabilities: 29
```

### What BCX Is (Sprint 5 — First-Class Concept)
```
BCX = Business Context Engine

A living, structured understanding of each business,
derived entirely from operational data — never from
user input.

BCX SCHEMA SECTIONS:
  identity         (name, industry, model, stage)
  offerings        (SKUs, pricing, top sellers, margins)
  customers        (count, LTV, repeat rate, segments)
  revenue          (today/week/month, growth, peaks)
  operations       (fulfillment, completion, stockouts)
  financialHealth  (margin, cash, AR/AP, profit trend)
  insights         (strengths, weaknesses, anomalies, NBA)
  goals            (primary goal, monthly target, focus)

BCX REFRESH:
  Hourly via Cloud Tasks
  + Triggered by: ORDER_CONFIRMED, PAYMENT_VERIFIED,
                  INVENTORY_UPDATED, CAMPAIGN_COMPLETED

BCX USAGE:
  Every exonion call injects BCX into prompt.
  Each exonion gets only relevant BCX sections.
  Field selection per exonion is configured.

WITHOUT BCX: AI gives generic answers.
WITH BCX:    AI gives data-driven, business-specific answers.

BCX is what makes "Executive AI" real.
```

### The 6-Layer Prompt Architecture (Sprint 5)
```
Every exonion call uses this prompt structure:

Layer 0: Identity
         "You are an OPERATOR not an assistant"

Layer 1: Live BCX data injection
         Selected fields based on exonion role

Layer 2: Role-specific expertise
         Domain knowledge for this exonion

Layer 3: Operating principles
         Honest, data-backed, decisive

Layer 4: Mode detection
         decision | execution | diagnosis | teaching | planning

Layer 5: India-specific constraints
         GST, festivals, Hinglish, COD, RBI rules

Layer 6: Output format rules
         What I see / What I recommend / What will happen / Shall I do it?

+ User message
↓
Specific, data-driven, actionable response.

This replaces all generic system prompts in Sprint 5.
```

### The Execution Flow
```
USER (web / WhatsApp / POS / KDS / Symbiote)
       ↓
EXONION (isolated AI persona)
  Reads BCX (Sprint 5)
  Reads Live Docs (Sprint 4)
  Understands intent
  Maps to capability
       ↓
CAPABILITY LAYER
  POST /exons/capabilities/execute
       ↓
NEURONS EXECUTE
  Atomic actions fire
  Events emitted
       ↓
EXECUTION FEED UPDATES
  Real-time in dashboard
       ↓
WORKERS REACT (async)
  Side effects: notifications, settlements, BCX recompute
       ↓
LEARNING LOOP CAPTURES (Sprint 5)
  Outcome measured 24h / 7d later
  Feeds back into model improvement
```

### Cross-Exonion Consultation Pattern (Sprint 4)
```
WorkspaceExonion is the ONLY exonion permitted to
formally request data from other exonions.
This enables the "debate model" without chaos.

REQUEST FORMAT (structured, not free-form):
  {
    requestingExonion: 'workspace-exonion'
    targetExonion:     'finance-exonion'
    dataRequest:       'current_margin_and_trend'
    ideaContext:       'Evaluating 30% discount campaign'
  }

RESPONSE FORMAT (data only, no opinions):
  {
    respondingExonion: 'finance-exonion'
    dataProvided: {
      currentMargin: 18,
      trend: 'stable',
      riskAssessment: '30% off creates negative margin'
    }
  }

WorkspaceExonion aggregates all responses,
then synthesizes a single recommendation.

Other exonions NEVER call each other directly.
All cross-domain coordination goes through:
  → CoFounderExonion (operational)
  → WorkspaceExonion (strategic / idea evaluation)
```

### Live Docs Injection Pattern (Sprint 4)
```
Docs marked `isLive: true` in Workspace are
automatically injected into relevant exonion prompts.

Example:
  SupportExonion handles a refund query
  → packages/exon-core/src/context/doc.context.injector.ts
  → getRelevantDocs(orgId, 'support', 'refund_query')
  → Injects refund policy doc into prompt
  → AI responds using OWNER's policy, not generic answer

This is the "AI doesn't make up policy" guarantee.
Critical for enterprise + compliance conversations.
```

### Autonomous Execution + Permission Levels (Sprint 5)
```
THREE LEVELS — owner controls what AI can do alone:

LEVEL 1 — AUTO-EXECUTE (notify after, undoable 30 min):
  Send order confirmations
  Send invoices
  Send low-stock alerts
  Update order status from KDS actions
  Payment reminders < ₹1,000
  Standard customer queries via Live Docs

LEVEL 2 — ASK FIRST, THEN EXECUTE:
  Launch campaigns
  Apply discounts
  Payment links > ₹1,000
  Restock requests
  Refunds < ₹500
  Bulk WhatsApp to customer list

LEVEL 3 — ALWAYS REQUIRE EXPLICIT APPROVAL (hardcoded):
  Any action > ₹10,000 impact
  Price changes
  Refunds > ₹500
  Deleting any data
  B2B orders or commitments
  Staff changes
  Integration changes

These cannot be moved to lower levels.
Audit log captures every autonomous action.
30-minute undo window for Level 1 actions.
```

### Neuron Contract (Unchanged, Non-Negotiable)
```
EVERY NEURON MUST HAVE:
1. Unique ID (e.g., CAT-001)
2. Input schema (Zod validated)
3. Output schema (typed)
4. Events emitted (string[])
5. Idempotency key logic
6. No imports from other modules
7. No direct DB writes to other domains
8. Stateless (state lives in Firestore/Redis)
```

---

## SECTION 4: ACTUAL MONOREPO STRUCTURE

```
fexverse/
│
├── apps/
│   ├── api/                ✅ LIVE — Backend API
│   │                          Cloud Run asia-south2
│   │
│   ├── exons/              ✅ LIVE — AI Exonion Service
│   │                          POST /exons/chat
│   │                          POST /exons/chat/:exonionId
│   │                          POST /exons/capabilities/execute
│   │
│   ├── futureex/           ✅ LIVE — Main Office Web App
│   │                          /dashboard/*
│   │                          /dashboard/connect/*
│   │                          /dashboard/workspace/* (Sprint 4)
│   │                          /dashboard/analytics (Sprint 4)
│   │
│   ├── workers/            ✅ LIVE — Event Subscribers
│   │                          BCXWorker (Sprint 5)
│   │                          ProactiveAgentSubscriber (Sprint 5)
│   │
│   ├── webhooks/
│   │   ├── whatsapp/       ✅ LIVE
│   │   ├── instagram/      ⬜ Future
│   │   ├── shadowfax/      ⬜ Sprint 4
│   │   └── ebay/           ⬜ Sprint 4
│   │
│   ├── store/              🔵 Sprint 2.5 — *.futureex.store
│   ├── store-builder/      🔵 Sprint 2.5 — store-builder.futureex.ai
│   ├── pos/                🔵 Sprint 2.5 (rewire) — pos.futureex.ai
│   ├── kds/                🔵 Sprint 2.5 (rewire) — kds.futureex.ai
│   ├── micro-exonions/     ⬜ Sprint 2.6 (parallel)
│   ├── symbiote/           ⬜ Sprint 4 — symbiote.futureex.ai
│   └── docs/               ⬜ Future
│
├── modules/                ← Neurons live here
│   ├── commerce/           ✅ Live
│   ├── finance/            ✅ Live
│   ├── inventory/          ✅ Live
│   ├── people/             ✅ Live
│   ├── marketing/          ✅ Live
│   ├── exonion/            🔵 Rebuild in progress
│   ├── payment/            🔵 Sprint 2.5 (Razorpay wire)
│   ├── fulfillment/        🔵 Sprint 2.5
│   ├── communication/      🔵 Sprint 2.5
│   ├── store/              🔵 Sprint 2.5
│   ├── workforce/          🔵 Sprint 2.5
│   ├── booking/            🔵 Sprint 2.5
│   ├── logistics/          ⬜ Sprint 3
│   ├── manufacturing/      ⬜ Sprint 3
│   ├── distribution/       ⬜ Sprint 3
│   ├── aggregator/         ⬜ Sprint 3
│   ├── partner/            ⬜ Sprint 3
│   ├── project/            ⬜ Sprint 3
│   ├── economic/           ⬜ Sprint 3
│   ├── ledger/             ⬜ Sprint 3
│   ├── settlement/         ⬜ Sprint 3
│   ├── escrow/             ⬜ Sprint 3
│   ├── governance/         ⬜ Sprint 3
│   └── group/              ⬜ Sprint 3
│
├── packages/               ← Shared infrastructure
│   ├── neuron-core/        ✅ 262 defined
│   ├── exon-core/          ✅ Published
│   │                          + bcx.prompt.builder (Sprint 5)
│   │                          + doc.context.injector (Sprint 4)
│   ├── exonions/           ✅ 22 definitions
│   ├── collections/        ✅ Live
│   ├── events/             ✅ Live
│   ├── auth/               🔵 Sprint 2.5 upgrades
│   │                          Custom claims (4 roles)
│   │                          Staff PIN, Device QR, Customer OTP
│   ├── integrations/       ⬜ Sprint 4 — adapter framework
│   ├── micro-models/       ⬜ Sprint 2.6
│   ├── component-registry/ ✅ Store V1 package
│   ├── validators/         ✅ Live
│   ├── firebase/           ✅ Live
│   ├── config/             ✅ Live
│   ├── utils/              ✅ Live
│   ├── logger/             ✅ Live
│   ├── types/              ✅ Live
│   ├── quantum/            ✅ Live
│   ├── ui/                 ✅ Live
│   ├── seeder/             ✅ Live
│   └── typescript-config/  ✅ Live
│
├── integrations/           ← External service adapters
│   ├── meta/               ✅ LIVE — WhatsApp/Instagram
│   ├── razorpay/           🔵 Sprint 2.5 wire
│   ├── razorpayx/          ⬜ Sprint 3 wire
│   ├── shopify/            ⬜ Sprint 4 wire
│   ├── woocommerce/        ⬜ Sprint 4 wire
│   ├── shadowfax/          ⬜ Sprint 4 wire
│   ├── stripe/             ⬜ Sprint 4 wire
│   ├── ebay/               ⬜ Sprint 4 wire
│   ├── google/             ⬜ Sprint 4 wire (full)
│   ├── boguspay/           ✅ Test only
│   ├── zoho/               ⬜ Sprint 4 build
│   └── tally/              ⬜ Sprint 4 build
│
├── cloudbuild/             ← CI/CD
│   ├── deploy-api.yaml             ✅
│   ├── deploy-exons.yaml           ✅
│   ├── deploy-futureex.yaml        ✅
│   ├── deploy-workers.yaml         ✅
│   ├── deploy-webhook-whatsapp.yaml✅
│   ├── deploy-store.yaml           🔵 Sprint 2.5
│   ├── deploy-store-builder.yaml   🔵 Sprint 2.5
│   ├── deploy-pos.yaml             🔵 Sprint 2.5
│   ├── deploy-kds.yaml             🔵 Sprint 2.5
│   ├── deploy-symbiote.yaml        ⬜ Sprint 4
│   └── publish-packages.yaml       ✅
│
├── scripts/
│   ├── bump-version.sh
│   ├── test-agents.sh
│   ├── test-e2e.sh
│   ├── test-local-e2e.sh
│   ├── training/           ⬜ Sprint 2.6
│   ├── colab/              ⬜ Sprint 2.6
│   └── infra/              ⬜ Sprint 2.6
│
└── archives/               ← Old versions, reference docs
```

---

## SECTION 5: INFRASTRUCTURE STATUS

```
SERVICE                     STATUS    NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
apps/api                    ✅ LIVE   Cloud Run asia-south2
apps/workers                ✅ LIVE   Cloud Run asia-south2
apps/exons                  ✅ LIVE   Cloud Run asia-south2
apps/futureex               ✅ LIVE   Cloud Run asia-south2
apps/webhooks/whatsapp      ✅ LIVE   Cloud Run asia-south2
apps/store                  🔵 2.5    Wildcard *.futureex.store
apps/store-builder          🔵 2.5    store-builder.futureex.ai
apps/pos                    🔵 2.5    pos.futureex.ai (PWA)
apps/kds                    🔵 2.5    kds.futureex.ai (PWA)
apps/micro-exonions         ⬜ 2.6    GCE VM (e2-standard-2)
apps/symbiote               ⬜ 4      symbiote.futureex.ai (PWA)
packages/exon-core          ✅ LIVE   Artifact Registry
integrations/meta           ✅ LIVE
Upstash Redis               ✅ LIVE   Session + idempotency
Firestore                   ✅ LIVE
Pub/Sub (6+ topics)         ✅ LIVE
CI/CD Cloud Build           ✅ LIVE
Cloud Tasks                 ✅ LIVE   whatsapp-route-queue
Cloud KMS                   🔵 2.5    Integration cred encryption
Firebase Storage            🔵 2.5    Product images, voice notes
Firebase Auth               ✅ LIVE   + custom claims (Sprint 2.5)
FCM                         🔵 2.5    Push notifications
Wildcard SSL                🔵 2.5    *.futureex.store
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## SECTION 6: SPRINT HISTORY + ROADMAP

### Sprint 1 — COMPLETE ✅
```
THEME: "Wire the plumbing"
BUILT: 13 neurons, 11 role-string agents
       packages/exon-core, apps/exons, apps/futureex
       apps/webhooks/whatsapp (code complete)
       integrations/meta (verified)
       LoginGate (reverse OTP via WhatsApp)
       All CI/CD pipelines
```

### Sprint 2 — COMPLETE ✅
```
THEME: "Make it feel like a real business OS"
BUILT: 28 neurons (cumulative)
       6 isolated exonions running, 14 stubs
       29 capabilities defined + live
       Main Office UI (3-panel + mobile)
       MetricsBar, CommandPanel, ExecutionFeed,
         ControlPanel
       Add Product flow end-to-end
       useExecutionFeed, useCapability,
         useBusinessMetrics hooks
       Glass UI polish
       All 5 Sprint 1 bugs fixed

CARRY FORWARD:
  STR-008, PPL-011, MSG-004 → Sprint 2.5
  3-5 pilot onboarding → Sprint 2.5
  First ₹499 collection → Sprint 2.5
```

### Sprint 2.5 — IN PROGRESS 🔵
```
THEME: "Single tenant stable, multi-channel, real money"
DURATION: 2 weeks
TRACKS: 9
GOAL: Multi-channel commerce with unified financial truth

WHAT IT BUILDS:
  Track 1: Auth Foundation (4 user types)
           Owner / Staff / Customer / Device
           Custom claims, Staff PIN, Device QR,
           Customer OTP, middleware for all apps

  Track 2: Public Store (apps/store)
           Wildcard *.futureex.store
           Handle system, store renderer, cart,
           checkout, Razorpay + COD, order tracking

  Track 3: Store Builder MVP (apps/store-builder)
           StoreExonion (#21) + generate_store capability
           Sitemap panel, page editor, theme editor,
           publish system

  Track 4: POS Rewire (apps/pos)
           Staff PIN auth, neuron-wired commerce,
           offline queue

  Track 5: KDS Rewire (apps/kds)
           Device auth via QR, real-time order board,
           multi-channel sources

  Track 6: App Connector (Integration Hub)
           Meta WhatsApp embedded signup
           Per-org Razorpay (not platform default)
           Google OAuth, KMS-encrypted credentials

  Track 7: Platform WhatsApp Store
           One FutureEx number, all businesses listed
           Category taxonomy, customer flow, STR-008

  Track 8: Missing neurons + real Razorpay
           PAY-001/002/003/008 wired (real)
           FUL-001→005, FIN-002/003, BKG-001/002/003,
           WRK-001/002, MSG-004 (FCM), PPL-011

  Track 9: StoreExonion full activation

ARCHITECTURE RULES (this sprint):
  ✅ ALL commerce through neurons
  ✅ Store/POS/KDS never write commerce data directly
  ✅ Same neuron flow regardless of channel
  ✅ Per-org Razorpay (not platform default)
  ✅ Credentials KMS-encrypted

DONE WHEN:
  3-5 pilots onboarded, first ₹499 collected,
  "Aaj kitna hua?" returns correct answer across
  all 5 channels (web / own WA / platform WA / POS / KDS)
```

### Sprint 2.6 — PARALLEL TRACK 🟡
```
THEME: "Cost optimization for kirana tier"
DURATION: 2 weeks (runs alongside Sprint 2.5+)
SCOPE: 5 micro-exonions on fine-tuned SmolLM2-135M
       Running on GCE e2-standard-2 (8GB RAM)

STRATEGIC NOTE:
  This sprint primarily serves the KIRANA door
  (₹0–₹499/month tier). Mid-market and enterprise
  doors do not need cost optimization at this scale —
  Gemini cost is rounding error against ₹2-5L/month
  contract values. Can be deferred if needed.

5 MICRO-EXONIONS:
  catalog-micro    → reorder, categorize, stock alert
  sales-micro      → classify, attribution, fraud score
  finance-micro    → payment verify, settlement, classify
  ops-micro        → fulfillment route, notify, ETA
  analytics-micro  → anomaly, trend, daily insight

ARCHITECTURE:
  Same Exonion contract (memory, capabilities, neurons)
  DIFFERENT runtime: type='micro-model'
  Falls back to Cloud LLM on failure
  Idempotency via local Redis
  Pub/Sub event subscription (parallel to Cloud Run)

DONE WHEN:
  All 5 models pass 90%+ golden test accuracy
  VM uptime > 99%
  JSON parse failure < 5%
  Latency p95 < 500ms
```

### Sprint 3 — PLANNED ⬜
```
THEME: "Make money move correctly between any entities"
DURATION: 3 weeks
GOAL: B2B + economic operating system

TRACK A: Complete Neuron Library (262 total)
TRACK B: Activate remaining 14 exonions
TRACK C: Layer 2 — Economic system
         ECO, LDG, STL, ESC neurons
         /platform_economic_transactions
         /organisation/{orgId}/ledgers
         /platform/settlements, /platform/escrow
         Inter-org API, Settlement engine (RazorpayX)
TRACK D: Layer 3 — Governance
         GOV-001 commission engine
         GOV-002 GST tax calculation
         GOV-003 risk limits
         GOV-004/005 disputes
         GOV-006 audit logs (immutable, 7yr)
         GOV-007 GST invoice auto-generation
TRACK E: Partner + Group Foundation
         PRT neurons, agency mode, org switcher
         GRP-001/002 group foundation
TRACK F: Integration Framework + Razorpay/X wire
TRACK G: UI Expansion (orders, products, customers,
         analytics, exonion switcher, multi-org)

DONE WHEN:
  Business A can order from Business B
  Double-entry ledgers balance correctly
  Settlements process automatically via RazorpayX
  GST invoice auto-generated on every transaction
  Agency can manage client orgs
  10+ pilot businesses live
  First B2B transaction + first automated settlement
```

### Sprint 4 — PLANNED ⬜
```
THEME: "Intelligence + Integrations"
DURATION: 3 weeks
GOAL: Thinking layer + external world connection

TRACK 1: Workspaces (headline feature)
         Sandbox (raw thoughts, voice notes)
         Ideas (AI-evaluated with cross-exonion data)
         Living Docs (SOPs, policies, brand guides)
         WorkspaceExonion (#22)
         Cross-exonion consultation pattern
         Live Docs injection into exonion prompts

TRACK 2: Integration Framework
         IntegrationAdapter interface
         Shopify, WooCommerce import
         Zoho Books OAuth + sync
         Tally (XML gateway or Excel export)
         Shadowfax (logistics)
         Stripe (international payments)
         eBay (marketplace sync)
         Google (full OAuth + Maps)
         Sync rule: ONE-WAY per entity

TRACK 3: Analytics Dashboard
         Real charts, channel breakdown,
         AI insights from AnalyticsExonion
         ANL-003 weekly, ANL-004 monthly summaries

TRACK 4: Symbiote App (PWA MVP)
         Customer-facing, order tracking,
         order history, one-tap reorder,
         basic discovery (nearby businesses)

TRACK 5: Notification Center
         Unified hub, persistent history,
         actionable alerts, preferences,
         WhatsApp + in-app + push routing

ARCHITECTURE RULES (this sprint):
  ✅ Workspace never executes directly (owner approves)
  ✅ Cross-exonion consultation is structured
       (data only, not free-form chat)
  ✅ Sync is always one-way per entity type
  ✅ Failed syncs notify owner + retry w/ backoff
  ✅ Neurons own commerce truth; external = secondary
```

### Sprint 5 — PLANNED ⬜ (THE BRAIN)
```
THEME: "From reactive tool to proactive operator"
DURATION: 3 weeks
GOAL: This is where FutureEx becomes Executive AI.
      The category-defining sprint.

TRACK 1: Business Context Engine (BCX)
         /organisation/{orgId}/bcx/current
         /organisation/{orgId}/bcx/history/{date}
         BCXWorker (hourly + event-triggered)
         Insight engine + Anomaly detection
         Festival calendar integrated

TRACK 2: Prompt Architecture Layer
         packages/exon-core/src/prompt/bcx.prompt.builder.ts
         6-layer prompt system
         Per-exonion BCX field selection
         Mode detection (5 modes)
         India constraint layer
         All 22 exonions updated

TRACK 3: Proactive Agent System
         ProactiveAgentSubscriber (workers)
         8 trigger types
         Alert preferences per owner
         Quiet hours respected
         WhatsApp + in-app + push delivery

TRACK 4: Autonomous Execution
         3 permission levels (L1/L2/L3)
         L1: auto-execute, undoable 30 min
         L2: ask first, then execute
         L3: always require approval (hardcoded)
         Audit log immutable
         Permission setup in onboarding

TRACK 5: Learning Loop
         /organisation/{orgId}/learning/{eventId}
         Implicit + explicit feedback signals
         Personalization at 30+ events
         Anonymization → /platform/learning_corpus
         Foundation for future model training

TRACK 6: Business Health Dashboard
         Score 0-100 with grade
         What's working / Needs attention
         Next best 3 actions with execution buttons
         Default landing in Main Office

POST-SPRINT-5: The platform is provably uncopyable.
  Competitor cannot copy: 2 years of Indian SMB data,
  BCX, learning loop, India patterns at scale.  
```

### Sprint 6 — PLANNED ⬜ (THE EMBODIMENT)
THEME: "From 22 exonions to 5 departments that talk"
DURATION: 5 weeks (split 6.1 + 6.2)
DEPENDS: Sprint 5 complete (BCX + Learning Loop +
         6-Layer Prompt Architecture)

5 DEPARTMENT BUILDINGS:
  catalog-building   (Asha)
  sales-building     (Vikram)
  finance-building   (Priya)
  operations-building (Ramesh)
  analytics-building  (Mama-ji)

NEW PRIMITIVES:
  packages/department-core/
  packages/boardroom/
  packages/learning-pipeline/

ARCHITECTURAL RULES ADDED: 15-21

DONE WHEN:
  All 5 buildings live, boardroom protocol
  working, "Your Team" dashboard live,
  cost ≤ ₹50/org-month at 1000 orgs,
  25,000+ quality ChatML examples accumulated,
  10 pilot orgs say "feels like a real team."

UNLOCKS: Sprint 7-8 (Stage 2 LoRA training)

## SECTION 7: FIRESTORE SCHEMA REFERENCE

### Path Parity Rule
```
Collection path = ODD  segments  (/a/b/c       = 3 ✅)
Document   path = EVEN segments  (/a/b/c/d     = 4 ✅)

FIXES APPLIED IN SPRINT 1:
  /users/business       ❌ (2 segments)
  /users/business/index ✅ (3 segments)

  /auth/api-keys        ❌ (2 segments)
  /auth/index/api-keys  ✅ (3 segments)

CHECK EVERY NEW COLLECTION PATH BEFORE WRITING.
```

### Collections By Sprint
```
SPRINT 1-2 (exist):
  /organisation/{orgId}                       org profile
  /organisation/{orgId}/products              catalog
  /organisation/{orgId}/orders                orders
  /organisation/{orgId}/customers             CRM
  /organisation/{orgId}/payments              payment records
  /organisation/{orgId}/analytics/daily       ANL-001 output
  /organisation/{orgId}/notifications/outbox  notifications
  /organisation/{orgId}/stores/{storeId}      stores
  /platform_events                            execution feed
  /sessions                                   chat sessions
  /users/business/index/{userId}              users (parity fix)

SPRINT 2.5 ADDS:
  /platform/store_handles/{handle}
  /platform/catalog/categories/{categoryId}
  /platform/catalog/listings/{listingId}
  /organisation/{orgId}/stores/{storeId}/siteConfig/current
  /organisation/{orgId}/stores/{storeId}/pages/{pageId}/current
  /organisation/{orgId}/stores/{storeId}/pages/{pageId}/history/{vId}
  /organisation/{orgId}/integrations/{integrationId}
  /organisation/{orgId}/staff/{staffId}
  /organisation/{orgId}/devices/{deviceId}
  /organisation/{orgId}/shipments/{shipmentId}
  /organisation/{orgId}/bookings/{bookingId}
  /organisation/{orgId}/expenses/{expenseId}
  /organisation/{orgId}/invoices/{invoiceId}

SPRINT 3 ADDS:
  /platform_economic_transactions/{txnId}
  /organisation/{orgId}/ledgers/{ledgerId}
  /platform/ledgers/{ledgerId}
  /platform/settlements/{settlementId}
  /platform/escrow/{escrowId}
  /platform/commission_rules/{ruleId}
  /platform/audit_log/{logId}
  /platform/groups/{groupId}
  /platform/disputes/{disputeId}
  /organisation/{orgId}/partners/{partnerId}

SPRINT 4 ADDS:
  /organisation/{orgId}/workspace/sandbox/{noteId}
  /organisation/{orgId}/workspace/ideas/{ideaId}
  /organisation/{orgId}/workspace/docs/{docId}
  /organisation/{orgId}/integrations/{integrationId}/sync_log/{logId}

SPRINT 5 ADDS:
  /organisation/{orgId}/bcx/current
  /organisation/{orgId}/bcx/history/{date}
  /organisation/{orgId}/bcx/insights/{insightId}
  /organisation/{orgId}/learning/{eventId}
  /organisation/{orgId}/ai_permissions
  /organisation/{orgId}/autonomous_actions/{actionId}
  /organisation/{orgId}/alert_preferences
  /platform/learning_corpus/{corpusId}
```

---

## SECTION 8: USER PERSONAS + AUTH ROLES

### The 4 Auth Roles (Sprint 2.5)
```
Roles define WHO can DO WHAT in the system.
Different from personas. Personas are WHO buys.

OWNER     → Firebase Auth + role:'owner'
            Auth: Phone OTP via WhatsApp (reverse OTP)
            Permissions: ALL
            Sees: their own org only

STAFF     → Firebase Auth + role:'staff'
            Auth: 6-digit PIN, org-scoped
            Permissions: scoped (pos.create_order,
                         kds.view_orders, etc.)
            Sees: assigned org only

CUSTOMER  → Firebase Auth + role:'customer'
            Auth: Phone OTP (soft, on checkout)
            Permissions: track own orders only
            Sees: own purchase history

DEVICE    → Firebase Auth + role:'device'
            Auth: Device token via QR scan
            Permissions: kds.view_orders, kds.update_status
            Sees: assigned org's order board

PLATFORM_ADMIN → Internal use only
            Sees: all orgs (for support / debugging)

ALL APPS verify claims using:
  packages/auth → verifyAndExtractClaims(token)
```

### The 5 Buyer Personas (GTM-Driven)
```
Persona 1 — Aspirant / Dreamer
  Has an idea, no business yet.
  Channel: futureex.ai homepage + Workspaces
  Journey: Sandbox → Ideas → AI evaluation → Build
  Value: "I went from idea to live store in 3 days"
  Stage: Dream → Build (Sprint 4 Workspaces unlocks this)

Persona 2 — Micro Business (Kirana)
  Chaiwala, home baker, small tailor.
  Channel: WhatsApp ONLY (wa.me/futureex)
  Journey: 5 messages → store created → orders flowing
  Value: "Ab mujhe manually order nahi lena"
  Pricing: ₹0/month (free) → ₹499 when value seen

Persona 3 — Growing Business (SMB)
  Boutique, restaurant, salon.
  Channel: WhatsApp + Main Office (web)
  Journey: Onboard → Catalog → Orders → AI manages ops
  Value: "Mera business professionally run ho raha hai
          without a team"
  Pricing: ₹499–₹1,999/month

Persona 4 — Mid-Market D2C Brand (THE WEDGE)
  ₹50–500 Cr revenue. Mamaearth, Sugar, Bewakoof tier.
  Channel: futureex.ai homepage → AI Executive purchase
  Journey: Hire AI Head of Operations → expand C-suite
  Value: "We're running 3x ops with same headcount.
          And our founder finally has Saturdays back."
  Pricing: ₹1.5L–₹6L/month

Persona 5 — Enterprise Brand
  ₹500 Cr+ revenue. Nike India tier.
  Channel: futureex.ai/enterprise (gated, sales-led)
  Journey: 6-9 month cycle → pilot → full deployment
  Value: "Autonomous operations layer with full audit
          trails and guardrails"
  Pricing: ₹50L–₹2Cr/year

Persona 6 — Agency / Partner
  Digital agency, web developer, consultant.
  Channel: Partner dashboard + client orgs
  Journey: Register → create client orgs → manage → earn
  Value: "FutureEx is my delivery platform"
  Pricing: ₹5K setup + ₹2K/month per client + commission

Persona 7 — Multi-Entity / Group
  Holding company, franchise network.
  Channel: Group dashboard
  Journey: Parent org + N subsidiaries
  Value: Consolidated P&L, transfer pricing, audit
  Pricing: Custom (Sprint 4+ Group features)
```

---

## SECTION 9: AI RULES

### What Exonions NEVER Say
```
❌ Neuron, Event, Subscriber, Pub/Sub
❌ Firestore, Redis, API, Webhook
❌ Exonion, Capability, NeuronBridge, BCX
❌ Any technical term

✅ Order, Payment, Delivery, Product
✅ "Done! Your product is live."
✅ "Aapka order place ho gaya"
✅ "I've sent the confirmation to your customer"
✅ Natural business language only
```

### What Exonions SAY About Themselves
```
PUBLIC NAMES (in user-facing output):
  CoFounderExonion    → "AI Chief of Staff"
                         OR just no name (it's "the AI")
  OperationsExonion   → "AI Head of Operations"
  CatalogExonion      → "AI Head of Merchandising"
  SalesExonion        → "AI Head of Sales"
  FinanceExonion      → "AI CFO"
  MarketingExonion    → "AI Head of Growth"
  WorkspaceExonion    → "AI Strategy Advisor"
  AnalyticsExonion    → "AI Head of Analytics"
  SupportExonion      → "AI Customer Success Lead"
  StoreExonion        → "AI Store Designer"

INTERNAL TERM (in code, this doc, dev conversations):
  Always "Exonion" — preserved for clarity in code.
```

### Language Support
```
✅ Hindi
✅ Hinglish (mixed — most common)
✅ English
🔜 All Indian languages (Sprint 6+)
```

### Exonion Routing Rules
```
Any message → CoFounderExonion decides who handles it.

DOMAIN ROUTING:
  Products / catalog       → CatalogExonion
  Orders / revenue         → SalesExonion
  Money / payments         → FinanceExonion
  Operations / delivery    → OperationsExonion
  Marketing / growth       → MarketingExonion
  Customer support         → SupportExonion
  Analytics / insights     → AnalyticsExonion
  Store design             → StoreExonion
  Ideas / strategy / plans → WorkspaceExonion
  Cross-domain             → CoFounder synthesizes

CRITICAL RULES:
  CoFounder is ALWAYS the orchestrator (operational).
  WorkspaceExonion is the strategic consultant
    (idea evaluation only).
  Never route directly between non-cofounder/non-workspace
    exonions for cross-domain.

EXCEPTION (Sprint 4):
  WorkspaceExonion may FORMALLY request data from other
  exonions via the structured consultation pattern.
  Other exonions reply with data only, never opinions.
```

### India-Specific AI Behavior (Sprint 5)
```
EVERY AI RESPONSE MUST RESPECT:
  → WhatsApp > Email for customer communication
  → COD availability matters (most India SMBs)
  → Festival calendar (Diwali, Holi, Eid, Navratri,
       Dussehra, Christmas, Independence Day, etc.)
  → GST compliance in financial advice
  → Hinglish when owner speaks Hinglish (don't force English)
  → Tier-2/3 city context when relevant
  → RBI payment regulations
```

---

## SECTION 10: DEVELOPMENT RULES

### Absolute Rules (Never Break)
```
1. NEVER write cross-module direct calls
   modules/ never imports from other modules/
   Always communicate through events.

2. NEVER write to another domain's Firestore
   FinanceModule never writes to /commerce/
   Always emit event, let owner module handle.

3. ALWAYS ask for existing files before writing code
   Never write blind.
   Never assume file contents.

4. ALWAYS emit events after neuron execution
   Every state change → event emitted.
   Workers react to events asynchronously.

5. ALWAYS validate with Zod at neuron boundary
   Input schema validated before processing.
   Output schema validated before returning.

6. ALWAYS use idempotency keys
   Neurons safe to retry.
   Redis-backed deduplication.

7. NEVER expose technical terms to users
   UI speaks business language only.
   Exonions speak business language only.

8. ALL COMMERCE THROUGH NEURONS (Sprint 2.5)
   Store/POS/KDS/Symbiote never write commerce
   data directly. Always via /api/v2/* routes.

9. CREDENTIALS ALWAYS ENCRYPTED (Sprint 2.5+)
   KMS encryption before Firestore write.
   Never in plaintext, never in logs,
   never returned to frontend after storage.

10. ONE-WAY SYNC PER ENTITY (Sprint 4)
    Products: external → FutureEx (import)
    Orders:   FutureEx → external (export)
    Accounting: FutureEx → Zoho/Tally (push)
    NEVER bidirectional for same entity.
    FutureEx ledger is always source of truth.

11. CROSS-EXONION CONSULTATION IS STRUCTURED (Sprint 4)
    Only WorkspaceExonion can request data from others.
    Requests/responses are structured (data only).
    No free-form exonion-to-exonion chat.

12. WORKSPACE NEVER EXECUTES DIRECTLY (Sprint 4)
    WorkspaceExonion can RECOMMEND execution.
    Owner approves.
    THEN capability fires.

13. AUTONOMOUS EXECUTION RESPECTS PERMISSIONS (Sprint 5)
    L1 actions auto-execute (30-min undo window).
    L2 actions require approval first.
    L3 actions are HARDCODED — cannot be moved
      to lower levels.
    Every autonomous action → audit log.

14. BCX-BACKED RESPONSES (Sprint 5)
    All exonion responses must use real business data.
    Never give generic answers when BCX is available.
    Field selection per exonion is enforced.
```

### File Before Code Rule
```
BEFORE WRITING ANY CODE:
  1. Share the existing file first
  2. Understand current state
  3. Then write targeted changes

NEVER:
  - Rewrite working code
  - Assume what's in a file
  - Write code without seeing imports
```

### Firestore Path Rules
```
PARITY RULE:
  Collection path = ODD  segments
  Document   path = EVEN segments

ALWAYS verify path parity before writing.
```

### Dockerfile Rules
```
✅ No NODE_ENV=production in builder stage
✅ --include=dev always
✅ No --ignore-scripts for Next.js
✅ Single stage for Next.js apps
✅ Two-stage ok for Node services
✅ CMD ["node", "server.js"] for Next.js standalone
```

### Auth Middleware Rules (Sprint 2.5)
```
EVERY PROTECTED ROUTE MUST USE MIDDLEWARE:
  store-builder.futureex.ai → owner only
  pos.futureex.ai           → staff + owner
  kds.futureex.ai           → device + owner
  *.futureex.store          → public; auth at checkout
  /connect/*                → owner only
  /workspace/*              → owner only (Sprint 4)
  /admin/*                  → platform_admin only
```

---

## SECTION 11: HOW TO USE THIS PROMPT

### Starting A New Session
```
"Load FutureEx Master Prompt v6.0.
 Current sprint: Sprint [N].
 Current track: [Track X].
 Current task: [specific task].
 [Paste relevant context or files]"
```

### Task Types
```
ARCHITECTURE QUESTION:
"Referring to v6.0, how should [X] connect
 to the capability layer?"

CODE TASK:
"Using v6.0 as context, implement [task].
 Here is the existing file: [paste file]"

DECISION:
"Given v6.0 strategy, should we build
 [X] or [Y] for [situation]?"

BUG FIX:
"v6.0 context. Bug: [describe].
 Relevant files: [paste files]"

GTM / POSITIONING (use other doc):
Switch to GTM_PLAYBOOK_v1.0.md
```

### Key URLs
```
API:           fexverse-api-vrebnvygea-em.a.run.app
EXONS:         fexverse-exons-vrebnvygea-em.a.run.app
WEB:           fexverse-web (Cloud Run)

PRODUCT URLS:
futureex.ai                 — main (mid-market homepage)
futureex.ai/enterprise      — enterprise (gated)
*.futureex.store            — customer storefronts
store-builder.futureex.ai   — store design studio
pos.futureex.ai             — Point of Sale (PWA)
kds.futureex.ai             — Kitchen Display (PWA)
symbiote.futureex.ai        — customer app (PWA, Sprint 4)
wa.me/futureex              — WhatsApp entry (kirana door)
```

### The AI Assistant Should Always
```
✅ Ask for existing files before writing code
✅ Respect neuron contracts (input/output/events)
✅ Never write cross-module direct calls
✅ Always emit events (never direct writes to other domains)
✅ Follow Firestore parity rule (odd=collection, even=doc)
✅ Use business language in all user-facing text
✅ Flag anything that contradicts this architecture
✅ Route through CoFounderExonion for cross-domain operational
✅ Route through WorkspaceExonion for cross-domain strategic
✅ Maintain memory isolation per exonion namespace
✅ All WhatsApp sending via integrations/meta only
✅ Stage advancement via stage.manager.ts (not LLM)
✅ NeuronBridge = write/execute only
✅ Respect AI permission levels (L1/L2/L3) — Sprint 5+
✅ Use BCX in all responses where available — Sprint 5+
✅ Never expose technical terms — always business language
```

---

## SECTION 12: WHAT CHANGED v5.0 → v6.0

```
v5.0 → v6.0 CHANGES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CATEGORY DEFINED
   v5.0: "Programmable economic operating system"
   v6.0: "Executive AI" — a new category
         (Programmable economic OS remains the
          architectural truth underneath)

2. SECTION 0 ADDED
   Explicit guidance: this is the CODING context.
   Strategy and positioning live in
   GTM_PLAYBOOK_v1.0.md.

3. THE 6-STAGE USER JOURNEY
   The tagline "Dream. Chat. Build. Launch. Manage. Market."
   is now a literal architectural backbone, mapped to
   sprints. Every feature must answer "which stage."

4. THREE DOORS BUSINESS MODEL
   Mid-market (futureex.ai) / Enterprise (gated) /
   Kirana (WhatsApp). Each with its own pricing, model
   selection, and surface — but ONE platform underneath.

5. EXONIONS: 20 → 22
   v5.0: 20 exonions
   v6.0: 22 exonions
         + StoreExonion (#21, Sprint 2.5)
         + WorkspaceExonion (#22, Sprint 4)

6. PUBLIC NAMES FOR EXONIONS
   Each exonion now has both an internal name
   ("CatalogExonion") and a public-facing name
   ("AI Head of Merchandising").

7. AI EXECUTIVE PRICING
   New pricing model for mid-market: per-AI-Executive
   (₹1.5L–₹6L/month). Sold as "team members" not
   features.

8. BCX ADDED AS FIRST-CLASS CONCEPT
   Business Context Engine documented in Section 3.
   Schema, refresh model, usage pattern.
   "BCX is what makes Executive AI real."

9. 6-LAYER PROMPT ARCHITECTURE
   Sprint 5 prompt system documented.
   Replaces all generic system prompts.

10. CROSS-EXONION CONSULTATION PATTERN
    New architectural primitive (Sprint 4).
    Only WorkspaceExonion can request data from others.
    Structured request/response, not free-form.

11. LIVE DOCS INJECTION PATTERN
    Sprint 4 — workspace docs marked `isLive: true`
    automatically inject into relevant exonion prompts.
    "AI doesn't make up policy."

12. AUTONOMOUS EXECUTION + 3 PERMISSION LEVELS
    Sprint 5 — L1 auto-execute / L2 ask first /
    L3 hardcoded approval. Audit log immutable.
    30-minute undo window for L1.

13. SPRINT HISTORY UPDATED
    Sprint 1, 2: Complete
    Sprint 2.5: In progress (replaces v5.0's "Sprint 2")
    Sprint 2.6: Parallel track (kirana cost optimization)
    Sprint 3: Planned (economic layer)
    Sprint 4: Planned (Workspaces + Integrations)
    Sprint 5: Planned (the brain)

14. FIRESTORE COLLECTIONS BY SPRINT
    New Section 7 — every collection path mapped to
    the sprint that introduces it.

15. 4 AUTH ROLES (Sprint 2.5) + 7 PERSONAS
    Auth roles (Owner/Staff/Customer/Device) separated
    from buyer personas. Both documented in Section 8.

16. NEW ABSOLUTE RULES (8-14)
    Rules added for: commerce-through-neurons,
    KMS-encrypted credentials, one-way sync,
    cross-exonion consultation, workspace approval,
    autonomous permissions, BCX-backed responses.

17. SECTION 13 ADDED
    Phased AI Evolution: prompts → LoRA adapter →
    FutureEx Foundation Model. The 3-stage moat.

18. GLOSSARY ADDED
    All custom terms defined once at the bottom.

19. INTEGRATION FRAMEWORK
    packages/integrations/ documented as new
    Sprint 4 package. Adapter pattern formalized.

20. SYMBIOTE PROMOTED FROM CONCEPT TO MVP
    PWA in Sprint 4 (apps/symbiote).
    Native app deferred to Sprint 6+.
```

---

## SECTION 13: PHASED AI EVOLUTION (THE MODEL ROADMAP)

```
FutureEx's AI architecture evolves across 3 stages.
Each stage funds and trains the next.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STAGE 1 — PROMPT ARCHITECTURE (Sprint 5)
  Status: Active development
  Sprint: 5
  
  WHAT IT IS:
    Sophisticated context injection layer
    BCX powers every LLM call
    Live Docs inject owner's policies
    6-layer prompt structure
    Learning loop captures every interaction
  
  MODELS USED:
    Cloud LLMs (Gemini, GPT-4o, Claude)
    SmolLM2-135M for kirana tier (Sprint 2.6)
  
  WHY THIS WORKS:
    Already more powerful than any competitor
    because of REAL business data behind it.
    Deployable now using existing LLMs.
  
  COST PROFILE:
    Mid-market: $0.50–$2/business/day (negligible
                vs ₹1.5L–₹6L/month contract value)
    Kirana: ~$0.05/business/day (micro-exonions)
  
  REVENUE FUNDED:
    This stage pays for the data collection that
    enables Stage 2.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STAGE 2 — FINE-TUNED ADAPTER (Sprint 7-8)
  Status: Designed, not built
  Trigger: When Stage 1 has accumulated 12+ months
           of anonymized data across 100+ businesses
  
  WHAT IT IS:
    LoRA fine-tuning on a strong base model
    (likely Qwen 2.5 or Llama 4 class)
    Trained on anonymized FutureEx corpus
    Indian business language native
    Hinglish-first
    Understands SMB patterns deeply
  
  MODELS USED:
    Custom adapters per exonion type
    Hosted on GPU infra (or partner)
  
  COST PROFILE:
    50-70% cheaper than raw API
    Faster inference (smaller, specialized)
  
  STRATEGIC IMPACT:
    Reduces dependency on OpenAI/Google.
    Margins expand significantly.
    Indian-context performance leapfrogs
    generic LLM competitors.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STAGE 3 — FUTUREEX FOUNDATION MODEL (Year 2+)
  Status: Vision
  Trigger: 1000+ businesses on platform,
           millions of transactions in corpus
  
  WHAT IT IS:
    Full custom foundation model
    Trained on millions of Indian SMB transactions
    Every exonion runs on FFM
    No external LLM dependency
    Complete data privacy
  
  COST PROFILE:
    Marginal cost of inference approaches zero
    Compute owned, not rented
  
  STRATEGIC IMPACT:
    THIS is the actual uncopyable moat.
    Competitors cannot replicate without:
      → 2+ years of Indian SMB transaction data
      → BCX corpus across thousands of businesses
      → Learning loop trained on real outcomes
      → Festival + India-specific patterns at scale
      → Hinglish business vocabulary at scale
    
    A competitor can copy a prompt in 1 hour.
    A competitor cannot copy the corpus.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY THIS ROADMAP MATTERS FOR CODING DECISIONS:

1. EVERY EXONION CALL MUST CAPTURE LEARNING DATA
   Sprint 5 Track 5 (Learning Loop) is non-negotiable.
   Without it, Stage 2 and Stage 3 have no fuel.

2. ANONYMIZATION PIPELINE IS A FOUNDATION FEATURE
   Build it correctly in Sprint 5 — it's the input
   to everything that follows.

3. EXONION ARCHITECTURE MUST STAY MODEL-AGNOSTIC
   Today: Gemini behind exonion X.
   Tomorrow: LoRA adapter behind exonion X.
   Year 2: FFM behind exonion X.
   The RUNTIME field on ExonionDefinition makes
   this swap possible without app changes.

4. CONSENT FRAMEWORK MUST BE FIRST-CLASS
   Owners opt in to anonymized corpus contribution.
   Built in Sprint 5 onboarding flow.
   Without consent → no corpus → no Stage 2/3.
```

---

## SECTION 14: GLOSSARY

```
All custom terms used in this document, defined once.
Use this when onboarding engineers or interpreting code.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEURON
  Atomic unit of business action.
  Has input/output schemas, emits events,
  is idempotent and stateless.
  Total: 262 across 4 layers (L1-L4).
  Lives in /modules/{domain}/src/neurons/

EXONION
  Isolated AI persona with memory namespace,
  capabilities, neuron access, and personality.
  Total: 22.
  Lives in packages/exonions/src/definitions/
  Public-facing name: "AI Executive" or by role.

CAPABILITY
  Named outcome that maps to a flow of neurons.
  User → Capability → Neurons → Events → Result.
  Total: 29.
  Examples: setup_catalog, place_order, evaluate_idea.

BCX (BUSINESS CONTEXT ENGINE)
  Living, structured understanding of each business
  computed from operational data — not user input.
  Refreshed hourly + after key events.
  Injected into every exonion prompt (Sprint 5+).

NEURON BRIDGE
  Write/execute only abstraction over neurons,
  used by exonions. Provides safe interface
  without exposing internal neuron logic.

CO-FOUNDER EXONION
  Operational orchestrator. Routes any message to
  the right specialist. Public-facing name:
  "AI Chief of Staff."

WORKSPACE EXONION
  Strategic orchestrator. Evaluates ideas by
  consulting other exonions. Only exonion
  permitted to formally request data from others.
  Sprint 4 addition. Public name: "AI Strategy Advisor."

WORKSPACES
  The thinking layer. Three components:
    → Sandbox (raw thoughts, voice notes)
    → Ideas (AI-evaluated concepts)
    → Living Docs (SOPs, policies, brand guides)
  Sprint 4 deliverable.

LIVE DOC
  A workspace doc marked `isLive: true`.
  Automatically injected into relevant exonion
  prompts when handling tasks in that domain.

EXECUTION FEED
  Real-time stream of business events shown in
  Main Office. Powered by /platform_events
  Firestore listener.

CONTROL PANEL
  Slide-in drawer in Main Office UI.
  Context-sensitive: shows order details,
  product editor, customer view, etc.

COMMAND PANEL
  Left column of Main Office UI.
  Quick actions + commands ("Add Product",
  "Daily Summary", etc.).

METRICS BAR
  Top transparent strip in Main Office.
  Shows revenue today, orders today, status.

MAIN OFFICE
  The Sprint 2 dashboard. The owner's command
  center for their business. 3-panel layout.

EXECUTIVE AI
  The category FutureEx defines and owns.
  AI that decides AND executes — not just generates.
  Distinct from Generative AI.

LEARNING LOOP
  Sprint 5 system that captures every interaction,
  measures outcomes 24h/7d later, and feeds back
  into model improvement.

PROACTIVE AGENT
  Sprint 5 capability — AI that initiates without
  being asked. Triggered by BCX patterns / anomalies.

AUTONOMOUS EXECUTION
  Sprint 5 capability — AI executes routine tasks
  within owner-defined permission boundaries.
  3 levels: L1 auto / L2 ask first / L3 always approve.

MICRO-EXONION
  Sprint 2.6 — exonion whose runtime is a fine-tuned
  small language model (SmolLM2-135M) running locally.
  Same contract as cloud exonions, different runtime.

SYMBIOTE
  The customer-facing app (PWA in Sprint 4,
  native in Sprint 6+). Connects buyers to
  businesses on the FutureEx platform.

PLATFORM WHATSAPP STORE
  Sprint 2.5 Track 7 — single FutureEx WhatsApp
  number where customers discover and order from
  ANY listed business. Two-sided network seed.

STORE HANDLE
  Auto-generated subdomain for each business store.
  Example: kiran.futureex.store.
  Stored in /platform/store_handles/{handle}.

EXONION RUNTIME
  Field on ExonionDefinition specifying execution mode:
    → cloud-llm  (Gemini, GPT-4o, Claude)
    → micro-model (local SmolLM2 via Ollama)
  Allows model swap without app code changes.

ECONOMIC TRANSACTION
  Sprint 3 concept — single source of truth for
  inter-org transactions on the platform.
  Stored in /platform_economic_transactions/.

LEDGER ENTRY
  Sprint 3 concept — double-entry bookkeeping
  record. Every economic transaction creates
  matched debit/credit entries.

SETTLEMENT
  Sprint 3 concept — instruction to RazorpayX
  to move money between parties after a
  transaction completes.

ESCROW
  Sprint 3 concept — funds held by platform
  pending fulfillment of conditions.

GOVERNANCE LAYER
  Sprint 3 deliverable — commission rules, GST,
  risk limits, disputes, audit logs, GST invoices.

GROUP
  Sprint 3+ concept — collection of organisations
  under common ownership (holding company, franchise).

PARTNER / AGENCY
  Sprint 3 concept — entity that manages multiple
  client orgs on the platform.

INTEGRATION ADAPTER
  Sprint 4 — implementation of IntegrationAdapter
  interface for an external service (Shopify, Zoho,
  Tally, etc.). Lives in /integrations/{vendor}/.

THE 6-STAGE JOURNEY
  Dream → Chat → Build → Launch → Manage → Market.
  The architectural backbone mapped from the tagline.
  Every feature serves a stage.

THE THREE DOORS
  Mid-market (futureex.ai) / Enterprise (gated) /
  Kirana (WhatsApp). Three GTM surfaces, one platform.

THE BRAIN
  Sprint 5 = the brain.
  BCX + Prompt Architecture + Proactive Agents +
  Autonomous Execution + Learning Loop.
  This is what makes Executive AI real.
```

---

**END OF MASTER PROMPT v6.0**

```
Version:        6.0
Date:           2026
Sprint:         2.5 — In Progress
Companion:      GTM_PLAYBOOK_v1.0.md
Neurons:        262 defined, 28 built, 234 pending
Exonions:       22 defined, 6 running, 16 pending
Capabilities:   29 defined + live
Auth Roles:     4 (Owner/Staff/Customer/Device)
Personas:       7 buyer types
Doors:          3 GTM surfaces
Stages:         6-stage Dream→Market journey
AI Evolution:   3 stages (Prompt → LoRA → FFM)
```