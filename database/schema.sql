-- ════════════════════════════════════════════════════════════
-- NJALA UNIVERSITY FEES MANAGEMENT SYSTEM — DATABASE SCHEMA
-- PostgreSQL Database
-- ════════════════════════════════════════════════════════════

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS njala_fees;

-- Use the database
\c njala_fees;

-- ── Users Table (Students) ──
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    
    -- Student Info
    faculty VARCHAR(100),
    level INTEGER DEFAULT 100,
    
    -- Account Status
    is_active BOOLEAN DEFAULT true,
    account_status VARCHAR(20) DEFAULT 'active',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    INDEX idx_student_id (student_id),
    INDEX idx_email (email),
    INDEX idx_faculty (faculty)
);

-- ── Admin Users Table ──
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'staff',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- ── Fees Table ──
CREATE TABLE IF NOT EXISTS fees (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Fee Details
    fee_category VARCHAR(100) NOT NULL,
    amount_due NUMERIC(15, 2) NOT NULL,
    amount_paid NUMERIC(15, 2) DEFAULT 0,
    
    -- Dates
    academic_year VARCHAR(9) NOT NULL,
    semester INTEGER NOT NULL,
    due_date TIMESTAMP NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_student_id (student_id),
    INDEX idx_academic_year (academic_year),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date)
);

-- ── Payments Table ──
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Transaction Details
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    reference_number VARCHAR(50) UNIQUE NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    
    -- Payment Method
    payment_method VARCHAR(20) NOT NULL,
    phone_number VARCHAR(20),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    
    -- Reconciliation
    reconciled BOOLEAN DEFAULT false,
    reconciled_by VARCHAR(100),
    reconciled_at TIMESTAMP,
    
    -- Receipt
    receipt_url VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    notes TEXT,
    
    INDEX idx_student_id (student_id),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_reference_number (reference_number),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_payment_method (payment_method)
);

-- ── Audit Log Table ──
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_action (action)
);

-- ── SMS Notifications Table ──
CREATE TABLE IF NOT EXISTS sms_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    phone_number VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'sent',
    message_sid VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- ── Email Notifications Table ──
CREATE TABLE IF NOT EXISTS email_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    recipient_email VARCHAR(120) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    message_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'sent',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- ── Session Table (for session management) ──
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
);

-- Create indexes for better query performance
CREATE INDEX idx_fees_student_academic ON fees(student_id, academic_year);
CREATE INDEX idx_payments_student_status ON payments(student_id, status);
CREATE INDEX idx_fees_amount_outstanding ON fees((amount_due - amount_paid));

-- ════════════════════════════════════════════════════════════
-- VIEWS FOR REPORTING
-- ════════════════════════════════════════════════════════════

-- Student Summary View
CREATE OR REPLACE VIEW student_summary AS
SELECT 
    u.id,
    u.student_id,
    CONCAT(u.first_name, ' ', u.last_name) as full_name,
    u.faculty,
    u.level,
    COALESCE(SUM(f.amount_due), 0) as total_fees,
    COALESCE(SUM(f.amount_paid), 0) as total_paid,
    COALESCE(SUM(f.amount_due - f.amount_paid), 0) as outstanding,
    COUNT(DISTINCT f.id) as fee_count
FROM users u
LEFT JOIN fees f ON u.id = f.student_id
WHERE u.is_active = true
GROUP BY u.id, u.student_id, u.first_name, u.last_name, u.faculty, u.level;

-- Payment Summary View
CREATE OR REPLACE VIEW payment_summary AS
SELECT 
    DATE_TRUNC('month', p.created_at) as month,
    p.payment_method,
    COUNT(*) as transaction_count,
    SUM(p.amount) as total_amount,
    COUNT(CASE WHEN p.status = 'completed' THEN 1 END) as completed_count,
    COUNT(CASE WHEN p.status = 'failed' THEN 1 END) as failed_count
FROM payments p
GROUP BY DATE_TRUNC('month', p.created_at), p.payment_method;

-- Faculty Collection View
CREATE OR REPLACE VIEW faculty_collection AS
SELECT 
    u.faculty,
    COUNT(DISTINCT u.id) as student_count,
    COALESCE(SUM(f.amount_due), 0) as total_fees,
    COALESCE(SUM(f.amount_paid), 0) as total_collected,
    COALESCE(SUM(f.amount_due - f.amount_paid), 0) as outstanding,
    ROUND(COALESCE(SUM(f.amount_paid) * 100.0 / NULLIF(SUM(f.amount_due), 0), 0), 2) as collection_percentage
FROM users u
LEFT JOIN fees f ON u.id = f.student_id
WHERE u.is_active = true
GROUP BY u.faculty;
