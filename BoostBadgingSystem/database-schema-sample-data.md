# Boost Badging System – Sample Data

Illustrative values for every column in the schema.

## `users`
| Column | Sample |
| --- | --- |
| `id` | `8f7c7d9b-1c0d-49f1-a29c-03d0c4c2c111` |
| `full_name` | `Alice Carter` |
| `email` | `alice@example.com` |
| `wallet_address` | `0x32ffw32....3f2` |
| `created_at` | `2025-02-01T10:12:55Z` |
| `updated_at` | `2025-02-10T08:00:00Z` |


## `badge_categories`
| Column | Sample |
| --- | --- |
| `id` | `2fcb0271-6316-4c45-9375-8fca4c98840c` |
| `name` | `Contribution Badges` |
| `description` | `GitHub activity milestones` |
| `created_at` | `2025-02-01T09:00:00Z` |

## `badges`
| Column | Sample |
| --- | --- |
| `id` | `0b1222b9-fd3f-4c4c-8e20-04a0670a74c2` |
| `category_id` | `2fcb0271-6316-4c45-9375-8fca4c98840c` |
| `name` | `SolDev Mentor` |
| `description` | `Mentored five Solana-focused Boost contributors` |
| `image` | `image data (this field may be blob, so the image data can be saved in database.)` |
| `badge_type` | `1 (database-only:0, blockchain:1)` |
| `contract_token_id` | `0 (database-only:null, blockchain:token_id)` |
| `metadata_uri` | `ipfs://Qm...abc/23fwefsdcwcf.json` |
| `created_at` | `2025-02-03T12:05:10Z` |

## `badge_issuances`
| Column | Sample |
| --- | --- |
| `id` | `3bf34c2a-3bb0-47cb-9336-6a9c8f4ecb5a` |
| `badge_id` | `0b1222b9-fd3f-4c4c-8e20-04a0670a74c2` |
| `user_id` | `8f7c7d9b-1c0d-49f1-a29c-03d0c4c2c111` |
| `metadata_uri` | `ipfs://Qm...abc/sw323edwswef42.json (this value is for only this issuance and updated from IPFS after issuance)` |
| `status` | `0 (pending:0, issued:1, claimed:2 (If the badge is based on database-only, then can have only 0 or 2 because of 'issued' means 'claimed'.)` |
| `wallet_address` | `0x32ffw32....3f2` |
| `issued_by` | `4783355a-4095-4fe8-a601-7d61d272af24` |
| `created_at` | `2025-02-05T16:20:00Z` |
| `updated_at` | `2025-02-05T16:20:00Z` |


## `badge_notifications`
| Column | Sample |
| --- | --- |
| `id` | `a8bcb904-6de7-4c49-96f9-9b0c165f08f1` |
| `issuance_id` | `3bf34c2a-3bb0-47cb-9336-6a9c8f4ecb5a` |
| `is_read` | `false` |
| `appeared_at` | `2025-02-05T16:25:00Z` |

## `claim_intents`
| Column | Sample |
| --- | --- |
| `id` | `6d42dc09-1a7f-4cd5-8f24-71e2fc7df7c8` |
| `issuance_id` | `3bf34c2a-3bb0-47cb-9336-6a9c8f4ecb5a` |
| `status` | `0(pending:0, transfered:1)` |
| `wallet_address` | `0x32ffw32....3f2` |
| `submitted_at` | `2025-02-06T09:30:00Z` |
| `admin_response_at` | `null` |

## `badge_logs`
| Column | Sample |
| --- | --- |
| `id` | `3232ff1-f23f-32f23-23f2f-23f23f23f23` |
| `action_type` | `0 (badge_created:0, badge_category_created:1, badge_issued:2, badge_claimed:3, wallet_updated:4, badge_issued:5, badge_claimed:6)` |
| `entity_type` | `issuance (badge, badge_category, issuance, user, claim_intent)` |
| `badge_id` | `0b1222b9-fd3f-4c4c-8e20-04a0670a74c2 (nullable, for badge-related operations)` |
| `category_id` | `2fcb0271-6316-4c45-9375-8fca4c98840c (nullable, for category-related operations)` |
| `issuance_id` | `3bf34c2a-3bb0-47cb-9336-6a9c8f4ecb5a (nullable, for issuance-related operations)` |
| `user_id` | `8f7c7d9b-1c0d-49f1-a29c-03d0c4c2c111 (nullable, for user-related operations)` |
| `claim_id` | `6d42dc09-1a7f-4cd5-8f24-71e2fc7df7c8 (nullable, for claim-related operations)` |
| `performed_by` | `4783355a-4095-4fe8-a601-7d61d272af24 (admin/user who performed the action)` |
| `blockchain_tx_signature` | `5HgZQ...sd8 (nullable, only for blockchain operations)` |
| `wallet_address` | `0xef23rg23f...f23f (nullable, for wallet-related operations)` |
| `old_value` | `null (or previous value for updates, e.g., old wallet address)` |
| `new_value` | `null (or new value for updates, e.g., new wallet address)` |
| `status` | `0 (success:0, failed:1, pending:2)` |
| `error_message` | `null (or error details if status is failed)` |
| `created_at` | `2025-02-05T16:21:00Z` |


## `email_logs`
| Column | Sample |
| --- | --- |
| `id` | `ddf95ffa-3236-4413-be0a-09964fa7150d` |
| `issuance_id` | `3bf34c2a-3bb0-47cb-9336-6a9c8f4ecb5a` |
| `notification_type` | `0 (badging is issued and claimed(means that is sent to your wallet in case of blockchain-based badging, in other case only issued) : 0, only issued (in case of only blockchain-based badging) : 1`) |
| `mail_provider_id` | `mailman-msg-49811` |
| `status` | `sent` |
| `metadata` | `{"template":"contract-claim","attempt":1}` |
| `created_at` | `2025-02-05T16:26:00Z` |

