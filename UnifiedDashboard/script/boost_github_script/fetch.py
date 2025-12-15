from datetime import datetime, timezone
import time
from typing import List, Dict
import logging
from git_client import GitHubAPIClient
logger = logging.getLogger(__name__)

def fetch_commit_from_github(client: GitHubAPIClient, repo: str, start_time: datetime, end_time: datetime) -> List[Dict]:
    logger.info(f"Fetching commits for {repo} from {start_time} to {end_time}")
    results: List[Dict] = []
    page = 1
    per_page = 100
    while True:
        params = {
            "per_page": per_page,
            "page": page,
            "since": start_time.isoformat() if start_time else None,
        }
        if end_time:
            params["until"] = end_time.isoformat()
        commits = client.rest_request(f"/repos/boostorg/{repo}/commits", params)
        if not commits:
            logger.debug(f"No more commits found at page {page}")
            break
        logger.debug(f"Fetched {len(commits)} commits from page {page}")
        for commit in commits:
            commit_date_str = (
                commit.get("commit", {}).get("author", {}).get("date")
                or commit.get("commit", {}).get("committer", {}).get("date")
            )
            if commit_date_str:
                try:
                    commit_dt = datetime.fromisoformat(commit_date_str.replace("Z", "+00:00"))

                    # Ensure start_time and end_time are timezone-aware for comparison
                    if start_time:
                        if start_time.tzinfo is None:
                            start_time_aware = start_time.replace(tzinfo=timezone.utc)
                        else:
                            start_time_aware = start_time
                        if commit_dt < start_time_aware:
                            continue

                    if end_time:
                        if end_time.tzinfo is None:
                            end_time_aware = end_time.replace(tzinfo=timezone.utc)
                        else:
                            end_time_aware = end_time
                        if commit_dt > end_time_aware:
                            continue
                except Exception as e:
                    logger.debug(f"Failed to parse commit date '{commit_date_str}': {e}")
                    pass
            yield commit
        if len(commits) < per_page:
            logger.debug(f"Last page reached (got {len(commits)} commits, expected {per_page})")
            break
        page += 1
        time.sleep(0.2)


def fetch_updated_comment_from_github(client: GitHubAPIClient, owner: str, repo: str, issue_number: int, start_time: datetime, end_time: datetime) -> List[Dict]:
    logger.debug(f"Fetching comments for {owner}/{repo} issue #{issue_number} from {start_time} to {end_time}")

    results: List[Dict] = []
    page = 1
    per_page = 100
    while True:
        params = {"per_page": per_page, "page": page}
        params["since"] = start_time.isoformat() if start_time else None
        params["until"] = end_time.isoformat() if end_time else None
        params["sort"] = "created"
        params["direction"] = "asc"
        comments = client.rest_request(
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            params,
        )
        if not comments:
            logger.debug(f"No more comments found at page {page} for issue #{issue_number}")
            break
        logger.debug(f"Fetched {len(comments)} comments from page {page} for issue #{issue_number}")
        for comment in comments:
            created_str = comment.get("created_at")
            if created_str:
                try:
                    c_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))

                    # Ensure start_time and end_time are timezone-aware for comparison
                    if start_time:
                        if start_time.tzinfo is None:
                            start_time_aware = start_time.replace(tzinfo=timezone.utc)
                        else:
                            start_time_aware = start_time
                        if c_dt < start_time_aware:
                            continue

                    if end_time:
                        if end_time.tzinfo is None:
                            end_time_aware = end_time.replace(tzinfo=timezone.utc)
                        else:
                            end_time_aware = end_time
                        if c_dt > end_time_aware:
                            continue
                except Exception as e:
                    logger.debug(f"Failed to parse comment date '{created_str}': {e}")
                    pass
            results.append(comment)
        if len(comments) < per_page:
            break
        page += 1
        time.sleep(0.1)
    logger.debug(f"Total comments fetched for issue #{issue_number}: {len(results)}")
    return results

def fetch_updated_issue_from_github(client: GitHubAPIClient, owner: str, repo: str, start_time: datetime, end_time: datetime) -> List[Dict]:
    logger.info(f"Fetching issues for {owner}/{repo} from {start_time} to {end_time}")
    results: List[Dict] = []
    page = 1
    per_page = 100
    while True:
        params = {
            "state": "all",
            "per_page": per_page,
            "page": page,
            "since": start_time.isoformat() if start_time else None,
            "until": end_time.isoformat() if end_time else None,
            "sort": "updated",
            "direction": "asc",
        }
        issues = client.rest_request(f"/repos/{owner}/{repo}/issues", params)
        if not issues:
            logger.debug(f"No more issues found at page {page}")
            break
        issues_length = len(issues)
        issues = [i for i in issues if "pull_request" not in i]  # drop PRs
        logger.debug(f"Fetched {len(issues)} issues (excluding PRs) from page {page}")
        for issue in issues:
            updated_str = issue.get("updated_at") or issue.get("created_at")
            if updated_str:
                try:
                    issue_dt = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
                except Exception as e:
                    logger.debug(f"Failed to parse issue date '{updated_str}': {e}")
                    pass

            issue_number = issue.get("number")
            if issue_number:
                logger.debug(f"Fetching comments for issue #{issue_number}")
                comments = fetch_updated_comment_from_github(client, owner, repo, issue_number, start_time, end_time)
                issue["comments"] = comments
                logger.debug(f"Found {len(comments)} comments for issue #{issue_number}")
            yield issue
        if issues_length < per_page:
            logger.debug(f"Last page reached (got {len(issues)} issues, expected {per_page})")
            break
        page += 1
        time.sleep(0.2)
    logger.info(f"Total issues fetched for {owner}/{repo}: {len(results)}")
    return results

