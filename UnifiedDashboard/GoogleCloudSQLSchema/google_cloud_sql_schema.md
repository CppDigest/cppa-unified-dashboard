# Database Schema Documentation

This document describes the database schema for the Boost Dashboard.

## Dashboard Data Requirements

- Track Boost library repositories, commits, issues, and pull requests with their key metrics and activities.

- Monitor Boost libraries, headers, versions, dependencies, and usage tracking across repositories.

- Track library dependency changes (addition/removal history) and processed repositories (processing status, Boost inclusion tracking).

- Monitor Slack activity (cpplang channel activity, team/channel information, message counts) and mailing lists (message counts, thread tracking, mailing list types).

- Resolve contributor profiles across platforms (email addresses, GitHub/Slack profiles) and track WG21 papers (authors and publications).

- Track website statistics (daily visit counts, visits by country, search word frequency and counts).

## Executive Summary

This database schema supports the Boost Dashboard. It tracks and analyzes Boost library development, community engagement, and ecosystem health. The schema has eight main parts:

**Part 1: Core Identity Schema** - Creates a unified identity system. It links contributors across GitHub, Slack, and mailing lists using email addresses and profiles. This allows tracking contributors across all platforms.

**Part 2: GitHub Schema** - Captures GitHub activity data. It includes commits, issues, pull requests, labels, and assignees for Boost library repositories. It tracks metrics like lines added or removed, issue states, PR reviews, and repository information such as stars, forks, language, and license.

**Part 3: Boost Library Schema** - Manages Boost library information. It stores library details, header files, version history, and dependencies between libraries. It also tracks how Boost libraries are used in external repositories. This enables tracking of library changes, version releases, and adoption patterns.

**Part 4: Slack Schema** - Tracks communication in Slack workspaces. It includes teams, channels, channel members, and messages. It supports thread tracking for conversations.

**Part 5: WG21 Papers Schema** - Records C++ Standards Committee papers and their authors. It links papers to contributor identities.

**Part 6: Mailing List Schema** - Captures mailing list messages with thread tracking. This enables analysis of community discussions and communication patterns.

**Part 7: Web Search Schema** - Stores website analytics. It includes daily visit counts, visits by country, and search word frequency statistics.

**Part 8: Pinecone Fail List Schema** - Tracks failed Pinecone operations. It records items that failed to be processed or indexed in the Pinecone vector database, categorized by type (mailing list, WG21 paper, Slack, etc.).

The schema uses email addresses as the central linking mechanism. This allows contributors to be tracked across all platforms. Data integrity is maintained through foreign key relationships and unique constraints. Most tables include timestamps (`created_at`, `updated_at`) to track when data changes.

## Entity Relationship Diagrams

**Legend:** PK = Primary Key, FK = Foreign Key, UK = Unique Key, IX = Index

### Part 1: Core Identity Schema (Identity, Email, Profile)

```mermaid
erDiagram
    direction LR
    Identity {
        int id PK
        string display_name "IX"
        text description
        datetime created_at
        datetime updated_at
    }

    Email {
        int id PK
        int identity_id FK
        string email "IX"
        boolean is_primary
        datetime created_at
        datetime updated_at
    }

    BaseProfile {
        int id PK
        int email_id FK
        datetime created_at
        datetime updated_at
    }

    GitHubProfile {
        bigint account_id "IX"
        string username "IX"
        string display_name "IX"
        string avatar_url
    }

    SlackProfile {
        string slack_user_id "IX"
        string username "IX"
        string display_name "IX"
        string avatar_url
    }

    MailingListProfile {
        string display_name "IX"
    }

    WG21PaperAuthorProfile {
        string display_name "IX"
    }

    TmpIdentity {
        int id PK
        string display_name "IX"
        text description
        datetime created_at
        datetime updated_at
    }

    EmailToMerge {
        int id PK
        int email_id FK
        int target_identity_id FK
        datetime created_at
        datetime updated_at
    }

    Identity ||--o{ Email : "has"
    Email ||--o{ BaseProfile : "has"
    BaseProfile ||--o| GitHubProfile : "extends"
    BaseProfile ||--o| SlackProfile : "extends"
    BaseProfile ||--o| MailingListProfile : "extends"
    BaseProfile ||--o| WG21PaperAuthorProfile : "extends"
    Email ||--o{ EmailToMerge : "has"
    TmpIdentity ||--o{ EmailToMerge : "target"
```

**Note:** The `email` field in the Email table is not unique. Multiple records with the same email address may exist, differentiated by `created_at` and `updated_at` timestamps to track historical changes.

**Note:** GitHubProfile, SlackProfile, MailingListProfile, and WG21PaperAuthorProfile extend BaseProfile (one-to-one).

