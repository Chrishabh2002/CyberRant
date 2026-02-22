-- Rant AI Community Intelligence & Trending Analytics Schema
-- Optimized for PostgreSQL

-- 1. Watermark management for n8n incremental processing
CREATE TABLE IF NOT EXISTS analytics_state (
    key VARCHAR(50) PRIMARY KEY,
    last_processed_id BIGINT DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Initialize watermark if not exists
INSERT INTO analytics_state (key, last_processed_id) 
VALUES ('post_watermark', 0)
ON CONFLICT (key) DO NOTHING;

-- 2. Source table for community posts (if not already existing)
CREATE TABLE IF NOT EXISTS user_posts (
    id SERIAL PRIMARY KEY,
    author_name VARCHAR(255),
    content TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    sentiment_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Primary Intelligence Table for Cluster Results
CREATE TABLE IF NOT EXISTS community_intel (
    topic_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_name VARCHAR(255) UNIQUE,
    category VARCHAR(50), -- e.g., 'Vulnerability', 'Phishing', 'Malware'
    summary TEXT,
    risk_level VARCHAR(20) DEFAULT 'LOW', -- LOW, MEDIUM, HIGH, CRITICAL
    trend_score INTEGER DEFAULT 0, -- 0 to 100
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB, -- { "tags": [], "affected_platforms": [] }
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Time-Series History for Velocity Calculation & Dashboard Graphs
CREATE TABLE IF NOT EXISTS trend_history (
    id SERIAL PRIMARY KEY,
    topic_id UUID REFERENCES community_intel(topic_id),
    engagement_score DECIMAL(10,2),
    velocity_score DECIMAL(10,2),
    snapshot_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Indices for Production Performance
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON user_posts(created_at);
CREATE INDEX IF NOT EXISTS idx_intel_risk_level ON community_intel(risk_level);
CREATE INDEX IF NOT EXISTS idx_trend_history_snapshot ON trend_history(snapshot_time);
CREATE INDEX IF NOT EXISTS idx_intel_trend_score ON community_intel(trend_score DESC);
