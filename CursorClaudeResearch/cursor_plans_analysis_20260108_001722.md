# Cursor Subscription and Plan Mechanics

**Generated:** 2026-01-08T00:17:22.488106

## Research Report

# Cursor billing and usage mechanics (as of early 2026)

## 1. Subscription vs API key usage

### 1.1 Use of ChatGPT Plus or Claude Pro inside Cursor

Cursor’s public pricing and documentation describe billing and usage in terms of Cursor subscription plans and optional external API keys, rather than consumer web subscriptions from model providers.[1][4]

### 1.2 Built in provider access vs BYO API keys

Cursor supports two main ways to access model providers:[1][4]

- **Bundled provider access**

  - Included as part of Free, Pro, Team, and Enterprise plans, with plan‑specific AI usage limits described on the pricing page and in documentation, rather than per‑token billing shown to the end user.[1][4]

- **Bring your own API keys (BYO)**
  - Users can add their own OpenAI and Anthropic API keys in Cursor settings.[4]
  - When BYO keys are used, usage is billed by OpenAI or Anthropic under their standard API pricing.[2][3][4]

### 1.3 Differences between bundled usage and BYO keys

- **Limits and metering**

  - Bundled usage is governed by plan‑specific limits shown qualitatively on the pricing page (e.g., higher or lower AI usage by plan), not as public per‑token quotas.[1]
  - BYO API usage is subject to the quotas and pricing set by OpenAI and Anthropic for the configured API keys.[2][3]

- **Models and configuration**
  - Cursor documentation lists support for models from OpenAI and Anthropic, including models such as GPT‑4o and Claude 3.5 Sonnet.[3][4]
  - BYO keys use the model pricing and availability described on the OpenAI and Anthropic pricing pages.[2][3]

### 1.4 Dollar to usage for OpenAI and Anthropic APIs

When using BYO keys, Cursor relays API calls to OpenAI and Anthropic, and the cost is determined by those providers’ standard API pricing.[2][3][4]

Indicative mid‑to‑late‑2024 pricing (per 1 million tokens, USD):[2][3]

| Provider and model          | Input price (USD per 1M tokens) | Output price (USD per 1M tokens) |
| --------------------------- | ------------------------------- | -------------------------------- |
| OpenAI GPT‑4o               | 5                               | 15                               |
| OpenAI GPT‑4o mini          | 0.15                            | 0.60                             |
| Anthropic Claude 3.5 Sonnet | 3                               | 15                               |
| Anthropic Claude 3.5 Haiku  | 0.25                            | 1.25                             |

Approximate per‑exchange cost example (using Claude 3.5 Sonnet at list price):[3]

- 2,000 input tokens and 1,000 output tokens:
  - Input cost ≈ 2,000 × 3 / 1,000,000 = 0.006 USD
  - Output cost ≈ 1,000 × 15 / 1,000,000 = 0.015 USD
  - Total ≈ 0.021 USD per exchange

The same method can be applied to other models in the table using their listed prices.[2][3]

### 1.5 Cursor subscription value vs direct API spend

Cursor’s paid plans (such as Pro, Team, and Enterprise) are sold per seat and described as including AI usage, but the pricing page does not present public per‑token or per‑message dollar equivalents for bundled usage.[1] BYO API usage instead follows the explicit token‑based pricing shown on the OpenAI and Anthropic pricing pages.[2][3]

---

## 2. Cursor plan comparison

### 2.1 Plan overview

Cursor publicly presents four main tiers on the pricing page:[1]

- Free
- Pro
- Team (also referred to as Business in some materials)
- Enterprise

The pricing page describes these tiers with per‑user or seat‑based billing, and indicates that Enterprise pricing is available via contact with sales rather than fixed self‑serve prices.[1]

### 2.2 Included usage and models by plan

Cursor’s pricing page describes relative AI usage differences by plan (for example, indicating more AI usage on higher‑tier plans), but does not list explicit monthly token caps.[1]

- **Free**

  - Described on the pricing page as suitable for trying Cursor, with limited AI usage.[1]

- **Pro**

  - Billed per individual user per month and described as including higher AI usage than Free.[1]

- **Team and Enterprise**
  - Billed centrally for multiple seats and described as including higher or priority AI usage and additional administrative capabilities compared with lower tiers.[1]

Cursor documentation lists supported models from OpenAI and Anthropic, including models such as GPT‑4o and Claude 3.5 Sonnet.[3][4]

### 2.3 Collaboration, security, and support differences

Cursor’s pricing and documentation describe functional differences between Pro, Team, and Enterprise plans:[1][4]

- Team and Enterprise plans include centralized billing and multi‑user collaboration features, in contrast to individually billed Pro.[1][4]
- Enterprise plans are described as including advanced capabilities such as SSO and other enterprise‑oriented security and governance features.[1][4]

---

## 3. Pooled usage and administrative control

### 3.1 Pooled or shared usage on Team and Enterprise

Cursor’s pricing and documentation indicate that Team and Enterprise plans are centrally billed, with organization‑level management of seats and AI usage.[1][4] Public materials do not describe detailed algorithms for how AI usage is pooled or allocated across individual seats.[1][4]

### 3.2 Admin visibility, notifications, and per user control (Team)

For Team‑type plans, Cursor documentation and pricing materials describe admin capabilities beyond Pro, including:[1][4]

- Centralized billing for multiple seats.[1]
- Organization‑level management of members and seats.[1][4]
- In‑product indications of plan limits and usage levels.[1][4]
- The ability for admins to add or remove seats and manage who is in the team workspace.[1][4]

### 3.3 Enterprise specific cost and usage controls

Cursor’s pricing and documentation indicate that Enterprise plans include additional governance and integration features beyond Team, such as SSO and other enterprise‑grade controls.[1][4]

### 3.4 Tiered deployment inside one organization

Public Cursor materials describe organizations and workspaces operating under a given plan (such as Team or Enterprise) with central billing for their seats.[1] The pricing page does not describe combining different plan families (for example, Pro and Team) under a single centralized bill.[1]

---

## 4. Value parity across Cursor plans and direct APIs

### 4.1 Teams vs Enterprise

Cursor’s pricing page emphasizes that Team plans have list pricing suitable for smaller organizations, while Enterprise plans involve contacting sales for custom pricing and add features such as SSO and enhanced governance.[1]

### 4.2 Cursor bundled usage vs direct OpenAI and Anthropic APIs

OpenAI and Anthropic publish token‑based API prices on their public pricing pages.[2][3] Cursor publishes per‑seat prices and qualitative descriptions of included AI usage and features on its pricing page.[1] When BYO keys are used in Cursor, costs follow the provider’s published API pricing.[2][3][4]

---

## 5. Key caveats and open points

- **Pricing and features can change**

  - Cursor’s pricing and documentation pages are the authoritative sources for current plan names, features, and prices and should be consulted at the time of purchase or renewal.[1][4]

- **Currency and taxes**

  - Cursor prices on the pricing page are shown in USD, and notes on taxes or region‑specific considerations, where applicable, appear there.[1]
  - OpenAI and Anthropic pricing pages describe their own pricing and any region‑specific considerations for API usage.[2][3]

- **Undocumented internal mechanics**
  - Public Cursor materials do not document internal details such as exact per‑plan token caps, pooling algorithms, or overage handling for Team and Enterprise.[1][4]

---

### Sources

[1] Cursor Pricing: https://www.cursor.com/pricing  
[2] OpenAI API Pricing: https://openai.com/api/pricing  
[3] Anthropic Claude API Pricing: https://www.anthropic.com/pricing  
[4] Cursor Documentation: https://docs.cursor.com
