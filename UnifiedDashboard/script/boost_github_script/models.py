"""
SQLAlchemy models for Boost Contributor Database
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, event, text
from sqlalchemy.orm import DeclarativeBase, relationship, foreign
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Identity(Base):
    """Identity table - represents a contributor identity"""
    __tablename__ = 'identity'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    needs_review = Column(Boolean, default=False, nullable=False)

    # Relationships
    emails = relationship("Email", back_populates="identity", cascade="save-update, merge, expunge")


class Email(Base):
    """Email table - email addresses linked to identities"""
    __tablename__ = 'email'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    identity_id = Column(Integer, ForeignKey('identity.id', ondelete='SET NULL'), nullable=True, index=True)

    # Relationships
    identity = relationship("Identity", back_populates="emails")
    users = relationship("User", back_populates="email", cascade="all, delete-orphan")
    commits = relationship("Commit", back_populates="email", cascade="all, delete-orphan")
    pull_requests = relationship("PullRequest", back_populates="email", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="email", cascade="all, delete-orphan")
    issue_comments = relationship("IssueComment", back_populates="email", cascade="all, delete-orphan")
    pull_request_reviews = relationship("PullRequestReview", back_populates="email", cascade="all, delete-orphan")
    pull_request_comments = relationship("PullRequestComment", back_populates="email", cascade="all, delete-orphan")


class User(Base):
    """User table - user profiles with source information"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey('email.id', ondelete='SET NULL'), nullable=True, index=True)
    name = Column(String(255), nullable=True, index=True)
    info = Column(String(255), nullable=True, index=True)
    source = Column(String(255), nullable=True, index=True)
    avatar_url = Column(String(500), nullable=True)

    # Relationships
    email = relationship("Email", back_populates="users")

class Commit(Base):
    """Commit table - Git commits"""
    __tablename__ = 'commit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey('email.id', ondelete='SET NULL'), nullable=True, index=True)
    commit_date = Column(DateTime(timezone=True), nullable=True, index=True)
    repo = Column(String(255), nullable=True, index=True)
    comment = Column(Text, nullable=True)
    commit_hash = Column(String(255), nullable=True, index=True)

    __table_args__ = (
        UniqueConstraint('commit_hash', 'repo', name='uq_commit_hash_repo'),
    )

    # Relationships
    email = relationship("Email", back_populates="commits")

class PullRequest(Base):
    """PullRequest table - GitHub pull requests"""
    __tablename__ = 'prs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pr_number = Column(Integer, nullable=False, index=True)
    pr_id = Column(BigInteger, nullable=False, index=True, unique=True)
    title = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, index=True)
    merged_at = Column(DateTime(timezone=True), nullable=True, index=True)
    closed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    email_id = Column(Integer, ForeignKey('email.id', ondelete='SET NULL'), nullable=True, index=True)
    repo = Column(String(255), nullable=True, index=True)
    state = Column(String(255), nullable=True, index=True)

    # Relationships
    email = relationship("Email", back_populates="pull_requests")

class Issue(Base):
    """Issue table - GitHub issues"""
    __tablename__ = 'issue'

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_number = Column(Integer, nullable=False, index=True)
    issue_id = Column(BigInteger, nullable=False, index=True, unique=True)
    title = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, index=True)
    closed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    email_id = Column(Integer, ForeignKey('email.id', ondelete='SET NULL'), nullable=True, index=True)
    repo = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True, index=True)
    state_reason = Column(String(255), nullable=True, index=True)

    # Relationships
    email = relationship("Email", back_populates="issues")

class IssueComment(Base):
    """IssueComment table - comments on GitHub issues"""
    __tablename__ = 'issue_comment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_number = Column(Integer, nullable=False, index=True)
    issue_comment_id = Column(BigInteger, nullable=False, index=True, unique=True)
    body = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, index=True)
    email_id = Column(Integer, ForeignKey('email.id', ondelete='SET NULL'), nullable=True, index=True)
    repo = Column(String(255), nullable=True, index=True)

    # Relationships
    email = relationship("Email", back_populates="issue_comments")
    issue = relationship(
        "Issue",
        primaryjoin="and_(IssueComment.issue_number == foreign(Issue.issue_number), IssueComment.repo == Issue.repo)",
        viewonly=True  # Read-only since there's no FK
    )

class PullRequestReview(Base):
    """PullRequestReview table - reviews on GitHub pull requests"""
    __tablename__ = 'prs_review'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pr_number = Column(Integer, nullable=False, index=True)
    pr_review_id = Column(BigInteger, nullable=False, index=True, unique=True)
    body = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, index=True)
    email_id = Column(Integer, ForeignKey('email.id', ondelete='SET NULL'), nullable=True, index=True)
    repo = Column(String(255), nullable=True)
    in_reply_to_id = Column(BigInteger, nullable=True, index=True)

    # Relationships
    email = relationship("Email", back_populates="pull_request_reviews")
    pr_reviews = relationship(
        "PullRequest",
        primaryjoin="and_(PullRequestReview.pr_number == foreign(PullRequest.pr_number), PullRequestReview.repo == PullRequest.repo)",
        viewonly=True  # Read-only since there's no FK
    )

class PullRequestComment(Base):
    """PullRequestComment table - comments on GitHub pull requests"""
    __tablename__ = 'prs_comment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pr_number = Column(Integer, nullable=False, index=True)
    pr_comment_id = Column(BigInteger, nullable=False, index=True, unique=True)
    body = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, index=True)
    email_id = Column(Integer, ForeignKey('email.id', ondelete='SET NULL'), nullable=True, index=True)
    repo = Column(String(255), nullable=True, index=True)

    # Relationships
    email = relationship("Email", back_populates="pull_request_comments")
    pr_comments = relationship(
        "PullRequest",
        primaryjoin="and_(PullRequestComment.pr_number == foreign(PullRequest.pr_number), PullRequestComment.repo == PullRequest.repo)",
        viewonly=True  # Read-only since there's no FK
    )


# Event listener to handle email deletion - set all related records to ghost email
@event.listens_for(Email, "before_delete")
def handle_email_delete(mapper, connection, target):
    """
    Before deleting an Email, update all related records to point to the ghost email.
    The ghost email should have address 'ghost@deleted.account.github.com'
    """
    ghost_email_address = 'ghost@deleted.account.github.com'

    # Get or create ghost email using raw SQL
    result = connection.execute(
        text("SELECT id FROM email WHERE email = :email"),
        {"email": ghost_email_address}
    ).first()

    if result:
        ghost_email_id = result[0]
    else:
        # Create ghost identity first
        identity_result = connection.execute(
            text("""
                INSERT INTO identity (name, description, needs_review)
                VALUES ('Ghost User', 'Deleted GitHub account', false)
                RETURNING id
            """)
        ).first()

        identity_id = identity_result[0] if identity_result else None

        if identity_id:
            # Create ghost email
            email_result = connection.execute(
                text("""
                    INSERT INTO email (email, identity_id)
                    VALUES (:email, :identity_id)
                    RETURNING id
                """),
                {"email": ghost_email_address, "identity_id": identity_id}
            ).first()
            ghost_email_id = email_result[0] if email_result else None
        else:
            ghost_email_id = None

    if ghost_email_id:
        # Update all related tables to point to ghost email
        tables_to_update = [
            'user',
            'commit',
            'prs',
            'issue',
            'issue_comment',
            'prs_review',
            'prs_comment'
        ]

        for table in tables_to_update:
            connection.execute(
                text(f"UPDATE {table} SET email_id = :ghost_id WHERE email_id = :deleted_id"),
                {"ghost_id": ghost_email_id, "deleted_id": target.id}
            )