### Part 2a: GitHub Schema - Repository

```mermaid
erDiagram
    direction LR
    GitHubProfile ||--o{ GitHubRepository : "owns"
    GitHubRepository ||--o{ RepoLanguage : "has"
    GitHubRepository ||--o{ RepoLicense : "has"
    Language ||--o{ RepoLanguage : "used_in"
    License ||--o{ RepoLicense : "used_in"

    GitHubProfile {
        bigint account_id "IX"
        string username "IX"
        string display_name "IX"
        string avatar_url
    }

    GitHubRepository {
        int id PK
        int owner_id FK
        string repo_name "IX"
        string repo_type "IX"
        int stars
        int forks
        text description
        datetime repo_pushed_at "IX"
        datetime repo_created_at "IX"
        datetime repo_updated_at "IX"
        datetime created_at
        datetime updated_at
    }

    Language {
        int id PK
        string name UK "IX"
        datetime created_at
    }

    License {
        int id PK
        string name UK "IX"
        string spdx_id "IX"
        string url
        datetime created_at
    }

    RepoLanguage {
        int id PK
        int repo_id FK
        int language_id FK
        int line_count
        datetime created_at
        datetime updated_at
    }

    RepoLicense {
        int id PK
        int repo_id FK
        int license_id FK
        datetime created_at
    }
```

**Note:** Composite unique constraints should be applied on: (`owner_id`, `repo_name`) in GitHubRepository, (`repo_id`, `language_id`) in RepoLanguage, (`repo_id`, `license_id`) in RepoLicense.

### Part 2b: GitHub Schema - Commits and Issues

```mermaid
erDiagram
    direction LR
    GitHubRepository ||--o{ GitCommit : "contains"
    GitHubRepository ||--o{ Issue : "contains"
    Issue ||--o{ IssueComment : "has"
    Issue ||--o{ IssueAssignee : "has"
    Issue ||--o{ IssueLabel : "has"

    GitHubRepository {
        int id PK
        int owner_id FK
        string repo_name "IX"
        string repo_type "IX"
        int stars
        int forks
        text description
        datetime repo_pushed_at "IX"
        datetime repo_created_at "IX"
        datetime repo_updated_at "IX"
        datetime created_at
        datetime updated_at
    }

    GitCommit {
        bigint id PK
        int repo_id FK
        bigint account_id "IX"
        string commit_hash UK "IX"
        text comment
        int changed_files
        int added_lines
        int deleted_lines
        datetime commit_at "IX"
    }

    Issue {
        int id PK
        int repo_id FK
        bigint account_id "IX"
        int issue_number "IX"
        bigint issue_id UK "IX"
        text title
        text body
        string state "IX"
        string state_reason
        datetime issue_created_at "IX"
        datetime issue_updated_at "IX"
        datetime issue_closed_at "IX"
    }

    IssueComment {
        int id PK
        int issue_id FK
        bigint account_id "IX"
        bigint issue_comment_id UK "IX"
        text body
        datetime issue_comment_created_at
        datetime issue_comment_updated_at
    }

    IssueAssignee {
        int id PK
        int issue_id FK
        bigint account_id "IX"
        datetime created_at
    }

    IssueLabel {
        int id PK
        int issue_id FK
        string label_name "IX"
        datetime created_at
    }
```

**Note:** `account_id` fields reference `account_id` in GitHubProfile (not a FK).

**Note:** Composite unique constraints should be applied on: (`repo_id`, `commit_hash`) in GitCommit, (`repo_id`, `issue_number`) in Issue, (`issue_id`, `account_id`) in IssueAssignee, (`issue_id`, `label_name`) in IssueLabel.

### Part 2c: GitHub Schema - Pull Requests

```mermaid
erDiagram
    direction LR
    GitHubRepository ||--o{ PullRequest : "contains"
    PullRequest ||--o{ PullRequestReview : "has"
    PullRequest ||--o{ PullRequestComment : "has"
    PullRequest ||--o{ PullRequestAssignee : "has"
    PullRequest ||--o{ PullRequestLabel : "has"

    GitHubRepository {
        int id PK
        int owner_id FK
        string repo_name "IX"
        string repo_type "IX"
        int stars
        int forks
        text description
        datetime repo_pushed_at "IX"
        datetime repo_created_at "IX"
        datetime repo_updated_at "IX"
        datetime created_at
        datetime updated_at
    }

    PullRequest {
        int id PK
        int repo_id FK
        bigint account_id "IX"
        int pr_number "IX"
        bigint pr_id UK "IX"
        text title
        text body
        string state "IX"
        datetime pr_created_at "IX"
        datetime pr_updated_at "IX"
        datetime pr_merged_at "IX"
        datetime pr_closed_at "IX"
    }

    PullRequestReview {
        int id PK
        int pr_id FK
        bigint account_id "IX"
        bigint pr_review_id UK "IX"
        text body
        bigint in_reply_to_id
        datetime pr_review_created_at "IX"
        datetime pr_review_updated_at "IX"
    }

    PullRequestComment {
        int id PK
        int pr_id FK
        bigint account_id "IX"
        bigint pr_comment_id UK "IX"
        text body
        datetime pr_comment_created_at "IX"
        datetime pr_comment_updated_at "IX"
    }

    PullRequestAssignee {
        int id PK
        int pr_id FK
        bigint account_id "IX"
        datetime created_at
    }

    PullRequestLabel {
        int id PK
        int pr_id FK
        string label_name "IX"
        datetime created_at
    }
```

