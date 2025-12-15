# Script for Boost repository activity

This script is used to load GitHub repository activity (commits, pull requests, issues, comments, and reviews) into a relational database for analysis.

## 1. Prerequisites

- Python 3.11+ (matching the project’s main environment)
- A running database (e.g. PostgreSQL) and a connection URL
- A GitHub personal access token with read access to public repositories

## 2. Configuration

Create a `.env` file in the `boost_github_script` directory based on `.env.example`:

```env
GITHUB_TOKEN=YOUR_GITHUB_TOKEN_HERE
DATABASE_URL=YOUR_DATABASE_URL_HERE
```

- `GITHUB_TOKEN`: GitHub personal access token.
- `DATABASE_URL`: SQLAlchemy-style database URL (for example, `postgresql+psycopg2://user:password@host:5432/dbname`).

## 3. Installing Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

Ensure the environment you run commands in has the same interpreter and dependencies as the rest of the project.

## 4. Main Entry Points

```bash
python app.py
```

`app.py` will:

- Initialise the database schema (via SQLAlchemy models).
- Use `GitHubAPIClient` to talk to the GitHub REST API.
- Store commits, issues, PRs, comments, and reviews into the database.

## 5. Database schema (high-level)

Key tables (see `models.py` for full definitions):

- `identity` / `email` / `user` – contributor identity resolution and metadata.
- `commit` – git commits (one row per commit).
- `prs` / `prs_review` / `prs_comment` – pull requests and their reviews and comments.
- `issue` / `issue_comment` – issues and their comments.

## 6. How this data is used

The data collected by this script can be used to:

- Monitor activity across Boost and its submodules
- Understand visibility and engagement
- Support design and communication decisions

## 7. Notes

- This submodule is designed to be run from within the larger project.
- For migrations or schema changes, use standard SQLAlchemy/Alembic workflows rather than altering tables manually in production.
