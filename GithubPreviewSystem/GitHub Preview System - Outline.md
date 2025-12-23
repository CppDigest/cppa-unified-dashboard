# GitHub Documentation Preview System

## Overview

Automatically converts documentation files (Markdown, Asciidoc, Quickbook) from GitHub PRs into HTML previews. Uses organization-level webhooks and a GitHub App to detect changes and generate previews without requiring setup in individual repositories.

**Processes**: PR opened/synchronize → Generate previews | PR closed/merged → Cleanup

---

## Workflow Diagram

```
┌─────────────────┐
│  Organization   │
│   Repositories  │
│  (PR Events)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Org Webhook    │
│  (PR events)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐       ┌──────────────┐
│   GitHub App    │────▶  │  Filter      │
│                 │       │  Repository  │
│  • Verify       │       └──────┬───────┘
│  • Route Action │              │
└────────┬────────┘              ▼
         │              ┌──────────────────┐
         │              │  Route by Action │
         │              │  opened/sync?    │
         │              └────────┬─────────┘
         │                       │
         │        ┌──────────────┴──────────────┐
         │        │                             │
         │      YES                            NO
         │        │                             │
         │        │                             ▼
         │        │                    ┌──────────────┐
         │        │                    │ Clone Preview│
         │        │                    │  Repository  │
         │        │                    └──────┬───────┘
         │        │                           │
         │        │                           ▼
         │        │                    ┌──────────────┐
         │        │                    │ Delete PR    │
         │        │                    │  folder      │
         │        │                    │  (closed/    │
         │        │                    │   merged)    │
         │        │                    └──────┬───────┘
         │        │                           │
         │        ▼                           │
         │  ┌──────────────┐                  │
         │  │ Clone Source │                  │
         │  │ Repo @ Commit│                  │
         │  └──────┬───────┘                  │
         │         │                          │
         │         ▼                          │
         │  ┌──────────────┐                  │
         │  │  Run Build   │                  │
         │  │  Script      │                  │
         │  └──────┬───────┘                  │
         │         │                          │
         │         ▼                          │
         │  ┌──────────────┐                  │
         │  │ Clone Preview│                  │
         │  │  Repository  │                  │
         │  └──────┬───────┘                  │
         │         │                          │
         │         ▼                          │
         │  ┌──────────────┐                  │
         │  │  Copy HTML   │                  │
         │  │  to Preview  │                  │
         │  └──────┬───────┘                  │
         │         │                          │
         └─────────┴──────────────────────────┘
                      │
                      ▼
         ┌──────────────────────┐
         │  Commit & Push       │
         │  to Preview Repo     │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Preview Repository  │
         │  {repo}/{PR}/        │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │   GitHub Pages       │
         │   (Public Preview)   │
         └──────────────────────┘
```

---

## Components

1. **Organization Webhook** - Monitors all repos, sends PR events (opened, synchronize, closed, merged)
2. **GitHub App** - Processes events, filters repos, clones at commit hash, runs build script, publishes HTML
3. **Preview Repository** - Stores HTML files under `{repo-name}/{PR-number}/` (files updated for each commit in same PR)
4. **GitHub Pages** - Serves previews publicly

---

## Key Features

- **Repository Filtering**: Only processes repositories in configured list
- **Multi-format Support**: Markdown (.md), Asciidoc (.adoc), Quickbook (.qbk), and more
- **Build Script Execution**: Each repo runs its own build script to generate HTML
- **Automatic Cleanup**: Removes PR folder when PR is closed or merged
- **PR-only Processing**: Only processes active PRs, not direct pushes to main/master

---

## Setup Steps

1. **Create GitHub App** - Set permissions (read/write contents, read PRs), generate private key
2. **Install App** - Install at organization level, grant repository access
3. **Create Preview Repo** - New repo for HTML previews, enable GitHub Pages
4. **Configure Filtering** - Define monitored repositories list
5. **Set Up Handler** - Deploy GitHub App handler (Actions workflow or external webhook handler)
6. **Test** - Make test PR change, verify preview generation

---

## Path Structure

Preview files are organized as: `{repository-name}/{PR-number}/{generated-html-files}`

Files in the same PR are updated in place (not creating separate folders per commit).

Example: `repo1/42/docs/guide.html`

---

## Appendix: Set Up Handler Details

### Option A: GitHub Actions Workflow (Recommended)

- Create workflow that triggers on `repository_dispatch` events
- App sends `repository_dispatch` events when PR webhooks are received
- Workflow routes based on PR action:
  - **For `opened`/`synchronize` actions:**
    1. Clone source repository at PR commit hash
    2. Run repository's build script (e.g., `npm run build-docs`, `./generate.sh`, `action.yml`)
    3. Collect generated HTML files
    4. Clone preview repository
    5. Copy HTML files to `{repository-name}/{PR-number}/` path (files updated in place)
    6. Commit and push to preview repository
  - **For `closed`/`merged` actions:**
    1. Clone preview repository
    2. Delete all files in `{repository-name}/{PR-number}/` folder
    3. Commit deletion to preview repository
    4. Push changes to preview repository

### Option B: External Webhook Handler

- Deploy webhook handler (can still be serverless, but uses App authentication)
- Configure App webhook URL to point to handler
- Handler processes `pull_request` events with all actions (opened, synchronize, closed, merged)
- Handler routes based on action:
  - **For `opened`/`synchronize` actions:**
    1. Clone source repository at PR commit hash using git
    2. Execute repository's build script
    3. Collect generated HTML files
    4. Clone preview repository
    5. Copy HTML files to `{repository-name}/{PR-number}/` path (files updated in place)
    6. Commit and push to preview repository
  - **For `closed`/`merged` actions:**
    1. Clone preview repository
    2. Delete all files in `{repository-name}/{PR-number}/` folder
    3. Commit deletion to preview repository
    4. Push changes to preview repository
- Handler uses App installation token for authentication

### Option C: GitHub Actions with Webhook Payload

- Store webhook payload in repository
- GitHub Actions workflow processes stored payloads
- Routes based on PR action:
  - **For `opened`/`synchronize`**: Clone, build, and push HTML files as in Option A
  - **For `closed`/`merged`**: Delete PR folder as in Option A cleanup process

### Repository Build Script Requirements

- Each repository must have its own script to generate HTML files
- Script should be executable (e.g., `build-docs.sh`, `generate-html.js`, `action.yml`)
- Script should output HTML files to a known directory (e.g., `dist/`, `output/`, `docs/html/`)
- Script can use any tools: npm scripts, Python, shell scripts, GitHub Actions, etc.

### Implementation Requirements

All implementations must:
- Process PR actions: `opened` and `synchronize` (generate previews)
- Cleanup PR actions: `closed` and `merged` (remove PR folder)
- Clone source repository at specific commit hash from PR (for opened/synchronize)
- Run repository's own build script (for opened/synchronize)
- Clone preview repository (for both processing and cleanup)
- Push HTML files to `{repository-name}/{PR-number}/` path (for opened/synchronize, files updated in place)
- Delete all files in `{repository-name}/{PR-number}/` folder and commit changes (for closed/merged)