**Note:** Composite unique constraints should be applied on: (`repo_id`, `pr_number`) in PullRequest, (`pr_id`, `account_id`) in PullRequestAssignee, (`pr_id`, `label_name`) in PullRequestLabel.

### Part 3a: Boost Library Schema

```mermaid
erDiagram
    direction LR
    GitHubRepository ||--o| BoostLibrary : "extends"
    BoostLibrary ||--o{ BoostHeader : "has"
    BoostLibrary ||--o{ BoostDependency : "main_library"
    BoostLibrary ||--o{ BoostDependency : "dependency_library"
    BoostVersion ||--o{ BoostDependency : "version"
    BoostVersion ||--o{ BoostLibrary : "created_version"
    BoostVersion ||--o{ BoostLibrary : "last_updated_version"
    BoostVersion ||--o{ BoostLibrary : "removed_version"
    BoostVersion ||--o{ IncludeBoostRepository : "version"
    BoostVersion ||--o{ IncludeBoostRepository : "candidate_version"
    GitHubRepository ||--o| IncludeBoostRepository : "extends"
    IncludeBoostRepository ||--o{ BoostUsage : "repo"
    BoostHeader ||--o{ BoostUsage : "header"

    GitHubRepository {
        int id PK
        int owner_id FK
        string repo_name "IX"
        string repo_type "IX"
        int stars
        int forks
        text description
        datetime repo_pushed_at "IX"
        datetime repo_created_at "IX"
        datetime repo_updated_at "IX"
        datetime created_at
        datetime updated_at
    }

    BoostLibrary {
        int created_version_id FK
        int last_updated_version_id FK
        int removed_version_id FK
        string name "IX"
        string cpp_version
        text description
    }

    BoostHeader {
        int id PK
        int library_id FK
        string header_name "IX"
        string full_header_name "IX"
        datetime last_commit_date "IX"
        datetime created_at
        datetime updated_at
    }

    BoostVersion {
        int id PK
        string version UK "IX"
        text updated_libraries
        text included_libraries
        datetime created_at
        datetime updated_at
    }

    BoostDependency {
        int id PK
        int main_library_id FK
        int version_id FK
        int dependency_library_id FK
        datetime created_at
    }

    IncludeBoostRepository {
        int boost_version_id FK
        int boost_candidate_version_id FK
        boolean boost_change_safe
    }

    BoostUsage {
        int id PK
        int repo_id FK
        int boost_header_id FK
        text file_path
        datetime last_commit_date "IX"
        date excepted_at
        datetime created_at
        datetime updated_at
    }
```

**Note:** BoostLibrary and IncludeBoostRepository extend GitHubRepository (one-to-one).

**Note:** Composite unique constraint should be applied on: (`main_library_id`, `version_id`, `dependency_library_id`) in BoostDependency.

### Part 3b: Boost Library Schema - Other

```mermaid
erDiagram
    direction LR
    BoostLibrary ||--o{ DependencyChangeLog : "library"
    BoostLibrary ||--o{ DependencyChangeLog : "dep_library"

    BoostLibrary {
        int created_version_id FK
        int last_updated_version_id FK
        int removed_version_id FK
        string name "IX"
        string cpp_version
        text description
    }

    DependencyChangeLog {
        int id PK
        int library_id FK
        int dep_library_id FK
        boolean is_add
        date created_at "IX"
    }

    ProcessedRepository {
        int id PK
        text repo_name "IX"
        boolean includes_boost
        datetime processed_at "IX"
    }
```

**Note:** Composite unique constraint should be applied on: (`library_id`, `dep_library_id`, `created_at`) in DependencyChangeLog.

### Part 4: Slack Schema

