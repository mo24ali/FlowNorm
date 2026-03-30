# Fintech Data Aggregation & Normalization MVP

A production-ready B2B fintech solution that solves data aggregation and normalization for credit scoring and cash flow visibility.

## Core Problem Solved
Financial institutions struggle to consolidate fragmented data from multiple sources. This solution:
1. **Ingests** messy CSV files and API data.
2. **Normalizes** them into a canonical schema using self-healing logic.
3. **Detects Anomalies** automatically to flag data quality issues.
4. **Exposes** standardized data via REST APIs for downstream credit scoring.

## Tech Stack
- **Backend**: FastAPI (Python 3.11), Pandas, Pydantic, SQLAlchemy
- **Frontend**: React, Vite, TailwindCSS, Lucide-React
- **Database**: PostgreSQL (SQLAlchemy models ready for AWS RDS)
- **Infrastructure**: Terraform (AWS VPC, RDS, Lambda)
- **CI/CD**: GitHub Actions (.github/workflows/deploy.yml)

## Architecture
```text
[ Data Sources ] --(CSV/API)--> [ FastAPI Ingestion ]
                                    | (Background)
                                    v
                          [ Normalization Engine ] 
                                    | (Self-Healing)
                                    +--> [ Pydantic Validator ]
                                    +--> [ Date/Amount Cleaner ]
                                    v
[ Monitoring Dashboard ] <--(API)-- [ PostgreSQL Storage ]
```

## Self-Healing Logic
- **Flexible Date Parsing**: Automatically detects and corrects 5+ different date formats.
- **Currency Cleaning**: Handles symbols ($, €), commas, and whitespace in amount fields.
- **Anomaly Detection**: Flags records with missing descriptions, zero amounts, or unparseable dates.
- **Retries & DLQ**: Simulated in this MVP, ready for AWS Step Functions.

## Getting Started

### 1. Backend (API)
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Frontend (Dashboard)
```bash
cd frontend
npm install
npm run dev
```

### 3. Usage
- Open `http://localhost:5173` (Frontend)
- Click **"Import CSV"** and select `sample_messy_data.csv` (provided in root)
- Watch the **Real-time Flow** and **Anomaly Trace** update as data is normalized.

## API Documentation
- `POST /ingest/file`: Upload a CSV for normalization. Returns `task_id`.
- `GET /tasks/{task_id}`: Monitor ingestion status.
- `GET /transactions`: Retrieve latest normalized transactions.
- `GET /anomalies`: Get list of records flagged by the engine.
- `GET /monitor/stats`: Get system operational health.

## Infrastructure
Terraform files are located in `/terraform`. To deploy to AWS:
```bash
cd terraform
terraform init
terraform apply -auto-approve
```
# FlowNorm
