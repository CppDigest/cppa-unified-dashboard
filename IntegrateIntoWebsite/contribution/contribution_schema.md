# Contribution Models - Field Relationship Diagram

```mermaid
erDiagram
    Email {
        int id PK "AutoField, Primary Key — unique identifier for each contributor email record"
        string email "EmailField, max_length=255, Indexed — contributor's email address"
        string name "CharField, max_length=255, nullable — contributor's full name (optional)"
        string info "CharField, max_length=255, nullable — extra info (e.g., GitHub username)"
        string source "CharField, max_length=255, default='user', Indexed — origin of email (github/user/etc.), part of unique (email, source)"
        datetime created_at "DateTimeField, auto_now_add — timestamp when record created"
        datetime updated_at "DateTimeField, auto_now — timestamp when record last updated"
    }

    EmailIdentifier {
        int id PK "AutoField, Primary Key — unique identifier for each email identifier"
        string name UK "CharField, max_length=255, unique — identifier's unique name"
        text description "TextField, nullable — human-readable description of the identifier"
        boolean needs_review "BooleanField, default=False — flag for AI-generated identifiers needing manual review"
        datetime created_at "DateTimeField, auto_now_add — timestamp when identifier created"
        datetime updated_at "DateTimeField, auto_now — timestamp when identifier last updated"
    }

    EmailIdentifierRelation {
        int id PK "AutoField, Primary Key — unique identifier for each email-identifier link"
        int email_id FK "ForeignKey -> Email.id, CASCADE — linked contributor email"
        int email_identifier_id FK "ForeignKey -> EmailIdentifier.id, CASCADE — linked identifier"
        datetime created_at "DateTimeField, auto_now_add — timestamp when relation created"
    }

    GitHubContribution {
        int id PK "AutoField, Primary Key — unique identifier for each GitHub contribution"
        int email_id FK "ForeignKey -> Email.id, CASCADE, Indexed — contributor email tied to the event"
        string type "CharField, max_length=50, choices=CONTRIBUTION_TYPES, Indexed — category of contribution"
        datetime date "DateTimeField, nullable, Indexed — when the contribution occurred"
        string repo "CharField, max_length=255, nullable, Indexed — repository name for the contribution"
        text comment "TextField, nullable — comment/message linked to the event"
        string info "CharField, max_length=255, nullable — extra info (commit hash, PR number, issue number)"
    }

    Wg21Contribution {
        int id PK "AutoField, Primary Key — unique identifier for each WG21 paper contribution"
        int email_id FK "ForeignKey -> Email.id, CASCADE, Indexed — contributor email tied to the contribution"
        int year "IntegerField, nullable, Indexed — year of the contribution"
        string title "CharField, max_length=255, nullable — title of the paper where the contribution was made"
        string paper_id "CharField, max_length=255, nullable — paper ID where the contribution was made"
    }

    Email ||--o{ EmailIdentifierRelation : "has many (email_id)"
    EmailIdentifier ||--o{ EmailIdentifierRelation : "has many (email_identifier_id)"
    Email ||--o{ GitHubContribution : "has many (email_id)"
    Email ||--o{ Wg21Contribution : "has many (email_id)"

    EmailIdentifierRelation }o--|| Email : "belongs to (email)"
    EmailIdentifierRelation }o--|| EmailIdentifier : "belongs to (email_identifier)"
    GitHubContribution }o--|| Email : "belongs to (email)"
    Wg21Contribution }o--|| Email : "belongs to (email)"

    EmailIdentifier }o--o{ Email : "many-to-many through EmailIdentifierRelation"
```

## Remark

- Email Model: (email, source) - ensures unique email per source (same email can exist with different sources, but each combination is unique)

- EmailIdentifierRelation Model: (email, email_identifier) - ensures unique relationship between email and identifier pairs (each email can be connected to multiple identifiers, but the same email-identifier pair cannot be duplicated)