```mermaid
erDiagram
    direction LR
    SlackTeam ||--o{ SlackChannel : "has"
    SlackChannel ||--o{ SlackChannelMember : "has"
    SlackChannel ||--o{ SlackMessage : "contains"

    SlackTeam {
        int id PK
        string team_id UK "IX"
        string team_name
        datetime created_at
        datetime updated_at
    }

    SlackChannel {
        int id PK
        int team_id FK
        string channel_id UK "IX"
        string channel_name "IX"
        string channel_type
        text description
        string creator_user_id
        datetime created_at
        datetime updated_at
    }

    SlackChannelMember {
        int id PK
        int channel_id FK
        string user_id "IX"
        boolean is_joined
        datetime created_at
    }

    SlackMessage {
        bigint id PK
        int channel_id FK
        string ts UK "IX"
        string user_id "IX"
        text message
        string thread_ts "IX"
        datetime slack_message_created_at "IX"
        datetime slack_message_updated_at "IX"
    }
```

**Note:** `user_id` fields reference `slack_user_id` in SlackProfile (not a FK).

**Note:** Composite unique constraint should be applied on: (`channel_id`, `ts`) in SlackMessage, (`channel_id`, `user_id`, `created_at`) in SlackChannelMember.

### Part 5: WG21 Papers Schema

```mermaid
erDiagram
    WG21PaperAuthorProfile ||--o{ WG21PaperAuthor : "author"
    WG21Paper ||--o{ WG21PaperAuthor : "has"

    WG21PaperAuthorProfile {
        string display_name
    }

    WG21PaperAuthor {
        int id PK
        int paper_id FK
        int profile_id FK
        datetime created_at
    }

    WG21Paper {
        int id PK
        string paper_id UK "IX"
        string url
        string title "IX"
        date publication_date "IX"
        datetime created_at
        datetime updated_at
    }
```

**Note:** Composite unique constraint should be applied on: (`paper_id`, `profile_id`) in WG21PaperAuthor.

### Part 6: Mailing List Schema

```mermaid
erDiagram
    direction LR
    Email ||--o{ MailingListMessage : "sender"

    Email {
        int id PK
        int identity_id FK
        string email UK "IX"
        boolean is_primary
        datetime created_at
        datetime updated_at
    }

    MailingListMessage {
        int id PK
        int sender_id FK
        string msg_id UK "IX"
        string parent_id "IX"
        string thread_id "IX"
        string subject
        text content
        string list_name "IX"
        datetime sent_at "IX"
        datetime created_at
    }
```

### Part 7: Web Search Schema

```mermaid
erDiagram
    Website {
        int id PK
        date stat_date UK "IX"
        int website_visit_count
    }

    WebsiteVisitCount {
        int id PK
        date stat_date "IX"
        string country "IX"
        int count
    }

    WebsiteWordCount {
        int id PK
        date stat_date "IX"
        string word "IX"
        int count
    }
```

**Note:** Composite unique constraints should be applied on: (`stat_date`, `country`) in WebsiteVisitCount, (`stat_date`, `word`) in WebsiteWordCount.

### Part 8: Pinecone Fail List Schema

```mermaid
erDiagram
    PineconeFailList {
        int id PK
        string failed_id UK "IX"
        string type "IX"
        datetime created_at
    }
```

## Table Descriptions

### Core Identity Tables

#### `identity`

Represents a contributor identity that groups multiple email addresses belonging to the same person. Used for identity resolution across different platforms.

**Key Fields:**

- `display_name`: Human-readable name for the identity
- `description`: Additional notes about the identity

#### `email`

Stores email addresses linked to identities. Acts as the central linking table connecting contributors to their activities across GitHub and Slack.

**Key Fields:**

- `email`: Unique email address (unique constraint)
- `identity_id`: Links to the parent identity
- `is_primary`: Indicates if this is the primary email for the identity

#### `base_profile`

Base profile table that links email addresses to platform-specific profiles. Acts as the parent table for extended profile types (GitHub, Slack, Mailing List).

**Key Fields:**

- `email_id`: Foreign key linking to the Email table

#### `github_profile`

Extended profile table for GitHub accounts. Stores GitHub-specific user information. Inherits `id`, `email_id`, `created_at`, `updated_at` from the BaseProfile table. Also serves as the repository owner reference.

**Key Fields:**

- `account_id`: GitHub account ID (numeric)
- `username`: GitHub username
- `display_name`: Display name on GitHub
- `avatar_url`: URL to the GitHub avatar image

#### `slack_profile`

Extended profile table for Slack accounts. Stores Slack-specific user information. Inherits `id`, `email_id`, `created_at`, `updated_at` from the BaseProfile table.

**Key Fields:**

- `slack_user_id`: Slack user ID
- `username`: Slack username
- `display_name`: Display name on Slack
- `avatar_url`: URL to the Slack avatar image

#### `mailing_list_profile`

