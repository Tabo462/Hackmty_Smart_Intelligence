-- Snowflake Tables Creation Script
-- Run this in your Snowflake environment

-- Products table
CREATE TABLE IF NOT EXISTS products (
  barcode VARCHAR PRIMARY KEY,
  product_id VARCHAR,
  name VARCHAR
);

-- Batches table
CREATE TABLE IF NOT EXISTS batches (
  id INTEGER AUTOINCREMENT PRIMARY KEY,
  barcode VARCHAR,
  product_id VARCHAR,
  lot_number VARCHAR,
  quantity INTEGER,
  expiration_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
