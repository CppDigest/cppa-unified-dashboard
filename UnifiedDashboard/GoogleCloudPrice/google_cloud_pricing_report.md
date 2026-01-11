# Google Cloud Deployment Pricing Report

## Project Overview

This deployment consists of two batch processing projects: a daily data scraper that monitors GitHub repositories, Slack channels, and mailing lists, and a monthly processor that downloads WG21 papers, converts them to Markdown format, and creates automated Pull Requests.

### Project Scope

- GitHub Repositories: 172 repositories (1 main Boost repository + 171 submodules), generating ~5,000 API requests per day for commits, PRs with reviews/comments, and issues with comments
- Slack Channels: 209 public channels in Cpplang Slack team, generating ~2,000 messages per day
- Mailing List: Isocpp mailing list (less than 200 messages per day)
- Data Processing: WG21 paper conversion (PDF/HTML to Markdown) and automated PR creation

## Architecture

### Project 1: Daily Data Scraper

- Purpose: Monitor and collect data from multiple sources to maintain a database of Boost community activity
- Schedule: Runs once per day during off-peak hours
- Workflow: Collects GitHub data (172 repositories), Slack messages (209 channels), mailing list data (converts to Markdown and pushes to GitHub), and monitors WG21 papers for updates
- Runtime: ~2 hours per day
- Resources: 1 vCPU / 2 GB RAM (2 GB container image with conversion tools)

### Project 2: Monthly WG21 Paper Processor

- Purpose: Download documentations from the wg21 paper website, convert them from PDF/HTML to Markdown, and contribute them to the wg21 paper GitHub repository via automated Pull Requests
- Schedule: Triggered by Project 1 when WG21 papers are updated (typically once per month)
- Workflow: Downloads papers, converts to Markdown (PDF: `docling` -> `pdfplumber` -> OpenAI; HTML: `pandoc`), creates Pull Requests (one per minute rate limit)
- Runtime: ~2 hours per month
- Resources: 4 vCPU / 8 GB RAM (8 GB container image with conversion tools)

## Price Details by Service

### 1. Google Cloud SQL

Purpose: Core database for storing scraped data

Assumptions:

- Active Time: 62 hours/month (~60h from Project 1 + 2h from Project 2)
- Current Database size: at most 3GB
- Instance: `db-f1-micro` (Shared Core)
- Region: us-central1 (Iowa)

| Component                    | Price Rate           | Monthly Cost     | Notes                             |
| ---------------------------- | -------------------- | ---------------- | --------------------------------- |
| **Instance (db-f1-micro)**   | $0.0105 / hour       | **$0.65**        | 62 hours active time              |
| **Storage (SSD - 10GB Min)** | $0.17 / GB per month | **$1.70**        | Minimum 10GB storage              |
| **Backups (3GB actual)**     | $0.08 / GB per month | **$0.24**        | 3GB actual backup storage         |
| **Networking (Private IP)**  | $0.00                | **$0.00**        | Private IP within VPC (no charge) |
| **TOTAL**                    |                      | **~$2.59/month** |                                   |

