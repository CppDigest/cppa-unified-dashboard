import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

from fetch import fetch_commit_from_github, fetch_updated_issue_from_github, fetch_updated_pr_from_github
from git_client import GitHubAPIClient
from database import Database

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def get_github_client():
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN not found in environment variables")
        raise ValueError("GITHUB_TOKEN environment variable is required")
    return GitHubAPIClient(GITHUB_TOKEN)

def process_repo_commit_activities(client: GitHubAPIClient, database: Database, repo: str):
    logger.info(f"Fetching commit activities for {repo}")
    last_commit_date = database.get_last_commit_date(repo)
    if last_commit_date:
        logger.info(f"Last commit date: {last_commit_date}")
        # Add 1 microsecond to avoid processing the same commit again (since 'since' parameter is inclusive)
        start_date = last_commit_date + timedelta(seconds=1)
    else:
        logger.info("No last commit date found")
        start_date = None

    end_date = datetime.now()
    logger.info(f"Start date: {start_date}, End date: {end_date}")
    cnt = 0
    session = database.get_session()
    for commit in fetch_commit_from_github(client, repo, start_date, end_date):
        cnt += 1
        logger.debug(f"Inserting commit #{commit['sha']}")
        database.insert_commit(commit, repo, session)
        logger.debug(f"Commit #{commit['sha']} inserted successfully")
    logger.info(f"Total commits inserted: {cnt}")
    session.close()

def process_repo_issues_activities(client: GitHubAPIClient, database: Database, repo: str):
    logger.info(f"Fetching issues activities for {repo}")
    last_issue_date = database.get_last_issue_date(repo)

    if last_issue_date:
        logger.info(f"Last issue date: {last_issue_date}")
        # Add 1 microsecond to avoid processing the same issue again (since 'since' parameter is inclusive)
        start_date = last_issue_date + timedelta(seconds=1)
    else:
        logger.info("No last issue date found")
        start_date = None

    end_date = datetime.now()
    logger.info(f"Start date: {start_date}, End date: {end_date}")
    cnt = 0
    session = database.get_session()
    for issue in fetch_updated_issue_from_github(client, "boostorg", repo, start_date, end_date):
        cnt += 1
        logger.debug(f"Fetching comments for issue #{issue['number']}")
        # if not os.path.exists(f"data/issues/{repo}"):
        #     os.makedirs(f"data/issues/{repo}")
        # with open(f"data/issues/{repo}/issue_{issue['number']}.json", "w") as f:
        #     import json
        #     json.dump(issue, f, indent=2, default=str)

        database.insert_issue(issue, repo, session)
    logger.info(f"Total issues inserted: {cnt}")
    session.close()

def process_repo_pr_activities(client: GitHubAPIClient, database: Database, repo: str):
    logger.info(f"Fetching PR activities for {repo}")
    last_pr_date = database.get_last_pr_date(repo)
    if last_pr_date:
        logger.info(f"Last PR date: {last_pr_date}")
        # Add 1 microsecond to avoid processing the same PR again (since 'since' parameter is inclusive)
        start_date = last_pr_date + timedelta(seconds=1)
    else:
        logger.info("No last PR date found")
        start_date = None

    end_date = datetime.now()
    logger.info(f"Start date: {start_date}, End date: {end_date}")
    cnt = 0
    session = database.get_session()
    for pr in fetch_updated_pr_from_github(client, "boostorg", repo, start_date, end_date):
        cnt += 1
        logger.debug(f"Fetching comments for PR #{pr['number']}")
        # if not os.path.exists(f"data/prs/{repo}"):
        #     os.makedirs(f"data/prs/{repo}")
        # with open(f"data/prs/{repo}/pr_{pr['number']}.json", "w") as f:
        #     import json
        #     json.dump(pr, f, indent=2, default=str)
        database.insert_pull_request(pr, repo, session)
    logger.info(f"Total PRs inserted: {cnt}")
    session.close()

def fetch_boost_repo_activities():
    logger.info("Fetching Boost repository activities")
    client = get_github_client()
    database = Database(os.getenv("DATABASE_URL"))
    database.create_tables()
    logger.info("Tables created successfully")
    git_modules = client.get_submodules("boostorg", "boost")

    def process_commit_activities():
        process_repo_commit_activities(client, database, "boost")
        for git_module in git_modules:
            process_repo_commit_activities(client, database, git_module["repo"])

    def process_issues_activities():
        process_repo_issues_activities(client, database, "boost")
        for git_module in git_modules:
            process_repo_issues_activities(client, database, git_module["repo"])

    def process_pr_activities():
        process_repo_pr_activities(client, database, "boost")
        for git_module in git_modules:
            process_repo_pr_activities(client, database, git_module["repo"])

    logger.info("Fetching commit activities")
    process_commit_activities()
    logger.info("Commit activities fetched successfully")

    logger.info("Fetching issues activities")
    process_issues_activities()
    logger.info("Issues activities fetched successfully")

    logger.info("Fetching PR activities")
    process_pr_activities()
    logger.info("Commit activities fetched successfully")


    logger.info("Closing database connection")
    database.close()


if __name__ == "__main__":
    fetch_boost_repo_activities()