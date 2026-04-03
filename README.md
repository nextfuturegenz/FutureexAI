# Business AI Dataset Generator

Synthetic data generation pipeline for training a
compact Business Intelligence model (~1B parameters).

## Quick Start

### Step 1: Clone
git clone https://github.com/YOUR_USERNAME/business-ai-datagen
cd business-ai-datagen

### Step 2: Add Colab Secrets
In Colab sidebar → 🔑 Secrets → Add:
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD
- ACCOUNT_ID (ACCOUNT-1, ACCOUNT-2, or ACCOUNT-3)

### Step 3: Run Database Setup (Once only)
Run scripts/db_setup.sql on your GCP PostgreSQL instance

### Step 4: Open Notebook
notebooks/data_generator.ipynb
Run cells in order

## Parallel Accounts Setup

| Account   | Model    | Categories                        |
|-----------|----------|-----------------------------------|
| ACCOUNT-1 | qwen     | startup_validation, gtm, pricing  |
| ACCOUNT-2 | deepseek | pmf, pivot, retention, hiring     |
| ACCOUNT-3 | phi      | support, social_media, content    |

All accounts write to the same GCP PostgreSQL database.

## Dataset Targets

| Model    | Target  |
|----------|---------|
| Qwen     | 20,000  |
| DeepSeek | 15,000  |
| Phi      | 15,000  |
| Total    | 50,000  |

## Resume After Session Ends
Just run the notebook again.
Pipeline auto-resumes from last checkpoint.