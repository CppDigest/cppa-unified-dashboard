## Prisma schema relations (CPPA Unified Dashboard)

This document summarizes the models and relations defined in `prisma/schema.prisma` for quick reference.

### Relations summary

- Message → User: many-to-one (`Message.userId` references `User.id`)
- Message → Channel: many-to-one (`Message.channelId` references `Channel.id`)
- Message → Message (self): optional parent-child thread relation via `threadTs`.
  - In Prisma: `parentMessage: Message? @relation("ThreadMessages", fields: [threadTs], references: [id])`
  - And backref: `threadMessages: Message[] @relation("ThreadMessages")`
- Message → Reaction: one-to-many (Reactions belong to a Message)
- Message → File: one-to-many (Files belong to a Message)
- Reaction → User: many-to-one (`Reaction.userId` → `User.id`)
- File → Message: many-to-one (`File.messageId` → `Message.id`)
- Channel → User: many-to-one (`Channel.creator` references `User.id`)
- Channel → Message: one-to-many (Messages belong to a Channel)

### Indexes and constraints (high level)

- Message
  - `@@index([channelId])`, `@@index([userId])`, `@@index([threadTs])`
  - `clientMsgId` is unique (optional)
- Reaction
  - Composite unique: `@@unique([messageId, userId, name])`
- File
  - `slackFileId` unique
  - Indexes on `messageId` and `userId`
- Channel
  - `@@index([creator])`, `@@index([contextTeamId])`, `@@index([isPrivate])`, `@@index([isArchived])`
- User
  - `@@index([teamId])`, `@@index([isBot])`, `@@index([isDeleted])`

### Notes

- `threadTs` implements the thread relationship by referencing `Message.id`; root messages have `threadTs = null` (or equal to their own `ts` are treated as roots in code).
- Timestamps: most models include `createdAt` with `@default(now())` and `updatedAt` with `@updatedAt`.
- Channel model includes Slack API fields: `created`, `updated` (DateTime), `creator` (User relation), and various channel type flags.
- User model includes `updated` field (DateTime) for Slack user update timestamps.
- All timestamp fields use DateTime type to handle Unix timestamps in milliseconds from Slack API.
