# GitHub Documentation Preview System

## Overview

This system automatically converts documentation files from multiple GitHub repositories into HTML previews. It supports various documentation formats including **Markdown**, **Asciidoc**, **Qubic**, and other text-based formats. It uses organization-level webhooks to detect changes across all repositories without requiring any setup in individual repositories.

### Core Concept

When documentation files change in **active pull requests** within your organization, the system:
1. Detects the change automatically (for open PRs with new commits)
2. Clones the repository at the PR commit hash
3. Runs the repository's own build script to generate HTML files
4. Publishes generated HTML files to a central preview repository (under `{repo-name}/{PR-number}/{commit-hash}/` path)
5. Makes it viewable via GitHub Pages for PR review
6. Automatically cleans up preview files when PR is merged or closed

**Important**: The system processes:
-  Pull requests that are **opened** (new PR created) → Generate previews
-  Pull requests with **new commits** (synchronize event) → Generate previews
-  Pull requests that are **merged** → Cleanup (remove PR folder)
-  Pull requests that are **closed** → Cleanup (remove PR folder)
-  **NOT** direct pushes to main/master branches

---

## How It Works - Logical Flow

### The Solution Architecture

The system has four main components:

1. **GitHub Organization Webhook** - Listens for all repository events
2. **GitHub App** - Processes events and makes decisions (runs on GitHub infrastructure)
3. **GitHub API** - Fetches and updates files
4. **Preview Repository** - Stores converted HTML files

