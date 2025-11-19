-- Boost Badging System - Database Schema
-- Generated from database-schema-sample-data.md

-- Enable UUID extension (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    wallet_address VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_wallet_address ON users(wallet_address) WHERE wallet_address IS NOT NULL;

-- ============================================================================
-- BADGE CATEGORIES TABLE
-- ============================================================================
CREATE TABLE badge_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_badge_categories_name ON badge_categories(name);

-- ============================================================================
-- BADGES TABLE
-- ============================================================================
CREATE TABLE badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL REFERENCES badge_categories(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    image BYTEA, -- Blob for image data
    badge_type INTEGER NOT NULL DEFAULT 0, -- 0: database-only, 1: blockchain
    contract_token_id INTEGER, -- Token ID for blockchain badges (null for database-only)
    metadata_uri TEXT, -- IPFS URI for badge metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_badges_category_id ON badges(category_id);
CREATE INDEX idx_badges_badge_type ON badges(badge_type);
CREATE INDEX idx_badges_name ON badges(name);
CREATE INDEX idx_badges_contract_token_id ON badges(contract_token_id) WHERE contract_token_id IS NOT NULL;
CREATE INDEX idx_badges_metadata_uri ON badges(metadata_uri) WHERE metadata_uri IS NOT NULL;

-- ============================================================================
-- BADGE ISSUANCES TABLE
-- ============================================================================
CREATE TABLE badge_issuances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    badge_id UUID NOT NULL REFERENCES badges(id) ON DELETE RESTRICT,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    metadata_uri TEXT NOT NULL, -- IPFS URI
    status INTEGER NOT NULL DEFAULT 0, -- 0: pending, 1: issued, 2: claimed
    wallet_address VARCHAR(255), -- Wallet address for this specific issuance
    issued_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT, -- Admin who issued
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_badge_issuances_badge_id ON badge_issuances(badge_id);
CREATE INDEX idx_badge_issuances_user_id ON badge_issuances(user_id);
CREATE INDEX idx_badge_issuances_issued_by ON badge_issuances(issued_by);
CREATE INDEX idx_badge_issuances_status ON badge_issuances(status);
CREATE INDEX idx_badge_issuances_metadata_uri ON badge_issuances(metadata_uri);
CREATE INDEX idx_badge_issuances_wallet_address ON badge_issuances(wallet_address) WHERE wallet_address IS NOT NULL;

-- ============================================================================
-- BADGE NOTIFICATIONS TABLE
-- ============================================================================
CREATE TABLE badge_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    issuance_id UUID NOT NULL REFERENCES badge_issuances(id) ON DELETE CASCADE,
    is_read BOOLEAN NOT NULL DEFAULT false,
    appeared_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_badge_notifications_issuance_id ON badge_notifications(issuance_id);
CREATE INDEX idx_badge_notifications_is_read ON badge_notifications(is_read);
CREATE INDEX idx_badge_notifications_appeared_at ON badge_notifications(appeared_at);

-- ============================================================================
-- CLAIM INTENTS TABLE
-- ============================================================================
CREATE TABLE claim_intents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    issuance_id UUID NOT NULL REFERENCES badge_issuances(id) ON DELETE RESTRICT,
    status INTEGER NOT NULL DEFAULT 0, -- 0: pending, 1: transferred
    wallet_address VARCHAR(255) NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    admin_response_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_claim_intents_issuance_id ON claim_intents(issuance_id);
CREATE INDEX idx_claim_intents_status ON claim_intents(status);
CREATE INDEX idx_claim_intents_wallet_address ON claim_intents(wallet_address);
CREATE INDEX idx_claim_intents_submitted_at ON claim_intents(submitted_at);

-- ============================================================================
-- BADGE LOGS TABLE
-- ============================================================================
CREATE TABLE badge_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_type INTEGER NOT NULL, -- 0: badge_created, 1: badge_category_created, 2: badge_issued, 3: badge_claimed, 4: wallet_updated, 5: badge_issued, 6: badge_claimed
    entity_type VARCHAR(50) NOT NULL, -- badge, badge_category, issuance, user, claim_intent
    badge_id UUID REFERENCES badges(id) ON DELETE SET NULL,
    category_id UUID REFERENCES badge_categories(id) ON DELETE SET NULL,
    issuance_id UUID REFERENCES badge_issuances(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    claim_id UUID REFERENCES claim_intents(id) ON DELETE SET NULL,
    performed_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    blockchain_tx_signature VARCHAR(255), -- Solana transaction signature
    wallet_address VARCHAR(255),
    old_value TEXT, -- Previous value for updates (e.g., old wallet address)
    new_value TEXT, -- New value for updates (e.g., new wallet address)
    status INTEGER NOT NULL DEFAULT 0, -- 0: success, 1: failed, 2: pending
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_badge_logs_action_type ON badge_logs(action_type);
CREATE INDEX idx_badge_logs_entity_type ON badge_logs(entity_type);
CREATE INDEX idx_badge_logs_badge_id ON badge_logs(badge_id) WHERE badge_id IS NOT NULL;
CREATE INDEX idx_badge_logs_category_id ON badge_logs(category_id) WHERE category_id IS NOT NULL;
CREATE INDEX idx_badge_logs_issuance_id ON badge_logs(issuance_id) WHERE issuance_id IS NOT NULL;
CREATE INDEX idx_badge_logs_user_id ON badge_logs(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_badge_logs_claim_id ON badge_logs(claim_id) WHERE claim_id IS NOT NULL;
CREATE INDEX idx_badge_logs_performed_by ON badge_logs(performed_by);
CREATE INDEX idx_badge_logs_blockchain_tx_signature ON badge_logs(blockchain_tx_signature) WHERE blockchain_tx_signature IS NOT NULL;
CREATE INDEX idx_badge_logs_status ON badge_logs(status);
CREATE INDEX idx_badge_logs_created_at ON badge_logs(created_at);

-- ============================================================================
-- EMAIL LOGS TABLE
-- ============================================================================
CREATE TABLE email_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    issuance_id UUID NOT NULL REFERENCES badge_issuances(id) ON DELETE CASCADE,
    notification_type INTEGER NOT NULL, -- 0: issued and claimed, 1: only issued
    mail_provider_id VARCHAR(255) NOT NULL, -- Mailman 3 message ID
    status VARCHAR(50) NOT NULL, -- sent, failed, pending, bounced
    metadata JSONB, -- Additional metadata (template, attempt, etc.)
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email_logs_issuance_id ON email_logs(issuance_id);
CREATE INDEX idx_email_logs_notification_type ON email_logs(notification_type);
CREATE INDEX idx_email_logs_mail_provider_id ON email_logs(mail_provider_id);
CREATE INDEX idx_email_logs_status ON email_logs(status);
CREATE INDEX idx_email_logs_created_at ON email_logs(created_at);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_badge_issuances_updated_at BEFORE UPDATE ON badge_issuances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS
-- ============================================================================
COMMENT ON TABLE users IS 'System users with email and optional wallet addresses';
COMMENT ON TABLE badge_categories IS 'Categories for organizing badges';
COMMENT ON TABLE badges IS 'Badge definitions with metadata and type (database-only or blockchain)';
COMMENT ON TABLE badge_issuances IS 'Individual badge issuances to users with IPFS metadata';
COMMENT ON TABLE badge_notifications IS 'In-app notifications for badge issuances';
COMMENT ON TABLE claim_intents IS 'User requests to claim badges from contract vault';
COMMENT ON TABLE badge_logs IS 'Comprehensive audit log for all badge system operations';
COMMENT ON TABLE email_logs IS 'Email delivery logs for badge notifications';

COMMENT ON COLUMN badges.badge_type IS '0: database-only, 1: blockchain';
COMMENT ON COLUMN badges.contract_token_id IS 'Token ID for blockchain badges (null for database-only badges)';
COMMENT ON COLUMN badges.metadata_uri IS 'IPFS URI for badge metadata';
COMMENT ON COLUMN badge_issuances.status IS '0: pending, 1: issued, 2: claimed (database-only badges can only be 0 or 2)';
COMMENT ON COLUMN claim_intents.status IS '0: pending, 1: transferred';
COMMENT ON COLUMN badge_logs.action_type IS '0: badge_created, 1: badge_category_created, 2: badge_issued, 3: badge_claimed, 4: wallet_updated, 5: badge_issued, 6: badge_claimed';
COMMENT ON COLUMN badge_logs.status IS '0: success, 1: failed, 2: pending';
COMMENT ON COLUMN email_logs.notification_type IS '0: issued and claimed, 1: only issued';

