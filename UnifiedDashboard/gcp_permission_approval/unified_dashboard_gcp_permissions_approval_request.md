# Request: Google Cloud Permissions for Unified Dashboard Deployment

## Current state

We want to deploy and operate a unified dashboard data pipeline using Google Cloud services.
There is an existing Google Cloud project (e.g. `boost`) with multiple products already enabled.
For this work we also need the ability to enable the required APIs as needed.

## Goal

Run a small, scheduled pipeline that:

- Collects activity data (GitHub, Slack, X.com, Reddit, etc.)
- Runs a scheduled automation script on Cloud Run (triggered by Cloud Scheduler)
- Stores results in PostgreSQL on Cloud SQL
- Visualizes results in Looker Studio

## Requested actions

### 1. Create a separate project for the dashboard

Create a new Google Cloud project (e.g., `boost-dashboard`) dedicated to the unified dashboard.
This project will host Cloud Run, Cloud Scheduler, Cloud SQL, and any supporting services.

- Advantages

  - Separation of concerns: dashboard infrastructure is isolated from the existing `boost` project.
  - Cleaner IAM: we can grant least-privilege roles without affecting other workloads.
  - Easier cost tracking: billing and budgets are scoped to one project.

- Disadvantages

  - More setup overhead (project creation, IAM, API enablement).
  - Ongoing maintenance across one additional project.

### 2. Grant least-privilege IAM roles

Grant the following roles in the dashboard project.

| Identity (who is it?)                      | Role name (human-readable)     | IAM role ID                          | Purpose                                                                     |
| ------------------------------------------ | ------------------------------ | ------------------------------------ | --------------------------------------------------------------------------- |
| 1. Developer Google account                | Cloud Run Developer            | `roles/run.developer`                | Build, deploy, and manage Cloud Run services/jobs.                          |
| 1. Developer Google account                | Service Account User           | `roles/iam.serviceAccountUser`       | Deploy Cloud Run using the dedicated runtime service account.               |
| 1. Developer Google account                | Cloud SQL Viewer               | `roles/cloudsql.viewer`              | View instance status and obtain the connection name.                        |
| 2. Cloud Run runtime service account       | Cloud SQL Client               | `roles/cloudsql.client`              | Allows Cloud Run to connect to Cloud SQL via the secure connector/proxy.    |
| 2. Cloud Run runtime service account       | Secret Manager Secret Accessor | `roles/secretmanager.secretAccessor` | Allows runtime code to retrieve secrets securely (no credentials in code).  |
| 3. Cloud Scheduler trigger service account | Cloud Run Invoker              | `roles/run.invoker`                  | Allows Cloud Scheduler to invoke the protected Cloud Run endpoint via OIDC. |

### 3. Enable required APIs

Enable these APIs in the dashboard project:

- Cloud Run API
- Cloud SQL Admin API
- Cloud Scheduler API
- Secret Manager API
- Cloud Build API

### 4. Add billing and set cost expectations

Attach billing to the dashboard project and (optionally) configure budget alerts.

Our expected workload is small:

- Database size: < 100MB (current expectation)
- At most 3 scheduled jobs
- Each job runs once per day

Expected monthly cost (based on free tier + low-volume usage):

- Cloud Scheduler: ~$0/month (within free allowance; otherwise ~ $0.10/job/month).
- Cloud Run: ~$0/month (very low run volume).
- Cloud SQL (PostgreSQL): main recurring cost.

  - For the smallest shared-core instance, a realistic minimum is often ~$15–$25/month (region/config dependent), plus disk/backups.
  - Cost tip: avoid an idle public IPv4 address fee when possible (prefer private IP, or remove unused public IPs).

### 5. Approve secrets / configuration handling

The automation script needs credentials and configuration.
Recommended approach:

- Store sensitive values in Secret Manager.
- Reference secrets from Cloud Run (env vars or direct secret references).

Required configuration keys (names can be adjusted to match implementation):

- `GITHUB_TOKEN` (stored in Secret Manager)
- Database connectivity (Cloud SQL connection name and/or connection URL)

- Advantages

  - No secrets in source code or container images.
  - Central rotation and access control through IAM.

- Disadvantages

  - Requires initial setup (secrets creation, permissions, and deployment wiring).

## Why this is needed

- To deploy and run daily jobs in a controlled, auditable way (Cloud Scheduler -> Cloud Run).
- To allow the runtime service account to securely access Cloud SQL and Secret Manager without embedding credentials in code.
- To enable billing so Cloud SQL (the primary recurring cost) can run, while keeping overall spend low via free tiers and budget alerts.

## Timeline

Once the new project is created and billing is enabled, we can start right away.
We already prepared the data (up to 2025-12-15) and the script to collect Boost library GitHub activity.
We will build the dashboard for Boost library GitHub activity first, then add other data sources continuously.
