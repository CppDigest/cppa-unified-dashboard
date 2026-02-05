# Cursor Subscription vs. API Key Mechanics and Plan Comparison Report

## Executive Summary

This report addresses the mechanics of using subscriptions versus API keys with Cursor, and provides a detailed comparison of Cursor's Pro, Teams, and Enterprise plans. Key findings:

- **Web subscriptions (ChatGPT Plus, Claude Pro) cannot be used directly in Cursor** - they are separate products with separate billing
- **API keys can be used in Cursor via BYO (Bring Your Own) keys**, but Cursor still applies token fees on Teams plans
- **Cost conversion is not 1:1** - web subscriptions use message/session limits, not token-based pricing
- **Pooled usage is only available on Enterprise** - Teams plans have per-seat usage that cannot be shared
- **Administrative Control** - Teams admins set limits and alerts, Enterprise adds granular billing and member-level controls.
- **Tired Deployment** -No, All users on a Teams or Enterprise plan must be on the same tier
- **Value parity exists at the API level** - $20 on Teams provides the same prompts/tokens as $20 on Enterprise (same API rates + Cursor fee)

---

## 1. Subscription vs. API Key Mechanics

### 1.1 Integration: Can Web Subscriptions Be Used in Cursor?

**Short Answer: No. Web subscriptions and API usage are strictly separate.**

#### OpenAI (ChatGPT) Integration

- **ChatGPT Plus, Business, Enterprise, and Edu** are web plans on chatgpt.com with flat monthly pricing and model-specific message limits. [1][3][4]
- **The API on platform.openai.com** is billed separately on a pay-per-token basis. OpenAI explicitly states that ChatGPT and the API are separate platforms and billing details do not transfer. [2]
- **No OAuth or direct integration exists** - there is no supported way to connect a ChatGPT Plus, Business, or Enterprise web subscription as a billing source in Cursor. [2][14]

#### Anthropic (Claude) Integration

- **Claude Pro, Max, and Claude for Work** (Team and Enterprise) are web subscriptions at claude.ai with usage caps and session or weekly limits. [8][9][10]
- **Anthropic support is explicit**: paid Claude plans do not include API usage; API access requires a separate Claude Console account and billing. [7][13]
- **No direct connection** - Cursor cannot use Claude web subscription credentials for API access.

#### Cursor's Access Modes

Cursor supports two ways to use AI models:

1. **Built-in Cursor-metered usage:**

   - Individual, Teams, and Enterprise plans include some AI usage that Cursor measures and bills at model API list prices plus a Cursor token fee. [14][15][20]

2. **Bring-your-own (BYO) API keys:**
   - Users can add OpenAI, Anthropic, Gemini, Azure OpenAI, and AWS Bedrock keys under Settings → Models. [19]
   - When enabled, Cursor sends model calls through those keys; vendor bills the API usage directly, while Cursor may still charge its own token fee depending on plan. [15][19]

**Conclusion:** Web subscriptions cannot be used directly in Cursor. Only API keys (BYO or Cursor-managed) can be used.

### 1.2 Cost Conversion: Dollars to Tokens

**Short Answer: There is no precise conversion rate. Web subscriptions use message/session limits, not token-based pricing.**

#### Why Direct Conversion Doesn't Work

**OpenAI Web Plans:**

- ChatGPT Plus offers access to advanced models with variable message caps that can tighten during high demand; there is no published token allowance. [1]
- ChatGPT Business and Enterprise publish matrices of model-specific limits (e.g., effectively unlimited GPT-4o messages but daily or weekly caps for higher-cost models like GPT-4.1). [3][4]
- Limits are in **messages**, not tokens, and can change over time.

**Anthropic Web Plans:**

- Claude Pro has session-based limits that reset roughly every five hours, with approximate ranges of messages and Claude Code prompts per session. [8]
- Claude Max increases those limits by factors such as 5x or 20x, again with session resets and weekly usage guidance. [9]
- Claude for Work Team and Enterprise define included weekly usage per seat and allow purchase of extra usage at API rates once those limits are hit. [10][11]