def fetch_updated_reviews_from_github(client: GitHubAPIClient, owner: str, repo: str,pr_number:int,  start_time: datetime, end_time: datetime) -> List[Dict]:
    logger.info(f"Fetching reviews for {owner}/{repo} PR #{pr_number} from {start_time} to {end_time}")
    results: List[Dict] = []
    page = 1
    per_page = 100
    while True:
        params = {
            "per_page": per_page,
            "page": page,
            "since": start_time.isoformat() if start_time else None,
            "until": end_time.isoformat() if end_time else None,
        }
        reviews = client.rest_request(f"/repos/{owner}/{repo}/pulls/{pr_number}/comments", params)
        if not reviews:
            logger.debug(f"No more reviews found at page {page}")
            break
        for review in reviews:
            updated_str = review.get("updated_at") or review.get("created_at")
            if updated_str:
                try:
                    review_dt = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))

                    # Ensure start_time and end_time are timezone-aware for comparison
                    if start_time:
                        if start_time.tzinfo is None:
                            start_time_aware = start_time.replace(tzinfo=timezone.utc)
                        else:
                            start_time_aware = start_time
                        if review_dt < start_time_aware:
                            continue

                    if end_time:
                        if end_time.tzinfo is None:
                            end_time_aware = end_time.replace(tzinfo=timezone.utc)
                        else:
                            end_time_aware = end_time
                        if review_dt > end_time_aware:
                            continue
                except Exception as e:
                    logger.debug(f"Failed to parse review date '{updated_str}': {e}")
                    pass
            results.append(review)
        if len(reviews) < per_page:
            logger.debug(f"Last page reached (got {len(reviews)} reviews, expected {per_page})")
            break
        page += 1
        time.sleep(0.2)
    logger.info(f"Total reviews fetched for {owner}/{repo} PR #{pr_number}: {len(results)}")
    return results

def fetch_updated_pr_from_github(client: GitHubAPIClient, owner: str, repo: str, start_time: datetime, end_time: datetime) -> List[Dict]:
    logger.info(f"Fetching PRs for {owner}/{repo} from {start_time} to {end_time}")
    # results: List[Dict] = []
    page = 1
    per_page = 100
    while True:
        params = {
            "state": "all",
            "per_page": per_page,
            "page": page,
            "sort": "updated",
            "direction": "desc",
        }
        prs = client.rest_request(f"/repos/{owner}/{repo}/pulls", params)
        if not prs:
            logger.debug(f"No more PRs found at page {page}")
            break
        flag = False
        for pr in prs:
            updated_str = pr.get("updated_at") or pr.get("created_at")
            logger.info(f"Fetching PR #{pr.get('number')} with updated_str: {updated_str}")
            if updated_str:
                try:
                    pr_dt = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))

                    # Ensure start_time and end_time are timezone-aware for comparison
                    if start_time:
                        if start_time.tzinfo is None:
                            start_time_aware = start_time.replace(tzinfo=timezone.utc)
                        else:
                            start_time_aware = start_time
                        if pr_dt < start_time_aware:
                            flag = True
                            break

                    if end_time:
                        if end_time.tzinfo is None:
                            end_time_aware = end_time.replace(tzinfo=timezone.utc)
                        else:
                            end_time_aware = end_time
                        if pr_dt > end_time_aware:
                            continue
                    logger.info(f"Fetching comments for PR #{pr['number']}")
                    pr["comments"] = fetch_updated_comment_from_github(client, owner, repo, pr["number"], start_time, end_time)
                    time.sleep(0.5)

                    logger.info(f"Fetching reviews for PR #{pr['number']}")
                    pr["reviews"] = fetch_updated_reviews_from_github(client, owner, repo, pr["number"], start_time, end_time)
                    time.sleep(0.5)
                    yield pr
                except Exception as e:
                    logger.info(f"Failed to parse PR date '{updated_str}': {e}")
                    pass

        if len(prs) < per_page or flag:
            logger.debug(f"Last page reached (got {len(prs)} PRs, expected {per_page})")
            break
        page += 1
        time.sleep(0.2)

