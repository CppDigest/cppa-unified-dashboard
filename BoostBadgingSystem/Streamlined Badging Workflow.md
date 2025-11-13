# Boost Badging System – Streamlined Workflow Plan

## Overview

Refined Solana-based badging flow that mints directly to recipient wallets or a vaulted holding account, supports email-triggered claims, and records all badge lifecycle events. The implementation window is capped at three weeks.

---

## End-to-End Workflow

1. **Preparation**  
   - Frontend retrieves token catalogue and recipient roster.  
   - Minter selects badge set (single or batch) and recipients.

2. **Metadata & Persistence**  
   - Frontend submits badge issuance payload to the IPFS service.  
   - IPFS returns content URI plus derived metadata (hash, gateway URL).  
   - Application persists issuance record in the database, including user data, payload hash, claim eligibility flags, and URI references.

3. **Minting**  
   - Minter wallet (e.g., MetaMask) signs mint or batch mint transaction supplying recipient wallet (or vault address), token IDs, and metadata URI.  
   - Solana program validates call, mints tokens, and routes them either to user wallets or the vault account.

4. **Notification**  
   - Post-confirmation hook (webhook or listener) enqueues email template jobs.  
   - Mailing list service delivers:  
     - **Direct wallet recipients** – badge details and blockchain links.  
     - **Vault recipients** – claim instructions, emphasizing security posture.

5. **Claim (Vaulted Tokens Only)**  
   - User initiates claim via claim portal link. System looks up issuance by URI and extracts the registered email.  
   - Service issues a one-time verification code via email and enforces rate limits.  
   - User submits verification code. On success, the UI prompts for a self-custodied public address.  
   - Vault admin signer service (HSM or custodial wallet) dispatches a transfer transaction to the provided address.  
   - System updates database with claim completion timestamp, destination wallet, and transaction signature.  
   - Confirmation email is sent to the claimant.

6. **Auditing & Reporting**  
   - Dashboard surfaces mint/claim status, IPFS hashes, and notification delivery logs.  
   - Scheduled jobs reconcile on-chain state with database records.

---