**API Pricing (for comparison):**

| Provider and Model (API)   | Input Price (USD / 1M tokens) | Output Price (USD / 1M tokens) | Notes            |
| -------------------------- | ----------------------------: | -----------------------------: | ---------------- |
| OpenAI GPT-4o mini         |                          0.15 |                           0.60 | Low-cost model   |
| Other OpenAI GPT-4.x/5.x   |   Varies, higher than 4o mini |                         Varies | See API pricing  |
| Anthropic Claude Haiku 4.5 |                          1.00 |                           5.00 | Fast, lower cost |

Sources: OpenAI API pricing and Anthropic Haiku 4.5 announcement. [5][12]

#### Cost Insight

- **Light users** usually pay a higher effective per-token price in exchange for a simple subscription
- **Heavy users** close to the caps may see lower effective per-token cost but can still be throttled rather than paying overage
- **No vendor-backed dollars-per-token figure exists** for web plans because limits are in messages or sessions, not tokens

**Conclusion:** $1 on an API key does NOT buy the same amount of prompts/completions as $1 of a monthly subscription. Web subscriptions are convenience bundles with opaque, variable effective per-token costs.

---

## 2. Cursor Plan Comparison: Pro vs. Teams vs. Enterprise

### 2.1 Pooled Usage: How Does It Work in Enterprise?

**Short Answer: Enterprise provides shared organizational usage pools. Teams does not pool usage.**

#### Teams Plan - No Pooling

- **Each user has their own 20 USD included usage per month**; unused included usage cannot be moved to other team members. [15][21]
- **Heavy users who exceed their own included usage** move into on-demand billing, even if others have unused capacity. [15][16]
- **Per-seat usage is tracked individually** and does not transfer between team members. [15][21]

#### Enterprise Plan - Pooled Usage

- **Enterprise users draw from a shared pool of usage**, so heavy users can consume a larger share while light users consume less. [18][21]
- **High-usage users can automatically draw from unused allotments** of others within the shared pool. [18][21]
- **Admins can still impose per-member limits** to prevent a single user from exhausting the pool. [16][17]

**Conclusion:** Only Enterprise supports pooled usage. Teams plans have per-seat usage that cannot be shared.

### 2.2 Administrative Control: Usage Limits and Top-Ups

**Short Answer: Teams admins set spend limits and alerts, but cannot top up usage. Enterprise adds controls.**

#### Teams Plan Admin Controls

**Usage-Limit Notifications (Spend Alerts):**

