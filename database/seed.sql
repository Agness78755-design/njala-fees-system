-- ════════════════════════════════════════════════════════════
-- NJALA UNIVERSITY FEES SYSTEM — SEED DATA
-- Demo data for testing
-- ════════════════════════════════════════════════════════════

-- Note: Passwords should be hashed in production
-- For demo: password123 hashed

-- ── Insert Demo Students ──
INSERT INTO users (student_id, first_name, last_name, email, phone, password_hash, faculty, level, is_active, account_status, created_at)
VALUES 
    ('NJU/2021/0042', 'Mohamed', 'Koroma', 'm.koroma@student.njala.edu.sl', '+232 76 123 456', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmXmIm', 'Faculty of Engineering', 300, true, 'active', NOW()),
    ('NJU/2022/0118', 'Fatmata', 'Sesay', 'f.sesay@student.njala.edu.sl', '+232 76 234 567', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmXmIm', 'Faculty of Agriculture', 200, true, 'active', NOW()),
    ('NJU/2023/0065', 'Ibrahim', 'Kamara', 'i.kamara@student.njala.edu.sl', '+232 76 345 678', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmXmIm', 'Faculty of Science', 100, true, 'active', NOW()),
    ('NJU/2021/0091', 'Mariama', 'Conteh', 'm.conteh@student.njala.edu.sl', '+232 76 456 789', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmXmIm', 'Faculty of Social Sciences', 400, true, 'active', NOW()),
    ('NJU/2022/0207', 'Alpha', 'Bangura', 'a.bangura@student.njala.edu.sl', '+232 76 567 890', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmXmIm', 'Faculty of Engineering', 200, true, 'active', NOW()),
    ('NJU/2023/0142', 'Khadijatu', 'Bangura', 'k.bangura@student.njala.edu.sl', '+232 76 678 901', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmXmIm', 'Faculty of Agriculture', 100, true, 'active', NOW()),
    ('NJU/2024/0085', 'Alhaji', 'Jallow', 'a.jallow@student.njala.edu.sl', '+232 76 789 012', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmXmIm', 'Faculty of Social Sciences', 100, true, 'active', NOW()),
    ('NJU/2021/0156', 'Aminata', 'Sesay', 'a.sesay@student.njala.edu.sl', '+232 76 890 123', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmXmIm', 'Faculty of Science', 300, true, 'active', NOW());

-- ── Insert Demo Admin Users ──
INSERT INTO admin_users (username, email, password_hash, full_name, role, is_active)
VALUES
    ('finance_officer', 'finance@njala.edu.sl', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmXmIm', 'Finance Officer', 'admin', true),
    ('registry_officer', 'registry@njala.edu.sl', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmXmIm', 'Registry Officer', 'staff', true);

-- ── Insert Demo Fees (Academic Year 2024/2025) ──
INSERT INTO fees (student_id, fee_category, amount_due, amount_paid, academic_year, semester, due_date, status, created_at)
VALUES
    -- Student 1: Mohamed Koroma (partially paid)
    (1, 'Tuition Fee', 1500000, 1500000, '2024/2025', 1, '2024-12-15', 'paid', NOW()),
    (1, 'Accommodation', 400000, 400000, '2024/2025', 1, '2024-12-15', 'paid', NOW()),
    (1, 'Lab Fees', 150000, 150000, '2024/2025', 1, '2024-12-15', 'paid', NOW()),
    (1, 'Exam Fees', 100000, 0, '2024/2025', 1, '2025-03-31', 'pending', NOW()),
    (1, 'Student Union', 50000, 0, '2024/2025', 1, '2025-03-31', 'pending', NOW()),
    
    -- Student 2: Fatmata Sesay (fully paid)
    (2, 'Tuition Fee', 1200000, 1200000, '2024/2025', 1, '2024-12-15', 'paid', NOW()),
    (2, 'Accommodation', 300000, 300000, '2024/2025', 1, '2024-12-15', 'paid', NOW()),
    (2, 'Lab Fees', 100000, 100000, '2024/2025', 1, '2024-12-15', 'paid', NOW()),
    
    -- Student 3: Ibrahim Kamara (outstanding)
    (3, 'Tuition Fee', 1400000, 700000, '2024/2025', 1, '2024-12-15', 'partial', NOW()),
    (3, 'Accommodation', 350000, 0, '2024/2025', 1, '2024-12-15', 'pending', NOW()),
    (3, 'Lab Fees', 120000, 0, '2024/2025', 1, '2024-12-15', 'pending', NOW()),
    
    -- Student 4: Mariama Conteh (fully paid)
    (4, 'Tuition Fee', 1100000, 1100000, '2024/2025', 1, '2024-12-15', 'paid', NOW()),
    (4, 'Accommodation', 250000, 250000, '2024/2025', 1, '2024-12-15', 'paid', NOW()),
    
    -- Student 5: Alpha Bangura (partially paid)
    (5, 'Tuition Fee', 1500000, 1500000, '2024/2025', 1, '2024-12-15', 'paid', NOW()),
    (5, 'Accommodation', 400000, 200000, '2024/2025', 1, '2024-12-15', 'partial', NOW()),
    (5, 'Lab Fees', 150000, 0, '2024/2025', 1, '2024-12-15', 'pending', NOW());

-- ── Insert Demo Payments ──
INSERT INTO payments (student_id, transaction_id, reference_number, amount, payment_method, phone_number, status, processed_at, created_at)
VALUES
    ('1', '9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d', 'TXN-20240910-A1B2C3', 1500000, 'orange_money', '+232 76 123 456', 'completed', '2024-09-10 14:30:00', '2024-09-10 14:15:00'),
    ('1', 'b2c3d4e5-6f7a-8b9c-0d1e-2f3a4b5c6d7e', 'TXN-20240905-D4E5F6', 400000, 'orange_money', '+232 76 123 456', 'completed', '2024-09-05 10:45:00', '2024-09-05 10:30:00'),
    ('1', 'c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f', 'TXN-20240901-G7H8I9', 150000, 'orange_money', '+232 76 123 456', 'completed', '2024-09-01 09:15:00', '2024-09-01 09:00:00'),
    
    ('2', 'd4e5f6a7-8b9c-0d1e-2f3a-4b5c6d7e8f9a', 'TXN-20240915-J0K1L2', 1200000, 'africell_money', '+232 76 234 567', 'completed', '2024-09-15 11:30:00', '2024-09-15 11:15:00'),
    ('2', 'e5f6a7b8-9c0d-1e2f-3a4b-5c6d7e8f9a0b', 'TXN-20240910-M3N4O5', 400000, 'bank_transfer', NULL, 'completed', '2024-09-10 16:00:00', '2024-09-10 15:45:00'),
    
    ('3', 'f6a7b8c9-0d1e-2f3a-4b5c-6d7e8f9a0b1c', 'TXN-20240908-P6Q7R8', 700000, 'orange_money', '+232 76 345 678', 'completed', '2024-09-08 13:20:00', '2024-09-08 13:05:00'),
    
    ('4', 'a7b8c9d0-1e2f-3a4b-5c6d-7e8f9a0b1c2d', 'TXN-20240912-S9T0U1', 1100000, 'africell_money', '+232 76 456 789', 'completed', '2024-09-12 10:10:00', '2024-09-12 09:55:00'),
    ('4', 'b8c9d0e1-2f3a-4b5c-6d7e-8f9a0b1c2d3e', 'TXN-20240907-V2W3X4', 250000, 'orange_money', '+232 76 456 789', 'completed', '2024-09-07 15:30:00', '2024-09-07 15:15:00'),
    
    ('5', 'c9d0e1f2-3a4b-5c6d-7e8f-9a0b1c2d3e4f', 'TXN-20240911-Y5Z6A7', 1500000, 'bank_transfer', NULL, 'completed', '2024-09-11 14:45:00', '2024-09-11 14:30:00'),
    ('5', 'd0e1f2a3-4b5c-6d7e-8f9a-0b1c2d3e4f5g', 'TXN-20240906-B8C9D0', 200000, 'orange_money', '+232 76 567 890', 'completed', '2024-09-06 12:15:00', '2024-09-06 12:00:00');

-- ── Insert Audit Log Sample ──
INSERT INTO audit_logs (user_id, action, entity_type, entity_id, ip_address, created_at)
VALUES
    (1, 'login', 'user', 1, '192.168.1.100', NOW() - INTERVAL '2 hours'),
    (1, 'view_fees', 'fees', 1, '192.168.1.100', NOW() - INTERVAL '1 hours'),
    (1, 'initiate_payment', 'payment', 1, '192.168.1.100', NOW() - INTERVAL '30 minutes');
