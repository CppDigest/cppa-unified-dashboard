# Unified Dashboard Using Third-Party Services

This project requires collecting data from GitHub, Slack, X.com, and other sources, then storing it in an online database.
The dashboard service will access the database and display data on the website.

## Automation Script Daily Running Platform

- GitHub Actions (Recommended)

  - Limit: 2000 free minutes per month per user, public repositories have unlimited action time
  - Supported languages: All languages

- PythonAnywhere

  - Limit: One scheduled Python task daily, up to 2 hours runtime
  - Supported languages: Python

- Netlify Functions
  - Limit: 300 free credits per month, or 1000 credits per month for $9
  - Supported languages: JavaScript/TypeScript
  - Credit consumption: production deploys 15 credits each, compute 5 credits per GB-hour, bandwidth 10 credits per GB, web requests 3 credits per 10,000 requests

**Note:** The data collection process requires approximately 700-1000 REST API calls to GitHub. Daily script execution should complete within 30 minutes since individual repository activity is limited each day.

## Online SQL Database Service

- Neon (Recommended)

  - Database type: Serverless Postgres
  - Storage: 0.5 GB free, then $0.35 per GB per month
  - Backups: 1 day retention in Free Tier

- Azure SQL Database
  - Database type: Relational (SQL Server)
  - Storage: 32 GB free, then $0.11 per GB per month
  - Backups: Automatic backups with retention
  - Requirement: Credit card information required

**Note:** The Boost organization GitHub data from beginning to 2025-10 is approximately 240 MB in raw format.

## Online Dashboard Service

- Google Looker Studio (Recommended)

  - Cost: Free forever

- Tableau
  - Cost: 14 days free trial, then $70 per user per month

**Note:** The dashboard supports connections with view or edit permissions.

## Appendix: Development Roadmap (2 weeks)

1. Configure the online database service
2. Develop and test the data collection script locally
3. Deploy the automation script to the selected platform
4. Design and configure the dashboard
5. Connect the dashboard to the database
