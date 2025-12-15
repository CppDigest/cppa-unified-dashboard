import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Dict
from models import Base, Commit, PullRequest, Issue, Email, Identity, User, IssueComment, PullRequestComment, PullRequestReview
from datetime import datetime, timezone


class Database:

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        session = sessionmaker(bind=self.engine)()
        return session

    def close(self):
        self.engine.dispose()

    def get_last_commit_date(self, repo: str):
        session = self.get_session()
        try:
            last_commit = session.query(Commit).filter(Commit.repo == repo).order_by(Commit.commit_date.desc()).first()
            return last_commit.commit_date if last_commit else None
        finally:
            session.close()

    def get_last_issue_date(self, repo: str):
        session = self.get_session()
        try:
            last_issue = session.query(Issue).filter(Issue.repo == repo).order_by(Issue.updated_at.desc()).first()
            return last_issue.updated_at if last_issue else None
        finally:
            session.close()

    def get_last_pr_date(self, repo: str):
        session = self.get_session()
        try:
            last_pr = session.query(PullRequest).filter(PullRequest.repo == repo).order_by(PullRequest.updated_at.desc()).first()
            return last_pr.updated_at if last_pr else None
        finally:
            session.close()

    def get_email_id(self, email: str = "", name: str = "", info: str = "", avatar_url: str = "", source: str = "", session=None):
        """
        Get or create email ID. If session is provided, use it; otherwise create a new one.
        """
        if session is None:
            return None

        try:
            if email == "":
                if source == "github" and info != "":
                    email = f"{info}@users.noreply.github.com"

            if email == "":
                raise ValueError(f"Email is empty for name: {name}, info: {info}, source: {source}")

            email_obj = session.query(Email).filter(Email.email == email).first()
            if not email_obj:
                name = name or info
                identity = Identity(name=name, description="Auto-generated identity from GitHub", needs_review=False)
                session.add(identity)
                session.flush()
                email_obj = Email(email=email, identity_id=identity.id)
                session.add(email_obj)
                session.flush()
                user = User(email_id=email_obj.id, name=name, info=info, avatar_url=avatar_url, source=source)
                session.add(user)
                session.flush()
                session.commit()
                return email_obj.id
            else:
                user = session.query(User).filter(User.email_id == email_obj.id, source == source).first()
                if user:
                    if user.name == "" and name != "" and name != None:
                        user.name = name
                    if user.info == "" and info != "" and info != None:
                        user.info = info
                    if user.avatar_url == "" and avatar_url != "" and avatar_url != None:
                        user.avatar_url = avatar_url
                    session.flush()
                    session.commit()
                    return email_obj.id
                else:
                    user = User(email_id=email_obj.id, name=name, info=info, avatar_url=avatar_url, source=source)
                    session.add(user)
                    session.flush()
                    session.commit()
                    return email_obj.id
        except Exception as e:
            session.rollback()
            print(f"Error getting email ID: {e}")
            raise


    def get_user_info(self, user: Dict = None):
        if user is None:
            email = "ghost@deleted.account.github.com"
            name = ""
            info = ""
            avatar_url = ""
            return email, name, info, avatar_url
        else:
            return user.get('email', ""), user.get('name', ""), user.get('login', ""), user.get('avatar_url', "")

    def insert_pull_request_comment(self, comment: Dict, pr_number: int, repo: str, session=None):
        if session is None:
            return None

        try:
            updated_at = comment.get('updated_at')
            if updated_at and isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            pr_comment_id = comment.get('id')
            pr_current_comment = session.query(PullRequestComment).filter(PullRequestComment.pr_comment_id == pr_comment_id).first()
            if pr_current_comment:
                pr_current_comment.body = comment['body']
                pr_current_comment.updated_at = updated_at
                session.flush()
                session.commit()
                return pr_current_comment.id
            else:

                email, name, info, avatar_url = self.get_user_info(user=comment.get('user'))

                email_id = self.get_email_id(email, name, info, avatar_url, "github", session=session)

                created_at = comment.get('created_at')
                if created_at and isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                push_data = {
                    "pr_number": pr_number,
                    "pr_comment_id": pr_comment_id,
                    "body": comment['body'],
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "email_id": email_id,
                    "repo": repo
                }
                session.add(PullRequestComment(**push_data))
                session.flush()
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error inserting pull request comment: {e}")
            raise

    def insert_pull_request_review(self, review: Dict, pr_number: int, repo: str, session=None):
        if session is None:
            return None

        try:
            updated_at = review.get('updated_at')
            if updated_at and isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

            pr_review_id = review.get('id')
            pr_current_review = session.query(PullRequestReview).filter(PullRequestReview.pr_review_id == pr_review_id).first()
            if pr_current_review:
                pr_current_review.body = review['body']
                pr_current_review.updated_at = updated_at
                session.flush()
                session.commit()
                return pr_current_review.id
            else:
                email, name, info, avatar_url = self.get_user_info(user=review.get('user'))

                email_id = self.get_email_id(email, name, info, avatar_url, "github", session=session)

                created_at = review.get('created_at')
                if created_at and isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                push_data = {
                    "pr_number": pr_number,
                    "pr_review_id": pr_review_id,
                    "body": review['body'],
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "email_id": email_id,
                    "repo": repo,
                    "in_reply_to_id": review.get('in_reply_to_id', None),
                }
                session.add(PullRequestReview(**push_data))
                session.flush()
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error inserting pull request review: {e}")
            raise

    def insert_pull_request(self, pr: Dict, repo: str, session=None):
        if session is None:
            return None
        try:

            pr_number = pr.get("number", "")

            for comment in pr.get("comments", []):
                self.insert_pull_request_comment(comment, pr_number, repo, session)
            for review in pr.get("reviews", []):
                self.insert_pull_request_review(review, pr_number, repo, session)

            updated_at = pr.get('updated_at')
            if updated_at and isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            merged_at = pr.get('merged_at')
            if merged_at and isinstance(merged_at, str):
                merged_at = datetime.fromisoformat(merged_at.replace("Z", "+00:00"))
            closed_at = pr.get('closed_at')
            if closed_at and isinstance(closed_at, str):
                closed_at = datetime.fromisoformat(closed_at.replace("Z", "+00:00"))

            pr_id = pr.get('id')
            pr_current_pr = session.query(PullRequest).filter(PullRequest.pr_id == pr_id).first()
            if pr_current_pr:
                pr_current_pr.title = pr['title']
                pr_current_pr.body = pr['body']
                pr_current_pr.updated_at = updated_at
                pr_current_pr.merged_at = merged_at
                pr_current_pr.closed_at = closed_at
                session.flush()
                session.commit()
                return pr_current_pr.id
            else:

                email, name, info, avatar_url = self.get_user_info(user=pr.get('user'))
                email_id = self.get_email_id(email, name, info, avatar_url, "github", session=session)


                created_at = pr.get('created_at')
                if created_at and isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

                push_data = {
                    "pr_number": pr_number,
                    "pr_id": pr['id'],
                    "title": pr['title'],
                    "body": pr['body'],
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "merged_at": merged_at,
                    "closed_at": closed_at,
                    "email_id": email_id,
                    "repo": repo,
                    "state": pr['state'],
                }

                session.add(PullRequest(**push_data))
                session.flush()
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error inserting pull request: {e}")
            raise

    def insert_issue_comment(self, comment: Dict, issue_number: int, repo: str, session=None):
        if session is None:
            return None
        try:

            email, name, info, avatar_url = self.get_user_info(user=comment.get('user'))

            email_id = self.get_email_id(email, name, info, avatar_url, "github", session=session)

            updated_at = comment.get('updated_at')
            if updated_at and isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

            issue_comment_id = comment.get('id')
            issue_current_comment = session.query(IssueComment).filter(IssueComment.issue_comment_id == issue_comment_id).first()
            if issue_current_comment:
                issue_current_comment.body = comment['body']
                issue_current_comment.updated_at = updated_at
                session.flush()
                session.commit()
                return issue_current_comment.id
            else:
                created_at = comment.get('created_at')
                if created_at and isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                push_data = {
                    "issue_number": issue_number,
                    "issue_comment_id": issue_comment_id,
                    "body": comment['body'],
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "email_id": email_id,
                    "repo": repo,
                }
                session.add(IssueComment(**push_data))
                session.flush()
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error inserting issue comment: {e}")
            raise

    def insert_issue(self, issue: Dict, repo: str, session=None):
        if session is None:
            return None
        try:
            issue_number = issue.get("number", "")
            for comment in issue.get("comments", []):
                self.insert_issue_comment(comment, issue_number, repo, session)

            # Reuse the same session for get_email_id to avoid creating multiple sessions
            email, name, info, avatar_url = self.get_user_info(user=issue.get('user'))
            email_id = self.get_email_id(email, name, info, avatar_url, "github", session=session)

            # Parse datetime strings if they are strings
            updated_at = issue.get("updated_at")
            if updated_at and isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

            closed_at = issue.get("closed_at")
            if closed_at and isinstance(closed_at, str):
                closed_at = datetime.fromisoformat(closed_at.replace("Z", "+00:00"))

            issue_id = issue.get("id")
            issue_current_issue = session.query(Issue).filter(Issue.issue_id == issue_id).first()
            if issue_current_issue:
                issue_current_issue.title = issue.get("title")
                issue_current_issue.body = issue.get("body")
                issue_current_issue.updated_at = updated_at
                issue_current_issue.closed_at = closed_at
                session.flush()
                session.commit()
                return issue_current_issue.id
            else:
                created_at = issue.get("created_at")
                if created_at and isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

                push_data = {
                    "issue_number": issue_number,
                    "issue_id": issue_id,
                    "title": issue.get("title"),
                    "body": issue.get("body"),
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "closed_at": closed_at,
                    "email_id": email_id,
                    "repo": repo,
                    "state": issue.get("state"),
                    "state_reason": issue.get("state_reason"),
                }
                session.add(Issue(**push_data))
                session.flush()
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error inserting issue: {e}")
            raise

    def insert_commit(self, commit: Dict, repo: str, session=None):
        if session is None:
            return None
        try:
            commit_hash = commit.get('sha')
            email = ""
            name = ""
            commit_date = None
            if commit.get('commit'):
                author = commit.get('commit').get('author')
                committer = commit.get('commit').get('committer')
                author_email = ""
                author_name = ""
                author_commit_date = None
                committer_email = ""
                committer_name = ""
                committer_commit_date = None
                if author:
                    author_email = author.get('email')
                    author_name = author.get('name')
                    author_commit_date = datetime.fromisoformat(author.get('date').replace("Z", "+00:00"))
                elif committer:
                    committer_email = committer.get('email')
                    committer_name = committer.get('name')
                    committer_commit_date = datetime.fromisoformat(committer.get('date').replace("Z", "+00:00"))
                email = author_email or committer_email or ""
                name = author_name or committer_name or ""
                commit_date = author_commit_date or committer_commit_date or None
            if commit.get('author'):
                info = commit.get('author').get('info')
                avatar_url = commit.get('author').get('avatar_url')
            elif commit.get('committer'):
                info = commit.get('committer').get('info')
                avatar_url = commit.get('committer').get('avatar_url')
            else:
                info = ""
                avatar_url = ""

            if email == "":
                if info != "":
                    email = f"{info}@users.noreply.github.com"
                else:
                    email = f"nobody@localhost"

            email_id = self.get_email_id(email, name, info, avatar_url, "github", session=session)

            comment = commit.get('commit').get('message')

            # Check if commit already exists (based on unique constraint: commit_hash + repo)
            existing_commit = session.query(Commit).filter(
                Commit.commit_hash == commit_hash,
                Commit.repo == repo
            ).first()

            if existing_commit:
                existing_commit.commit_date = commit_date
                existing_commit.comment = comment
                session.flush()
                session.commit()
                return existing_commit.id
            else:
                # Insert new commit
                new_commit = Commit(
                    email_id=email_id,
                    commit_date=commit_date,
                    repo=repo,
                    comment=comment,
                    commit_hash=commit_hash
                )
                session.add(new_commit)
                session.flush()
                session.commit()
                return new_commit.id
        except Exception as e:
            session.rollback()
            print(f"Error inserting commit: {e}")
            raise

