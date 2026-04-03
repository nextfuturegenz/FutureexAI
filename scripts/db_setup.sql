-- ============================================================
-- Business AI Training Dataset - Database Setup
-- Run this ONCE on your GCP PostgreSQL instance
-- PostgreSQL 18.2 compatible
-- ============================================================

-- STEP 1: Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify it installed correctly
SELECT extname, extversion 
FROM pg_extension 
WHERE extname = 'vector';

-- ============================================================
-- STEP 2: Create training_samples table (CORE TABLE)
-- ============================================================
CREATE TABLE IF NOT EXISTS training_samples (
    id                    SERIAL PRIMARY KEY,
    sample_id             VARCHAR(20) UNIQUE NOT NULL,
    batch_id              VARCHAR(20) NOT NULL,
    sprint                VARCHAR(10) DEFAULT 'SPRINT-1',
    generated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_model          VARCHAR(50) NOT NULL,
    category              VARCHAR(50) NOT NULL,
    subcategory           VARCHAR(50),
    industry              VARCHAR(50),
    geography             VARCHAR(50),
    business_stage        VARCHAR(50),
    instruction           TEXT NOT NULL,
    problem_breakdown     TEXT,
    strategic_options     TEXT,
    recommended_decision  TEXT,
    execution_plan        TEXT,
    risks_and_mitigation  TEXT,
    full_output           TEXT,
    word_count            INTEGER DEFAULT 0,
    has_india_context     BOOLEAN DEFAULT FALSE,
    quality_score         FLOAT DEFAULT 0.0,
    quality_flag          VARCHAR(10) DEFAULT 'PENDING',
    embedding             vector(768),
    is_deduplicated       BOOLEAN DEFAULT FALSE,
    is_used_in_training   BOOLEAN DEFAULT FALSE,
    critique_output       TEXT,
    improved_output       TEXT,
    notes                 TEXT
);

-- ============================================================
-- STEP 3: Create generation_log table (CHECKPOINT TABLE)
-- ============================================================
CREATE TABLE IF NOT EXISTS generation_log (
    id                    SERIAL PRIMARY KEY,
    batch_id              VARCHAR(20) UNIQUE NOT NULL,
    account_id            VARCHAR(50),
    run_started_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    run_ended_at          TIMESTAMP,
    model_used            VARCHAR(50),
    category              VARCHAR(50),
    subcategory           VARCHAR(50),
    prompts_attempted     INTEGER DEFAULT 0,
    prompts_succeeded     INTEGER DEFAULT 0,
    prompts_failed        INTEGER DEFAULT 0,
    last_sample_id        VARCHAR(20),
    last_sample_index     INTEGER DEFAULT 0,
    status                VARCHAR(20) DEFAULT 'RUNNING',
    error_log             TEXT,
    session_notes         TEXT
);

-- ============================================================
-- STEP 4: Create category_stats table (TRACKING TABLE)
-- ============================================================
CREATE TABLE IF NOT EXISTS category_stats (
    id                    SERIAL PRIMARY KEY,
    category              VARCHAR(50) NOT NULL,
    subcategory           VARCHAR(50),
    total_generated       INTEGER DEFAULT 0,
    total_passed          INTEGER DEFAULT 0,
    total_failed          INTEGER DEFAULT 0,
    total_review          INTEGER DEFAULT 0,
    avg_quality_score     FLOAT DEFAULT 0.0,
    last_updated          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category, subcategory)
);

-- ============================================================
-- STEP 5: Create prompt_templates table
-- ============================================================
CREATE TABLE IF NOT EXISTS prompt_templates (
    id                    SERIAL PRIMARY KEY,
    template_id           VARCHAR(20) UNIQUE NOT NULL,
    prompt_type           VARCHAR(30) NOT NULL,
    category              VARCHAR(50) NOT NULL,
    subcategory           VARCHAR(50),
    template_text         TEXT NOT NULL,
    times_used            INTEGER DEFAULT 0,
    avg_quality_score     FLOAT DEFAULT 0.0,
    is_active             BOOLEAN DEFAULT TRUE,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- STEP 6: Create indexes for fast queries
-- ============================================================

-- Fast lookup by category
CREATE INDEX IF NOT EXISTS idx_samples_category 
ON training_samples(category);

-- Fast lookup by quality
CREATE INDEX IF NOT EXISTS idx_samples_quality 
ON training_samples(quality_flag);

-- Fast lookup by model
CREATE INDEX IF NOT EXISTS idx_samples_model 
ON training_samples(source_model);

-- Fast checkpoint resume
CREATE INDEX IF NOT EXISTS idx_genlog_status 
ON generation_log(status);

-- Fast batch lookup
CREATE INDEX IF NOT EXISTS idx_samples_batch 
ON training_samples(batch_id);

-- Fast stats update
CREATE INDEX IF NOT EXISTS idx_stats_category 
ON category_stats(category, subcategory);

-- ============================================================
-- STEP 7: Pre-populate category_stats with all categories
-- ============================================================
INSERT INTO category_stats (category, subcategory) VALUES
    ('startup_validation', 'idea_testing'),
    ('startup_validation', 'pmf_analysis'),
    ('startup_validation', 'competitor_analysis'),
    ('startup_validation', 'customer_discovery'),
    ('marketing_strategy', 'brand_positioning'),
    ('marketing_strategy', 'content_marketing'),
    ('marketing_strategy', 'social_media'),
    ('marketing_strategy', 'influencer_marketing'),
    ('marketing_strategy', 'seo_strategy'),
    ('gtm_strategy', 'launch_planning'),
    ('gtm_strategy', 'channel_selection'),
    ('gtm_strategy', 'partnership_strategy'),
    ('gtm_strategy', 'market_entry'),
    ('sales_communication', 'cold_outreach'),
    ('sales_communication', 'objection_handling'),
    ('sales_communication', 'sales_copy'),
    ('sales_communication', 'pitch_deck_advice'),
    ('pricing_models', 'subscription_pricing'),
    ('pricing_models', 'freemium_strategy'),
    ('pricing_models', 'price_sensitivity'),
    ('pricing_models', 'competitive_pricing'),
    ('growth_strategy', 'user_acquisition'),
    ('growth_strategy', 'retention_strategy'),
    ('growth_strategy', 'referral_programs'),
    ('growth_strategy', 'expansion_strategy'),
    ('customer_support', 'support_scripts'),
    ('customer_support', 'escalation_handling'),
    ('customer_support', 'refund_scenarios'),
    ('customer_support', 'onboarding_flows'),
    ('business_decisions', 'hiring_decisions'),
    ('business_decisions', 'pivot_analysis'),
    ('business_decisions', 'budget_allocation'),
    ('business_decisions', 'vendor_selection')
ON CONFLICT (category, subcategory) DO NOTHING;

-- ============================================================
-- STEP 8: Verification queries - run after setup
-- ============================================================

-- Check all tables created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check pgvector is working
SELECT typname 
FROM pg_type 
WHERE typname = 'vector';

-- Check category_stats populated
SELECT COUNT(*) as total_categories 
FROM category_stats;

-- ============================================================
-- SETUP COMPLETE
-- Expected output:
-- Tables: 4 created
-- pgvector: 1 row returned
-- Categories: 33 rows
-- ============================================================