---

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         GITHUB ORGANIZATION                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  Repo 1  │  │  Repo 2  │  │  Repo 3  │  │  Repo N  │         │
│  │          │  │          │  │          │  │          │         │
│  │ docs/    │  │ docs/    │  │ README   │  │ docs/    │         │
│  │ guide.md │  │ api.adoc │  │ .md      │  │ index.qb │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │             │             │             │               │
│       └─────────────┴─────────────┴─────────────┘               │
│                          │                                      │
│                          │ Pull Request Event                   │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│            ORGANIZATION WEBHOOK (One-Time Setup)                        |
│                                                                         |
│  • Monitors ALL repositories in organization                            |
│  • Sends events for: pull_request (opened, synchronize, closed, merged) │
│  • Does NOT send: push events                                           |
│  • Configured to send events to GitHub App                              |
│                                                                         |
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           │ Webhook Event (HTTP POST)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB APP                                   │
│                    (Installed at Organization Level)            │
│                                                                 │
│  • Receives webhook events from organization                    │
│  • Processes events using GitHub Actions or App logic           │
│  • Uses installation token for API authentication               │
│  • Runs entirely on GitHub infrastructure                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 1: Verify Webhook Signature                         │   │
│  │   • Check if request is from GitHub                      │   │
│  │   • Reject if signature invalid                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 2: Extract Event Information                        │   │
│  │   • Repository name (e.g., "org/repo1")                  │   │
│  │   • Event type: pull_request                             │   │
│  │   • PR action: opened, synchronize, closed, merged       │   │
│  │   • PR number and branch                                 │   │
│  │   • Changed files list (if opened/synchronize)           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 2B: Check PR Action Type                            │   │
│  │                                                          │   │
│  │   Is action "closed" or "merged"?                        │   │
│  │   ┌─────────────────────────────────────┐                │   │
│  │   │ YES → Go to Cleanup Process         │                │   │
│  │   │ NO  → Continue to Repository Filter │                │   │
│  │   └─────────────────────────────────────┘                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                      │
│        ┌─────────────────┴─────────────────┐                    │
│        │                                   │                    │
│       YES                                 NO                    │
│        │                                   │                    │
│        ▼                                   ▼                    │
│  ┌──────────────────┐        ┌────────────────────────────────┐ │
│  │ CLEANUP PROCESS  │        │ STEP 3: Repository Filtering   │ │
│  │ (See below)      │        │                                │ │
│  │                  │        │   Is repository in monitored   │ │
│  │                  │        │   list?                        │ │
│  │                  │        │   ┌──────────────────────────┐ │ │
│  │                  │        │   │ YES → Continue processing│ │ │
│  │                  │        │   │ NO  → Skip (do not       │ │ │
│  │                  │        │   │      process)            │ │ │
│  │                  │        │   └──────────────────────────┘ │ │
│  │                  │        │                                │ │
│  │                  │        │   Note: Only repositories in   │ │
│  │                  │        │   your configured list will be │ │
│  │                  │        │   processed.                   │ │
│  └──────────────────┘        └────────────────────────────────┘ │
│                                            │                    │
│                                            ▼                    │
│                             (Continue to STEP 4)                │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 4: Filter Documentation Files                       │   │
│  │   • Check each changed file                              │   │
│  │   • Match against documentation patterns:                │   │
│  │     - docs/**/*.md, *.md (Markdown)                      │   │
│  │     - docs/**/*.adoc, *.asciidoc (Asciidoc)              │   │
│  │     - docs/**/*.qb, *.qubic (Qubic)                      │   │
│  │     - documentation/**/*.* (all formats)                 │   │
│  │   • Identify file format by extension                    │   │
│  │   • Skip non-documentation files                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 5: Clone Repository at PR Commit                    │   │
│  │   1. Clone repository from PR creator's branch           │   │
│  │   2. Checkout specific commit hash from PR               │   │
│  │   3. Repository is now at exact PR commit state          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 6: Run Repository's Action Script                   │   │
│  │   • Execute repository's own build/generation script     │   │
│  │   • Script generates HTML files from documentation       │   │
│  │   • HTML files created in repository's output directory  │   │
│  │   • Script may use repository-specific tools/config      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP 7: Push HTML Files to Preview Repository            │   │
│  │   • Copy generated HTML files from cloned repo           │   │
│  │   • Push to preview repository under path:               │   │
│  │     {repository-name}/{PR-number}/{commit-hash}/         │   │
│  │   • Example: repo1/42/abc1234def/                        │   │
│  │   • Commit HTML files to preview repository              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           │ Git Operations
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLEANUP PROCESS                              │
│                    (For closed/merged PRs)                      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP CLEANUP 1: Verify Repository                        │   │
│  │   • Check if repository is in monitored list             │   │
│  │   • Skip cleanup if repository not monitored             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ STEP CLEANUP 2: Remove PR Folder                         │   │
│  │   • Delete all files in: {repository-name}/{PR-number}/  │   │
│  │   • Remove entire folder structure                       │   │
│  │   • Example: Delete repo1/42/ folder and all contents    │   │
│  │   • Commit deletion to preview repository                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           │ Git Operations
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GIT OPERATIONS                               │
│                                                                 │
│  • Clone repository from PR branch                              │
│  • Checkout specific commit hash                                │
│  • Run repository's build script                                │
│  • Copy generated HTML files                                    │
│  • Commit and push to preview repository                        │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ Commits HTML files
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PREVIEW REPOSITORY                           │
│                    (org-docs-preview)                           │
│                                                                 │
│  Directory Structure:                                           │
│  ├── repo1/                                                     │
│  │   ├── 42/                  (PR number)                       │
│  │   │   ├── abc1234def/      (commit hash from PR)             │
│  │   │   │   ├── docs/guide.html                                │
│  │   │   │   └── README.html                                    │
│  │   │   └── def5678ghi/      (another commit from PR)          │
│  │   │       └── docs/updated.html                              │
│  │   └── ...                                                    │
│  ├── repo2/                                                     │
│  │   ├── 15/                  (PR number)                       │
│  │   │   └── xyz9876abc/      (commit hash from PR)             │
│  │   │       ├── docs/api.html                                  │
│  │   │       └── docs/manual.html                               │
│  │   └── ...                                                    │
│  └── ...                                                        │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ GitHub Pages automatically serves
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GITHUB PAGES                               │
│                      (Public Preview)                           │
│                                                                 │
│  https://your-org.github.io/org-docs-preview/                   │
│                                                                 │
│  Users can browse all documentation in one place                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Concepts Explained

### 1. Organization Webhook