Extended profile table for mailing list contributors. Stores mailing list-specific user information. Inherits `id`, `email_id`, `created_at`, `updated_at` from the BaseProfile table.

**Key Fields:**

- `display_name`: Display name used in mailing list messages

#### `wg21_paper_author_profile`

Extended profile table for WG21 paper authors. Stores WG21-specific author information. Inherits `id`, `email_id`, `created_at`, `updated_at` from the BaseProfile table.

**Key Fields:**

- `display_name`: Display name used in WG21 paper authorship

#### `tmp_identity`

Temporary table for storing proposed identity records during the human review process. These identities are candidates for merging into the main Identity table after approval.

**Key Fields:**

- `display_name`: Human-readable name for the proposed identity
- `description`: Additional notes about the proposed identity

#### `email_to_merge`

Temporary table for human review of identity merging. Stores proposed email-to-identity associations that require manual verification before merging.

**Key Fields:**

- `email_id`: Foreign key linking to the Email table (the email to be merged)
- `target_identity_id`: Foreign key linking to the TmpIdentity table (the target temporary identity to merge into)

### GitHub Tables

#### `github_repo`

Stores GitHub repository information. Each repository belongs to one owner (GitHubProfile). Tracks Boost libraries being monitored for activity.

**Key Fields:**

- `owner_id`: Foreign key linking to the GitHubProfile table (the repository owner)
- `repo_name`: Repository name
- `repo_type`: Type/category of repository
- `stars`: Number of stars the repository has received
- `forks`: Number of forks of the repository
- `description`: Repository description/topic
- `repo_pushed_at`: Timestamp of the last push to the repository (from GitHub)
- `repo_created_at`: Timestamp when the repository was created on GitHub
- `repo_updated_at`: Timestamp when the repository was last updated on GitHub
- `created_at`: Timestamp when this record was added to the database
- `updated_at`: Timestamp when this record was last updated in the database

#### `language`

Stores programming language information. Used for tracking which languages are used in repositories.

**Key Fields:**

- `name`: Language name (unique constraint)

#### `license`

Stores software license information. Used for tracking which licenses are used in repositories.

**Key Fields:**

- `name`: License name (unique constraint)
- `spdx_id`: SPDX license identifier (e.g., "MIT", "Apache-2.0", "GPL-3.0")
- `url`: URL to the license text

#### `repo_language`

Junction table establishing the many-to-many relationship between repositories and programming languages. One repository can use multiple languages, and one language can be used in multiple repositories.

**Key Fields:**

- `repo_id`: Foreign key linking to the GitHubRepository table
- `language_id`: Foreign key linking to the Language table
- `line_count`: Number of lines of code in this language for the repository

#### `repo_license`

Junction table establishing the many-to-many relationship between repositories and licenses. One repository can have multiple licenses, and one license can be used in multiple repositories.

**Key Fields:**

- `repo_id`: Foreign key linking to the GitHubRepository table
- `license_id`: Foreign key linking to the License table

#### `github_commit`

Stores Git commit information including commit metadata and statistics.

**Key Fields:**

- `commit_hash`: Unique commit hash (unique per repository)
- `commit_at`: When the commit was made
- `comment`: Commit message
- `changed_files`: Number of files changed
- `added_lines`: Lines added in the commit
- `deleted_lines`: Lines deleted in the commit

#### `github_issue`

Stores GitHub issue information including title, body, and state.

**Key Fields:**

- `issue_number`: Issue number within the repository
- `issue_id`: Unique GitHub issue ID
- `state`: Issue state (open, closed, etc.)
- `state_reason`: Reason for the current state (completed, closed, etc)

#### `github_issue_comment`

Stores comments made on GitHub issues.

**Key Fields:**

- `issue_id`: Foreign key linking to the Issue table
- `issue_comment_id`: Unique GitHub comment ID
- `body`: Comment content

#### `github_issue_assignee`

Junction table establishing the many-to-many relationship between GitHub issues and their assignees. One issue can have multiple assignees, and one email (person) can be assigned to multiple issues.

**Key Fields:**

- `issue_id`: Foreign key linking to the Issue table
- `email_id`: Foreign key linking to the Email table (identifies the assignee)

#### `github_issue_label`

Junction table establishing the many-to-many relationship between GitHub issues and labels. One issue can have multiple labels, and one label name can be applied to multiple issues.

**Key Fields:**

- `issue_id`: Foreign key linking to the Issue table
- `label_name`: Name of the label (e.g., "bug", "enhancement", "documentation")

#### `github_pull_request`

Stores GitHub pull request information including merge and close timestamps.

**Key Fields:**

- `pr_number`: Pull request number within the repository
- `pr_id`: Unique GitHub PR ID
- `state`: PR state (open, closed, merged)
- `merged_at`: When the PR was merged (if applicable)
- `closed_at`: When the PR was closed

