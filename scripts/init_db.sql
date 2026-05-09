-- ChaloGhumo Sprint 4: Postgres Schema Initialization
-- Optimized for Relational Pruning and Geographic Lookups

-- Enable PostGIS if required for geographic search (optional, but recommended)
-- CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS destinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    iata_code VARCHAR(3) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    
    -- Relational Pruning Attributes
    budget_level VARCHAR(20) CHECK (budget_level IN ('Budget', 'Mid-range', 'Luxury', 'Ultra-Luxury')),
    safety_index FLOAT DEFAULT 1.0,
    climate_type VARCHAR(50),
    
    -- Geographical Data
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    
    -- Metadata
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices for High-Speed Pruning
CREATE INDEX IF NOT EXISTS idx_destinations_budget ON destinations(budget_level);
CREATE INDEX IF NOT EXISTS idx_destinations_safety ON destinations(safety_index);
CREATE INDEX IF NOT EXISTS idx_destinations_climate ON destinations(climate_type);
CREATE INDEX IF NOT EXISTS idx_destinations_iata ON destinations(iata_code);

-- GIN Index for fast tag searching
CREATE INDEX IF NOT EXISTS idx_destinations_tags ON destinations USING GIN (tags);

-- Function for updated_at refresh
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_destinations_updated_at
    BEFORE UPDATE ON destinations
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();