**What it is:**
- A single webhook configured at the organization level
- Automatically receives events from ALL repositories in the organization
- No need to configure webhooks in individual repositories

**What it does:**
- Listens for pull request events only
- Sends HTTP POST requests to your GitHub App webhook endpoint
- Includes information about which repository changed and what files were modified
- Triggers for: `opened`, `synchronize`, `closed`, and `merged` actions
- Does NOT trigger for: `push` events

**Configuration:**
- Can be configured to send events to GitHub App webhook URL
- Or can use GitHub App's built-in webhook handling

### 2. GitHub App

**What it is:**
- A GitHub App installed at the organization level
- Receives webhook events from the organization
- Processes events using GitHub Actions workflows or App webhook handlers
- Runs entirely on GitHub infrastructure

**What it does:**
1. **Webhook Reception**: Receives pull request webhook events from organization
2. **PR Action Routing**: Routes based on PR action type
   - **For `opened`/`synchronize` actions**: Process PR (generate previews)
   - **For `closed`/`merged` actions**: Cleanup PR folder (remove files)
3. **Security Check**: Verifies webhook signature (automatic with GitHub Apps)
4. **Repository Filtering**: Decides which repositories to process
5. **File Filtering**: Identifies documentation files that changed in PR (for opened/synchronize)
6. **Repository Cloning**: Clones repository at specific commit hash from PR (for opened/synchronize)
7. **Script Execution**: Runs repository's own build/generation script (for opened/synchronize)
8. **HTML Collection**: Collects generated HTML files from script output (for opened/synchronize)
9. **Publishing**: Commits HTML files to preview repository under `{repo-name}/{PR-number}/{commit-hash}/` path (for opened/synchronize)
10. **Cleanup**: Removes all files in `{repo-name}/{PR-number}/` folder when PR is closed or merged

**Implementation Options:**
- **Option A**: GitHub App webhook handler (can be deployed as serverless function)
- **Option B**: GitHub App triggers GitHub Actions workflows via `repository_dispatch`
- **Option C**: GitHub App with GitHub Actions workflow that processes webhook payloads


### 3. Repository Filtering

**Why it's needed:**
- Organization webhooks send events for ALL repositories
- You may only want to process certain repositories
- Filtering happens in the handler, not the webhook

**How it works:**
- **List Approach**: List specific repository names
  - Only repositories in the list are processed
  - All others are automatically skipped

**Filtering Priority**
1. If repository is in exact match list → Process
2. Otherwise → Skip

### 4. File Processing

**What files are processed:**
- Multiple documentation formats supported:
  - **Markdown**: `.md`, `.markdown` files
  - **Asciidoc**: `.adoc`, `.asciidoc` files
  - **Qubic**: `.qb`, `.qubic` files
  - **Other formats**: Configurable extensions
- Files matching configured patterns:
  - Files in `docs/` folder
  - Root-level documentation files
  - Files in `documentation/` folder

**What happens for each PR commit:**
1. Clone the repository from PR creator's branch
2. Checkout the specific commit hash from the PR
3. Run the repository's own build/generation script (e.g., `build.sh`, `generate-docs.js`, `action.yml`, etc.)
4. The script generates HTML files using repository-specific tools and configuration
5. Collect all generated HTML files from the script's output directory
6. Copy HTML files to preview repository under: `{repository-name}/{PR-number}/{commit-hash}/`
7. Commit and push HTML files to preview repository

**File paths:**
- Format: `{repository-name}/{PR-number}/{commit-hash}/{generated-html-files}`
- Example: PR #42 with commit `abc1234def` in `repo1` → `repo1/42/abc1234def/`
- Example: PR #15 with commit `xyz9876abc` in `repo2` → `repo2/15/xyz9876abc/`
- Each commit hash gets its own folder with all generated HTML files
- Note: Main branch pushes are NOT processed (only active PRs)

### 5. Preview Repository

**What it is:**
- A dedicated GitHub repository that stores all converted HTML files
- Serves as the central location for all documentation previews