#### `github_pull_request_review`

Stores review comments and approvals on pull requests.

**Key Fields:**

- `pr_id`: Foreign key linking to the PullRequest table
- `pr_review_id`: Unique GitHub review ID
- `in_reply_to_id`: ID of the review being replied to (for threaded reviews)

#### `github_pull_request_comment`

Stores comments on pull requests (non-review comments).

**Key Fields:**

- `pr_id`: Foreign key linking to the PullRequest table
- `pr_comment_id`: Unique GitHub comment ID
- `body`: Comment content

#### `github_pull_request_assignee`

Junction table establishing the many-to-many relationship between GitHub pull requests and their assignees. One pull request can have multiple assignees, and one email (person) can be assigned to multiple pull requests. Note that the creator of a PR (stored in `github_pull_request.email_id`) is separate from assignees.

**Key Fields:**

- `pr_id`: Foreign key linking to the PullRequest table
- `email_id`: Foreign key linking to the Email table (identifies the assignee)

#### `github_pull_request_label`

Junction table establishing the many-to-many relationship between GitHub pull requests and labels. One pull request can have multiple labels, and one label name can be applied to multiple pull requests.

**Key Fields:**

- `pr_id`: Foreign key linking to the PullRequest table
- `label_name`: Name of the label (e.g., "bug", "enhancement", "documentation")

#### `dependency_change_log`

Stores dependency change history between Boost libraries. Tracks when one Boost library depends on another Boost library, including when dependencies are added or removed.

**Key Fields:**

- `library_id`: Foreign key linking to the BoostLibrary table (the Boost library that has the dependency)
- `dep_library_id`: Foreign key linking to the BoostLibrary table (the Boost library being depended upon)
- `is_add`: Boolean flag indicating whether this dependency was added (true) or removed (false)
- `created_at`: Date when this dependency relationship was recorded

**Note:** This table tracks the history of dependency changes.

#### `processed_repository`

Stores processing status of repositories. Used for tracking which repositories have been processed and whether they include Boost.

**Key Fields:**

- `repo_name`: Repository name (text)
- `processed_at`: Timestamp when the repository was processed
- `includes_boost`: Boolean flag indicating if the repository includes Boost

**Note:** This table is used only for recording processing status and does not have any foreign key relationships.

### Boost Library Tables

#### `boost_library`

Stores Boost library information. Each Boost library is linked to a GitHub repository and tracks version information.

**Key Fields:**

- `name`: Boost library name
- `repo_id`: Foreign key linking to the GitHubRepository table
- `created_version_id`: Foreign key linking to the BoostVersion table (version when the library was first created)
- `last_updated_version_id`: Foreign key linking to the BoostVersion table (last version when the library was updated)
- `removed_version_id`: Foreign key linking to the BoostVersion table (version when the library was removed, if applicable)
- `cpp_version`: C++ version requirement for the library
- `description`: Library description
- `repo_type`: Type of repository (should be 'boost-library')

#### `boost_header`

Stores header file information for Boost libraries. Each header belongs to a Boost library.

**Key Fields:**

- `library_id`: Foreign key linking to the BoostLibrary table
- `header_name`: Short header name (e.g., "algorithm")
- `full_header_name`: Full header path (e.g., "boost/algorithm/string.hpp")
- `last_commit_date`: Timestamp of the last commit that modified this header

#### `boost_version`

Stores Boost release version information. Tracks which libraries were updated or included in each version.

**Key Fields:**

- `version`: Boost version string (e.g., "1.84.0")
- `updated_libraries`: Text field listing libraries updated in this version
- `included_libraries`: Text field listing libraries included in this version

#### `boost_dependency`

Stores dependency relationships between Boost libraries for specific versions. Tracks which libraries depend on other libraries in each Boost version.

**Key Fields:**

- `main_library_id`: Foreign key linking to the BoostLibrary table (the library that has the dependency)
- `version_id`: Foreign key linking to the BoostVersion table
- `dependency_library_id`: Foreign key linking to the BoostLibrary table (the library being depended upon)

#### `include_boost_repository`

Stores information about repositories that include/use Boost libraries. Links external repositories to Boost versions they use.

**Key Fields:**

- `repo_id`: Foreign key linking to the GitHubRepository table
- `boost_change_safe`: Boolean flag indicating if the repository is safe from Boost changes
- `boost_version_id`: Foreign key linking to the BoostVersion table (current Boost version used)
- `boost_candidate_version_id`: Foreign key linking to the BoostVersion table (candidate Boost version)
- `repo_type`: Type of repository (should be 'include boost repository')

