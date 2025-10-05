## Prisma schema relations (CPPA Unified Dashboard)

This document summarizes the models and relations defined in `prisma/schema.prisma` for quick reference.

### Relations summary

- Message → User: many-to-one (`Message.userId` references `User.id`)
- Message → Message (self): optional parent-child thread relation via `threadTs`.
  - In Prisma: `parentMessage: Message? @relation("ThreadMessages", fields: [threadTs], references: [id])`
  - And backref: `threadMessages: Message[] @relation("ThreadMessages")`
- Message → Reaction: one-to-many (Reactions belong to a Message)
- Message → File: one-to-many (Files belong to a Message)
- Reaction → User: many-to-one (`Reaction.userId` → `User.id`)
- File → Message: many-to-one (`File.messageId` → `Message.id`)
- Channel: standalone (no explicit relations in schema)

### Indexes and constraints (high level)

- Message
  - `@@index([channelId])`, `@@index([userId])`, `@@index([threadTs])`
  - `clientMsgId` is unique (optional)
- Reaction
  - Composite unique: `@@unique([messageId, userId, name])`
- File
  - `slackFileId` unique
  - Indexes on `messageId` and `userId`

### Notes

- `threadTs` implements the thread relationship by referencing `Message.id`; root messages have `threadTs = null` (or equal to their own `ts` are treated as roots in code).
- Timestamps: most models include `createdAt` with `@default(now())` and `updatedAt` with `@updatedAt`.