**Structure:**
- Each source repository gets its own folder
- Each PR number gets its own subfolder
- Each commit hash gets its own subfolder within the PR folder
- Format: `{repository-name}/{PR-number}/{commit-hash}/`
- Contains all HTML files generated by repository's build script

**GitHub Pages:**
- Automatically serves the repository contents as a website
- Provides a public URL for viewing all documentation
- Updates automatically when new files are committed

---

## Setup Process

### Step 1: Create GitHub App
- Navigate to organization settings → GitHub Apps
- Create a new GitHub App
- Configure App permissions:
  - Repository contents: Read (to fetch files from PR branches)
  - Repository contents: Write (to commit to preview repo)
  - Pull requests: Read (to access PR information)
  - Metadata: Read (to access repository information)
- Set webhook URL (if using external handler) or configure to use GitHub Actions
- Generate and store App private key
- Note the App ID

### Step 2: Install GitHub App at Organization Level
- Install the App to the organization
- Grant access to all repositories (or specific ones)
- Store the installation ID

### Step 3: Create Preview Repository
- Create a new repository for storing HTML previews
- Enable GitHub Pages to serve the files
- Configure branch and folder settings
- Grant the GitHub App write access to this repository

### Step 4: Configure Repository Filtering
- Define which repositories to monitor (in App configuration or environment)
- Specify documentation file patterns to process

### Step 5: Set Up GitHub App Handler
**Option A: GitHub Actions Workflow (Recommended)**
- Create workflow that triggers on `repository_dispatch` events
- App sends `repository_dispatch` events when PR webhooks are received
- Workflow routes based on PR action:
  - **For `opened`/`synchronize` actions:**
    1. Clone repository at PR commit hash
    2. Run repository's build script (e.g., `npm run build-docs`, `./generate.sh`, `action.yml`)
    3. Collect generated HTML files
    4. Push to preview repo under `{repository-name}/{PR-number}/{commit-hash}/` path
  - **For `closed`/`merged` actions:**
    1. Delete all files in `{repository-name}/{PR-number}/` folder
    2. Commit deletion to preview repository

**Option B: External Webhook Handler**
- Deploy webhook handler (can still be serverless, but uses App authentication)
- Configure App webhook URL to point to handler
- Handler processes `pull_request` events with all actions (opened, synchronize, closed, merged)
- Handler routes based on action:
  - **For `opened`/`synchronize` actions:**
    1. Clone repository at PR commit hash using git
    2. Execute repository's build script
    3. Collect generated HTML files
    4. Commit to preview repo under `{repository-name}/{PR-number}/{commit-hash}/` path
  - **For `closed`/`merged` actions:**
    1. Delete all files in `{repository-name}/{PR-number}/` folder
    2. Commit deletion to preview repository
- Handler uses App installation token for authentication

**Option C: GitHub Actions with Webhook Payload**
- Store webhook payload in repository
- GitHub Actions workflow processes stored payloads
- Routes based on PR action:
  - **For `opened`/`synchronize`**: Clone, build, and push HTML files as in Option A
  - **For `closed`/`merged`**: Delete PR folder as in Option A cleanup process

**Repository Build Script Requirements:**
- Each repository must have its own script to generate HTML files
- Script should be executable (e.g., `build-docs.sh`, `generate-html.js`, `action.yml`)
- Script should output HTML files to a known directory (e.g., `dist/`, `output/`, `docs/html/`)
- Script can use any tools: npm scripts, Python, shell scripts, GitHub Actions, etc.

**Important**: All implementations must:
-  Process PR actions: `opened` and `synchronize` (generate previews)
-  Cleanup PR actions: `closed` and `merged` (remove PR folder)
-  Clone repository at specific commit hash from PR (for opened/synchronize)
-  Run repository's own build script (for opened/synchronize)
-  Push HTML files to `{repository-name}/{PR-number}/{commit-hash}/` path (for opened/synchronize)
-  Delete all files in `{repository-name}/{PR-number}/` folder (for closed/merged)

### Step 5: Test and Monitor
- Make a test change in a monitored repository
- Verify the preview is generated correctly
- Monitor logs for any issues