#### `boost_usage`

Stores usage information of Boost headers in external repositories. Tracks which Boost headers are used in which files.

**Key Fields:**

- `repo_id`: Foreign key linking to the IncludeBoostRepository table
- `file_path`: Path to the file using the Boost header
- `boost_header_id`: Foreign key linking to the BoostHeader table
- `last_commit_date`: Timestamp of the last commit that modified this usage
- `excepted_at`: Date when this usage was excepted/excluded from tracking

### Slack Tables

#### `slack_team`

Stores Slack workspace/team information.

**Key Fields:**

- `team_id`: Unique Slack team ID
- `team_name`: Name of the Slack team/workspace

#### `slack_channel`

Stores Slack channel information including channel type and creator.

**Key Fields:**

- `channel_id`: Unique Slack channel ID
- `channel_name`: Name of the channel
- `channel_type`: Type of channel (public, private, etc.)
- `description`: Channel description/topic
- `creator_user_id`: Slack user ID of the channel creator (matches `slack_user_id` in SlackProfile)

#### `slack_channel_member`

Junction table linking channels to their members.

**Key Fields:**

- `channel_id`: Associated channel
- `user_id`: Slack user ID of the member (matches `slack_user_id` in SlackProfile)
- `is_joined`: Whether the user is currently a member

#### `slack_message`

Stores Slack messages including thread information.

**Key Fields:**

- `ts`: Slack timestamp identifier
- `user_id`: Slack user ID of the message author (matches `slack_user_id` in SlackProfile)
- `message`: Message content
- `thread_ts`: Timestamp of parent message (if this is a thread reply)
- `created_at`: When the message was sent
- `updated_at`: When the message was last edited

### WG21 Papers Tables

#### `wg21_paper`

Stores metadata for WG21 (C++ Standards Committee) papers. Papers can have multiple authors, which are tracked through the `wg21_paper_author` junction table.

**Key Fields:**

- `paper_id`: Unique identifier for the WG21 paper (e.g., "p1234r5", "n4567")
- `url`: Full URL to the paper document
- `title`: Paper title
- `publication_date`: Date when the paper was published/submitted

#### `wg21_paper_author`

Junction table establishing the many-to-many relationship between WG21 papers and their authors. One paper can have multiple authors, and one author can write multiple papers.

**Key Fields:**

- `paper_id`: Foreign key linking to the WG21Paper table
- `profile_id`: Foreign key linking to the WG21PaperAuthorProfile table (identifies the author)

### Mailing List Tables

#### `mailing_list_message`

Stores messages from mailing lists (e.g., Boost mailing lists). Tracks email threads, parent-child relationships, and message metadata.

**Key Fields:**

- `msg_id`: Unique message identifier (unique constraint)
- `parent_id`: Message ID of the parent message (string, stores the `msg_id` of the parent message for threaded conversations)
- `thread_id`: Thread identifier to group related messages together
- `subject`: Message subject line
- `content`: Message body/content
- `sender_id`: Foreign key linking to the Email table (identifies the sender)
- `sent_at`: Timestamp when the message was sent
- `list_name`: Name of the mailing list (e.g., "boost@lists.boost.org")

**Note:** The `parent_id` field stores the `msg_id` of the parent message as a string reference to track message threads. A unique constraint should be applied on `msg_id` to prevent duplicate messages.

### Web Search Tables

#### `website`

Stores overall website visit statistics aggregated by date.

**Key Fields:**

- `stat_date`: Statistics date (unique constraint) - represents a single day
- `website_visit_count`: Total number of website visits on this date

**Note:** A unique constraint should be applied on `stat_date` to ensure one record per day.

#### `website_visit_count`

Stores website visit statistics broken down by country and date.

**Key Fields:**

- `stat_date`: Statistics date - represents a single day
- `country`: Country code or name
- `count`: Number of visits from this country on this date

#### `website_word_count`

Stores search word frequency statistics by date.

**Key Fields:**

- `stat_date`: Statistics date - represents a single day
- `word`: Search word or keyword
- `count`: Number of times this word was searched on this date

### Pinecone Fail List Tables

#### `pinecone_fail_list`

Stores records of failed Pinecone operations. Tracks items that failed to be processed or indexed in Pinecone vector database.

**Key Fields:**

- `failed_id`: Unique identifier of the failed item (unique constraint) - the ID of the item that failed (e.g., message ID, paper ID, Slack message ID)
- `type`: Type of the failed item (e.g., "mailing list", "wg21 paper", "slack", etc.)

**Note:** A unique constraint should be applied on `failed_id` to prevent duplicate failure records. The `type` field categorizes the source of the failed item for easier tracking and debugging.

## Relationships Summary