Reference: [Cloud SQL Pricing](https://cloud.google.com/sql/pricing)

### 2. Google Cloud Run

Purpose: Execute batch jobs (Project 1 and Project 2)

#### Project 1: Daily Scraper

- Runtime: ~2 hours/day = ~60 hours/month
- Resources: 1 vCPU / 2 GB RAM
- Compute: 216,000 vCPU-seconds/month
- Memory: 432,000 GiB-seconds/month

#### Project 2: Monthly Git Processor

- Runtime: 2 hours/month
- Resources: 4 vCPU / 8 GB RAM
- Compute: 28,800 vCPU-seconds/month (4 vCPU × 7,200 seconds)
- Memory: 57,600 GiB-seconds/month (8 GB × 7,200 seconds)

#### Free Tier Limits (Per Account)

- First 240,000 vCPU-seconds/month: FREE
- First 450,000 GiB-seconds/month: FREE

#### Excess Cost Calculation

- Total Compute: 244,800 vCPU-seconds/month (216,000 + 28,800)
  - Free Tier: 240,000 vCPU-seconds/month
  - Excess: 4,800 vCPU-seconds
  - Cost: 4,800 × $0.000018/vCPU-second ≈ $0.09/month
- Total Memory: 489,600 GiB-seconds/month (432,000 + 57,600)
  - Free Tier: 450,000 GiB-seconds/month
  - Excess: 39,600 GiB-seconds
  - Cost: 39,600 × $0.000002/GiB-second ≈ $0.08/month

#### Price without free tier

- Total Compute: 244,800 vCPU-seconds/month (216,000 + 28,800)
  - Cost: 244,800 × $0.000018/vCPU-second ≈ $4.41/month
- Total Memory: 489,600 GiB-seconds/month (432,000 + 57,600)
  - Cost: 489,600 × $0.000002/GiB-second ≈ $0.98/month

Total Cloud Run Cost (without free tier): $5.39/month

Total Cloud Run Cost (with free tier): $0.17/month

Reference: [Cloud Run Pricing & Free Tier](https://cloud.google.com/run/pricing)

### 3. Artifact Registry

Purpose: Store container images for Cloud Run jobs

- Image Size: 10 GB
- Pricing: $0.10 per GB/month after first 0.5 GB
- Calculation:
  - (10 GB - 0.5 GB) × $0.10 = $0.95/month (with free tier)
  - 10 GB × $0.10 = $1.00/month (without free tier)

Reference: [Artifact Registry Pricing](https://cloud.google.com/artifact-registry/pricing)

### 4. Networking (Egress)

Purpose: Data transfer out of Google Cloud to external services

- Usage: ~2 GB/month consisting of:
  - GitHub API requests (commits, PRs, issues, comments)
  - Git operations (clone, push, pull requests)
  - Slack API requests (channel messages retrieval)
  - Mailing list data retrieval (HTTP requests)
- Pricing: ~$0.12 per GB (Premium Tier)
- Free Tier: First 1 GB/month is free
- Calculation:
  - (2 GB - 1 GB) × $0.12 = $0.12/month (with free tier)
  - 2 GB × $0.12 = $0.24/month (without free tier)

Reference: [VPC Network Pricing](https://cloud.google.com/vpc/network-pricing)

### 5. Cloud Scheduler

Purpose: Schedule daily and monthly jobs

- Jobs: 1 active job (schedules Project 1 daily; Project 2 is triggered programmatically by Project 1 when WG21 papers are updated)
- Pricing: $0.10 per job per month
- Free Tier: First 3 jobs per billing account are free
- Cost:
  - $0.00/month (with free tier)
  - 1 job × $0.10 = $0.10/month (without free tier)

Reference: [Cloud Scheduler Pricing](https://cloud.google.com/scheduler/pricing)

### 6. Google Cloud Logging

Purpose: Store and analyze log data from applications and services

- Usage: Logs from Cloud Run jobs, Cloud SQL, and API requests
- Pricing: $0.50 per GB/month for ingested logs (after free tier)
- Free Tier: First 50 GB/month of ingested logs is free
- Assumptions:
  - Estimated log volume: ~5 GB/month (application logs, API request logs, error logs)
- Calculation:
  - Within free tier: $0.00/month (5 GB < 50 GB free tier)
  - Without free tier: 5 GB × $0.50 = $2.50/month

Reference: [Cloud Logging Pricing](https://cloud.google.com/logging/pricing)

### 7. Google Cloud Secret Manager

Purpose: Securely store and manage API keys, passwords, and other sensitive data

- Usage: Store secrets for GitHub API tokens, Slack API tokens, database credentials, and other sensitive configuration
- Pricing: $0.06 per secret per month + $0.03 per 10,000 secret versions accessed
- Free Tier: First 6 secrets per month are free
- Assumptions:
  - Estimated secrets: 5 secrets (GitHub token, Slack token, database password, mailing list credentials, OpenAI API key)
  - Secret access: ~1,000 accesses/month (read operations during job execution)
- Calculation:
  - Secrets: 5 secrets (within free tier of 6) = $0.00/month
  - Secret access: 1,000 accesses = 0.1 × 10,000 = $0.00/month (minimal cost)
  - Total: $0.00/month (with free tier)
  - Without free tier: 5 secrets × $0.06 = $0.30/month

Reference: [Secret Manager Pricing](https://cloud.google.com/secret-manager/pricing)

### 8. Google Cloud Monitoring

Purpose: Monitor application performance, uptime, and resource metrics

- Usage: Metrics collection from Cloud Run, Cloud SQL, and custom application metrics
- Pricing: $0.258 per million metric data points ingested
- Free Tier: First 150 MB/month of metric data is free
- Assumptions:
  - Estimated metrics: ~500,000 data points/month (from Cloud Run jobs, Cloud SQL, and custom metrics)
  - Metric size: ~100 bytes per data point = ~50 MB/month
- Calculation:
  - Within free tier: $0.00/month (50 MB < 150 MB free tier)
  - Without free tier: 500,000 data points × $0.258 / 1,000,000 ≈ $0.13/month

Reference: [Cloud Monitoring Pricing](https://cloud.google.com/monitoring/pricing)

## Total Monthly Cost Summary

| Service               | Monthly Cost     | Notes                                                 |
| --------------------- | ---------------- | ----------------------------------------------------- |
| **Cloud SQL**         | **$2.59**        | Shared between both projects (62 hrs/month)           |
| **Cloud Run**         | **$0.17**        | 4,800 vCPU-sec + 39,600 GiB-sec excess over free tier |
| **Artifact Registry** | **$0.95**        | 10 GB container image storage                         |
| **Networking**        | **$0.12**        | Egress for API requests and Git operations            |
| **Cloud Scheduler**   | **$0.00**        | Free tier (first 3 jobs)                              |
| **Cloud Logging**     | **$0.00**        | Free tier (first 50 GB/month)                         |
| **Secret Manager**    | **$0.00**        | Free tier (first 6 secrets/month)                     |
| **Cloud Monitoring**  | **$0.00**        | Free tier (first 150 MB/month)                        |
| **TOTAL**             | **~$3.83/month** | **~$46/year**                                         |

## Total Monthly Cost Summary (Without Free Tier)

| Service               | Monthly Cost      | Notes                                           |
| --------------------- | ----------------- | ----------------------------------------------- |
| **Cloud SQL**         | **$2.59**         | Shared between both projects (62 hrs/month)     |
| **Cloud Run**         | **$5.39**         | 244,800 vCPU-sec + 489,600 GiB-sec (full usage) |
| **Artifact Registry** | **$1.00**         | 10 GB container image storage (full usage)      |
| **Networking**        | **$0.24**         | 2 GB egress (full usage)                        |
| **Cloud Scheduler**   | **$0.10**         | 1 job (full usage)                              |
| **Cloud Logging**     | **$2.50**         | 5 GB log ingestion (full usage)                 |
| **Secret Manager**    | **$0.30**         | 5 secrets (full usage)                          |
| **Cloud Monitoring**  | **$0.13**         | 500,000 metric data points (full usage)         |
| **TOTAL**             | **~$12.25/month** | **~$147/year**                                  |

**Note:** This table shows costs if free tier limits were not available. The actual cost with free tier is ~$3.83/month.

## Cost Optimization Recommendation

    Ensure Cloud Run jobs and Cloud SQL are in the same region to avoid cross-region data transfer costs

## References

- Cloud SQL Pricing: https://cloud.google.com/sql/pricing
- Cloud Run Pricing & Free Tier: https://cloud.google.com/run/pricing
- Artifact Registry Pricing: https://cloud.google.com/artifact-registry/pricing
- VPC Network Pricing: https://cloud.google.com/vpc/network-pricing
- Cloud Scheduler Pricing: https://cloud.google.com/scheduler/pricing
- Cloud Logging Pricing: https://cloud.google.com/logging/pricing
- Secret Manager Pricing: https://cloud.google.com/secret-manager/pricing
- Cloud Monitoring Pricing: https://cloud.google.com/monitoring/pricing
