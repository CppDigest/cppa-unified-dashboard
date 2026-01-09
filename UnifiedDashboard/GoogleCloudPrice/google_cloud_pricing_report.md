# Google Cloud Deployment Pricing Report

## Project Overview

This deployment consists of two batch processing projects that scrape and process data from multiple sources.

### Project Scope

- GitHub Repositories: 172 repositories (1 main Boost repository + 171 submodules)
- Slack Channels: 209 public channels in cpplang Slack team
- Daily Messages: ~2,000 messages per day from Slack
- Mailing List: isocpp mailing list (less than 200 messages per day)
- API Requests: ~5,000 requests per day for GitHub data (commits, PRs with reviews/comments, issues with comments)
- Data Processing: WG21 paper conversion (PDF/HTML to Markdown) and automated PR creation

## Architecture

### Project 1: Daily Data Scraper

- Purpose: Monitor and collect data from multiple sources to maintain a database of C++ community activity
- Schedule: Runs once per day during off-peak hours
- Workflow: Collects GitHub data (172 repositories), Slack messages (209 channels), mailing list data (converts to Markdown and pushes to GitHub), and monitors WG21 papers for updates
- Runtime: ~2 hours per day
- Resources: 1 vCPU / 2 GB RAM

### Project 2: Monthly WG21 Paper Processor

- Purpose: Download documentations from the wg21 paper website, convert them from PDF/HTML to Markdown, and contribute them to the wg21 paper GitHub repository via automated Pull Requests
- Schedule: Triggered by Project 1 when WG21 papers are updated (typically once per month)
- Workflow: Downloads papers, converts to Markdown (PDF: `docling` -> `pdfplumber` -> OpenAI; HTML: `pandoc`), creates Pull Requests (one per minute rate limit)
- Runtime: ~2 hours per month
- Resources: 4 vCPU / 8 GB RAM (6 GB container image with conversion tools)

## Price Details by Service

### 1. Google Cloud SQL

Purpose: Core database for storing scraped data

Assumptions:

- Active Time: 62 hours/month (~60h from Project 1 + 2h from Project 2)
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

Total Cloud Run Cost: $0.17/month

Reference: [Cloud Run Pricing & Free Tier](https://cloud.google.com/run/pricing)

### 3. Artifact Registry

Purpose: Store container images for Cloud Run jobs

- Image Size: 6 GB (for Project 2)
- Pricing: $0.10 per GB/month after first 0.5 GB
- Calculation: (6 GB - 0.5 GB) × $0.10 = $0.55/month

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
- Calculation: (2 GB - 1 GB) × $0.12 = $0.12/month

Reference: [VPC Network Pricing](https://cloud.google.com/vpc/network-pricing)

### 5. Cloud Scheduler

Purpose: Schedule daily and monthly jobs

- Jobs: 1 active job (1 daily)
- Pricing: $0.10 per job per month
- Free Tier: First 3 jobs per billing account are free
- Cost: $0.00 (within free tier)

Reference: [Cloud Scheduler Pricing](https://cloud.google.com/scheduler/pricing)

## Total Monthly Cost Summary

| Service               | Monthly Cost     | Notes                                                 |
| --------------------- | ---------------- | ----------------------------------------------------- |
| **Cloud SQL**         | **$2.59**        | Shared between both projects (62 hrs/month)           |
| **Cloud Run**         | **$0.17**        | 4,800 vCPU-sec + 39,600 GiB-sec excess over free tier |
| **Artifact Registry** | **$0.55**        | 6 GB container image storage                          |
| **Networking**        | **$0.12**        | Egress for API requests and Git operations            |
| **Cloud Scheduler**   | **$0.00**        | Free tier (first 3 jobs)                              |
| **TOTAL**             | **~$3.43/month** | **~$41/year**                                         |

## Cost Optimization Recommendations

1. Regional Deployment: Ensure Cloud Run jobs and Cloud SQL are in the same region to avoid cross-region data transfer costs

## References

- Cloud SQL Pricing: https://cloud.google.com/sql/pricing
- Cloud Run Pricing & Free Tier: https://cloud.google.com/run/pricing
- Artifact Registry Pricing: https://cloud.google.com/artifact-registry/pricing
- VPC Network Pricing: https://cloud.google.com/vpc/network-pricing
- Cloud Scheduler Pricing: https://cloud.google.com/scheduler/pricing