- Spend alerts send **email notifications** when configured thresholds of on-demand spend are reached at team or member level. [17]
- Alerts **do not block usage** - they are informational only. [17]
- Admins can configure alerts for:
  - Team-level spend thresholds
  - Individual member spend thresholds
  - On-demand usage (included usage doesn't count toward alerts) [17]

**Topping Up a Specific User:**

- Teams plans do **not support direct "top-ups"** of included usage for individual users
- When a user exhausts their 20 USD included usage, they automatically move to on-demand billing at API rates plus Cursor token fee (0.25 USD per million tokens) [15]
- Admins can:
  - **Adjust spend limits** to allow more on-demand usage for specific users [16]
  - **View per-user spend** in the admin dashboard [15][16]
  - **Set team-level spend limits** to control overall costs [16]

#### Enterprise Plan Admin Controls

- **Enhanced visibility** - For Enterprise with pooled usage, alerts can be based on total spend per member, not only on-demand spend, giving more accurate visibility into high-consumption users. [17]
- **Billing groups** - Admins can group users and associate spend with specific cost centers or projects. [18]
- **Advanced analytics APIs** - Enterprise includes analytics and service account APIs for programmatic access to usage data. [18]
- **Member-level limits** - Admins can set per-member limits within the shared pool to prevent abuse. [16][17]

**Conclusion:** Teams admins can set spend limits and receive alerts, but cannot directly "top up" included usage. Enterprise provides more granular controls including billing groups and member-level limits within the shared pool.

### 2.3 Tiered Deployment: Mixed Plans Within an Organization

**Short Answer: No. All users on a Teams or Enterprise plan must be on the same tier.**

#### Teams Plan Structure

- **Teams plans are flat-rate** - 40 USD per active user per month, with each seat including 20 USD of AI usage. [15]
- **All team members share the same plan** - there is no option to have some users on a $40/mo plan and others on higher tiers within the same Teams account.
- **Individual plans are separate** - Individual Pro, Pro Plus, and Ultra plans cannot be mixed with Teams plans in the same organization account.

#### Enterprise Plan Structure

- **Enterprise is custom and contract-based** - specific discounts and allowances are negotiated and not published. [15][18]
- **Contract terms determine structure** - while Enterprise may offer more flexibility in pricing and usage allocation, the specific mechanics would be defined in the contract.
- **Billing groups** allow admins to group users and associate spend with specific cost centers, but this is for accounting purposes, not tiered pricing. [18]

**Conclusion:** Cursor does not support tiered deployment where some employees are on smaller plans ($40/mo) while power users are on higher plans within the same org account. Teams is a flat per-seat rate, and Enterprise terms are contract-specific.

### 2.4 Value Parity: Does $20 on Teams Equal $20 on Enterprise?

**Short Answer: Yes, at the API pricing level. Both use the same underlying API rates plus Cursor token fees.**

#### Pricing Structure Comparison

**Teams Plan:**

- **Base cost:** 40 USD per active user per month
- **Included usage:** 20 USD per seat per month of AI usage, priced at public API list prices plus the Cursor token fee (0.25 USD per million tokens for non-Auto agent requests) [15]
- **Overage pricing:** Same API list prices plus 0.25 USD per million tokens [15]

**Enterprise Plan:**

- **Base cost:** Custom contract-based pricing
- **Included usage:** Pooled usage (details per contract), but based on underlying model API prices plus Cursor fees [15][18]
- **Overage pricing:** API prices plus Cursor fee (contracted rates, but public docs indicate same API list prices) [15][18]

#### Token-Level Cost Parity

- **Both plans use the same underlying API rates** from OpenAI, Anthropic, etc. [15][18][20]
- **Both plans apply Cursor token fees** on top of API costs [15][18]
- **Public documentation indicates the same API list prices** plus Cursor fee structure for both Teams and Enterprise [15][18]
- **Enterprise may have negotiated discounts** on the base API rates, but these would be contract-specific and not publicly documented [18]

**Conclusion:** $20 of usage on Teams provides the same prompts/tokens as $20 on Enterprise, assuming the same models are used and Enterprise hasn't negotiated special API discounts. The difference is in pooling (Enterprise) vs. per-seat allocation (Teams), not in per-token pricing.

---

## 3. Detailed Plan Feature Comparison

### 3.1 Comprehensive Feature Matrix

| Aspect                      | Individual (Pro, Pro Plus, Ultra)                           | Teams                                      | Enterprise                                               |
| --------------------------- | ----------------------------------------------------------- | ------------------------------------------ | -------------------------------------------------------- |
| **Billing scope**           | Single user                                                 | Team with centralized billing              | Organization-wide                                        |
| **Base cost**               | Varies by tier (Pro ~$20/mo)                                | 40 USD per active user/month               | Custom contract                                          |
| **Included usage**          | Fixed dollars of usage per user (~20 USD equivalent on Pro) | 20 USD usage per seat per month            | Pooled usage (details per contract)                      |
| **Pooling across users**    | No                                                          | No                                         | Yes                                                      |
| **Overage pricing**         | API prices plus Cursor fee                                  | API prices plus 0.25 USD per M tokens      | API prices plus Cursor fee (contracted)                  |
| **Spend limits**            | User limits and alerts                                      | User and team limits and alerts            | Team and member limits and alerts on pooled usage        |
| **BYO API keys**            | Supported for some providers                                | Supported; token fee still applies         | Supported; details may be negotiated                     |
| **Admin dashboard**         | User-level only                                             | Team activity, usage stats, per-user spend | Enhanced with audit logs, billing groups, analytics APIs |
| **Security and compliance** | Standard                                                    | SSO and basic admin controls               | SSO, advanced admin, audit logs, SIEM integration        |
| **Usage notifications**     | User-level alerts                                           | Team and member-level spend alerts         | Enhanced alerts with total spend visibility              |

Sources: Cursor pricing, Team Pricing, Enterprise, Spend Limits, Spend Alerts, API Keys, Models. [14][15][16][17][18][19][20]

### 3.2 Cost Channel Comparison

| Channel or Plan Type                    | How You Pay                                                                                 | How Usage is Limited                                | Cost Predictability per Token               |
| --------------------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------- |
| **OpenAI or Anthropic API directly**    | Per token at published API rates                                                            | API rate limits and vendor budget tools             | High; directly tied to tokens               |
| **ChatGPT or Claude web subscriptions** | Flat per user per month                                                                     | Message caps, session windows, fair use             | Low; effective rate varies                  |
| **Cursor individual plans**             | Flat per user plus included usage dollars                                                   | Included usage caps; optional user spend limits     | Medium; marginal cost is clear              |
| **Cursor Teams (Cursor-metered)**       | 40 USD per user plus 20 USD included usage; overage at API rates plus 0.25 USD per M tokens | Per-user included usage; user and team spend limits | High for overage; included chunk is opaque  |
| **Cursor Teams (BYO API keys)**         | Vendor API bill plus Cursor token fee (0.25 USD per M tokens)                               | Vendor caps and Cursor spend limits                 | High on API side; small markup              |
| **Cursor Enterprise (pooled usage)**    | Custom contract; underlying API prices plus Cursor fee                                      | Org-wide pool plus member and team limits           | High for metered usage; depends on contract |

Sources: OpenAI API pricing, Anthropic docs, Cursor pricing and billing docs. [5][7][13][14][15][16][18][19][20]

---

## 4. Key Takeaways and Practical Recommendations

### 4.1 Direct Answers to Research Questions

| Question                                                                                               | Answer                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Can an existing direct Claude or ChatGPT subscription be used within Cursor via OAuth or similar?**  | No. Web subscriptions and API usage are fully separate for both providers and for Cursor. There is no OAuth or direct integration.                                           |
| **What is the "conversion rate" of dollars to tokens for web subscriptions vs API keys?**              | There is no precise conversion rate. Web subscriptions use message/session limits, not token-based pricing. $1 on an API key does NOT equal $1 of subscription value.        |
| **How does pooled usage work in Enterprise?**                                                          | Enterprise provides a shared organizational usage pool. Heavy users can automatically draw from unused allotments of others within the pool, subject to member-level limits. |
| **Can high-usage users automatically draw from unused allotments of others on Teams?**                 | No. Teams plans have per-seat usage (20 USD per user) that cannot be shared. Heavy users move to on-demand billing even if others have unused capacity.                      |
| **How do usage-limit notifications work on Teams?**                                                    | Spend alerts send email notifications when configured thresholds of on-demand spend are reached at team or member level. Alerts do not block usage.                          |
| **How does an admin top up a specific user on Teams?**                                                 | Teams does not support direct "top-ups" of included usage. Admins can adjust spend limits to allow more on-demand usage, but included usage cannot be transferred.           |
| **Can most employees be on a smaller plan while power users are on higher plans within the same org?** | No. Teams is a flat per-seat rate (40 USD/user). Enterprise terms are contract-specific, but tiered deployment within one account is not standard.                           |
| **Does $20 on Teams provide the same prompts/tokens as $20 on Enterprise?**                            | Yes, at the API pricing level. Both use the same underlying API rates plus Cursor token fees. The difference is pooling (Enterprise) vs. per-seat allocation (Teams).        |

### 4.2 Practical Recommendations

**For Individuals and Small Teams:**

- Use **direct API plus a lightweight client** if you primarily care about predictable token costs and already have strong internal tools. [5][13]
- Use **Cursor Pro or Teams** if the integrated coding experience and tooling outweigh a small markup and some opacity around included usage. [14][15]

**For Larger Organizations:**

- Choose **Cursor Teams** if:
  - Most users have moderate usage and per-seat included usage (20 USD) is sufficient
  - You are comfortable with heavy users moving into on-demand pricing under spend limits
  - You need basic admin controls and centralized billing [15][16]
- Choose **Cursor Enterprise** if:
  - You want a shared usage pool where heavy users can draw on unused capacity
  - You require SSO, audit logs, SIEM integration, billing groups, and fine-grained member limits and alerts
  - You need advanced analytics APIs and compliance features [16][17][18]

**For Budgeting and Governance:**

- Anchor financial models on **vendor API pricing and Cursor's documented token fee** (0.25 USD per million tokens on Teams), not on web subscriptions. [5][12][14][15]
- Treat ChatGPT Plus, ChatGPT Business, Claude Pro, Claude Max, and Cursor's included usage as **convenience bundles with inherently approximate effective per-token cost**. [1][7][8][9]
- For Teams, budget assuming **per-seat usage cannot be pooled** - each user's 20 USD is separate
- For Enterprise, negotiate **pooled usage terms and member limits** in the contract to match your organization's usage patterns

---

## Sources

[1] What is ChatGPT Plus – OpenAI Help Center: https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus  
[2] Billing settings in ChatGPT vs Platform – OpenAI Help Center: https://help.openai.com/en/articles/9039756-billing-settings-in-chatgpt-vs-platform  
[3] ChatGPT Business – Models & Limits – OpenAI Help Center: https://help.openai.com/en/articles/12003714-chatgpt-business-models-limits  
[4] ChatGPT Enterprise and Edu – Models & Limits – OpenAI Help Center: https://help.openai.com/en/articles/11165333-chatgpt-enterprise-and-edu-models-limits  
[5] Pricing – OpenAI API: https://platform.openai.com/docs/pricing  
[6] Best Practices for API Key Safety – OpenAI Help Center: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety  
[7] I subscribe to a paid Claude AI plan – Anthropic Support: https://support.anthropic.com/en/articles/9876003-i-subscribe-to-a-paid-claude-ai-plan-why-do-i-have-to-pay-separately-for-api-usage-on-console  
[8] About Claude's Pro Plan Usage – Anthropic Support: https://support.anthropic.com/en/articles/8324991-about-claude-s-pro-plan-usage  
[9] About Claude's Max Plan Usage – Anthropic Support: https://support.anthropic.com/en/articles/11014257-about-claude-s-max-plan-usage  
[10] About Claude for Work Team and Enterprise Plan Usage – Anthropic Support: https://support.anthropic.com/en/articles/9267304-about-claude-for-work-team-and-enterprise-plan-usage  
[11] Extra Usage for Claude for Work Team and Enterprise Plans – Anthropic Support: https://support.anthropic.com/en/articles/12005970-extra-usage-for-claude-for-work-team-and-enterprise-plans  
[12] Claude Haiku 4.5 – Anthropic: https://www.anthropic.com/news/claude-haiku-4-5  
[13] Getting Started with the API – Anthropic Claude Docs: https://docs.anthropic.com/claude/reference/getting-started-with-the-api  
[14] Pricing – Cursor Docs: https://cursor.com/docs/account/pricing  
[15] Team Pricing – Cursor Docs: https://cursor.com/docs/account/teams/pricing  
[16] Spend Limits – Cursor Docs: https://cursor.com/docs/account/billing/spend-limits  
[17] Spend Alerts – Cursor Docs: https://cursor.com/docs/account/billing/spend-alerts  
[18] Enterprise – Cursor Docs: https://cursor.com/docs/enterprise  
[19] API Keys – Cursor Docs: https://cursor.com/docs/settings/api-keys  
[20] Models – Cursor Docs: https://cursor.com/docs/models  
[21] Team Pricing Clarification – Cursor Forum: https://forum.cursor.com/t/team-pricing-clarification-per-seat-usage-vs-shared-usage-pool/146379