- **Identity -> Email**: One-to-many (one identity can have multiple emails)
- **Email -> BaseProfile**: One-to-many (one email can have multiple profiles)
- **BaseProfile -> GitHubProfile**: One-to-one (one base profile can have one GitHub profile extension)
- **BaseProfile -> SlackProfile**: One-to-one (one base profile can have one Slack profile extension)
- **BaseProfile -> MailingListProfile**: One-to-one (one base profile can have one mailing list profile extension)
- **BaseProfile -> WG21PaperAuthorProfile**: One-to-one (one base profile can have one WG21 paper author profile extension)
- **Email -> All Activity Tables**: One-to-many (one email can have many commits, issues, PRs, mailing list messages, etc.)
- **SlackProfile (via user_id) -> SlackChannelMember**: One-to-many (one Slack user can be a member of multiple channels)
- **SlackProfile (via user_id) -> SlackMessage**: One-to-many (one Slack user can send multiple messages)
- **Email -> MailingListMessage**: One-to-many (one email can send multiple mailing list messages)
- **WG21PaperAuthorProfile <-> WG21Paper**: Many-to-many (through WG21PaperAuthor - one profile can author multiple papers, one paper can have multiple authors)
- **Email <-> Issue**: Many-to-many (through IssueAssignee - one email can be assigned to multiple issues, one issue can have multiple assignees)
- **Email <-> PullRequest**: Many-to-many (through PullRequestAssignee - one email can be assigned to multiple PRs, one PR can have multiple assignees. Note: PR creator is separate from assignees)
- **Issue <-> Label**: Many-to-many (through IssueLabel - one issue can have multiple labels, one label name can be applied to multiple issues)
- **PullRequest <-> Label**: Many-to-many (through PullRequestLabel - one PR can have multiple labels, one label name can be applied to multiple PRs)
- **GitHubProfile -> GitHubRepository**: One-to-many (one GitHub profile/owner can have multiple repositories)
- **GitHubRepository <-> Language**: Many-to-many (through RepoLanguage - one repository can use multiple languages, one language can be used in multiple repositories)
- **GitHubRepository <-> License**: Many-to-many (through RepoLicense - one repository can have multiple licenses, one license can be used in multiple repositories)
- **GitHubRepository -> All GitHub Activity Tables**: One-to-many (one repository contains many commits, issues, PRs, etc.)
- **BoostLibrary <-> BoostLibrary**: Many-to-many (through DependencyChangeLog - one Boost library can depend on multiple Boost libraries, one Boost library can be depended upon by multiple Boost libraries)
- **GitHubRepository -> BoostLibrary**: One-to-one (one repository can be one Boost library)
- **BoostLibrary -> BoostHeader**: One-to-many (one Boost library has many headers)
- **BoostVersion -> BoostLibrary**: One-to-many (created_version_id - one version can be the creation version for multiple libraries)
- **BoostVersion -> BoostLibrary**: One-to-many (last_updated_version_id - one version can be the last update version for multiple libraries)
- **BoostVersion -> BoostLibrary**: One-to-many (removed_version_id - one version can be the removal version for multiple libraries)
- **BoostLibrary <-> BoostLibrary**: Many-to-many (through BoostDependency - one library can depend on multiple libraries, one library can be depended upon by multiple libraries, per version)
- **BoostVersion -> BoostDependency**: One-to-many (one Boost version has many dependency relationships)
- **BoostVersion -> IncludeBoostRepository**: One-to-many (one Boost version can be used by multiple repositories)
- **GitHubRepository -> IncludeBoostRepository**: One-to-one (one repository can be one include Boost repository)
- **IncludeBoostRepository -> BoostUsage**: One-to-many (one include Boost repository has many Boost header usages)
- **BoostHeader -> BoostUsage**: One-to-many (one Boost header can be used in multiple files/repositories)
- **SlackTeam -> SlackChannel**: One-to-many (one team has many channels)
- **SlackChannel -> SlackChannelMember**: One-to-many (one channel has many members)
- **SlackChannel -> SlackMessage**: One-to-many (one channel contains many messages)

## Notes

- All tables use integer primary keys with auto-increment except `GitCommit` and `SlackMessage` which use `BigInteger`
- Foreign keys use `ondelete='SET NULL'` to preserve data integrity when referenced records are deleted
- Most tables include `created_at` and `updated_at` timestamps for audit purposes
- Email addresses serve as the central linking mechanism between identities and their activities across platforms
- The `boost_library` table should have `repo_type` set to 'boost-library'
- The `include_boost_repository` table should have `repo_type` set to 'include boost repository'
- The `processed_repository` table is used only for tracking processing status and has no foreign key relationships
- All composite unique constraints are documented in the diagram notes above each ERD section
