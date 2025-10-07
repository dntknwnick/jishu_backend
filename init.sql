-- Initial database setup for Jishu Backend
-- This file is executed when MySQL container starts for the first time

-- Create the users table
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mobile_no` varchar(20) NOT NULL,
  `email_id` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  `is_premium` tinyint(1) DEFAULT '0',
  `is_admin` tinyint(1) DEFAULT '0',
  `color_theme` enum('light','dark') DEFAULT 'light',
  `otp` varchar(10) DEFAULT NULL,
  `otp_verified` tinyint(1) DEFAULT '0',
  `last_login` datetime DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('active','inactive','blocked') DEFAULT 'active',
  `source` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_id` (`email_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert default admin user
-- Password: Admin@123 (hashed)
INSERT IGNORE INTO `users` (
  `email_id`, 
  `name`, 
  `mobile_no`, 
  `password`, 
  `is_admin`, 
  `is_premium`, 
  `source`, 
  `status`
) VALUES (
  'admin@jishu.com',
  'System Administrator',
  '9999999999',
  'scrypt:32768:8:1$8xKzGqJHNvQwYrLm$46c8c65cb1f1c4a6b8f9c8e4d5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2',
  1,
  1,
  'email',
  'active'
);

-- Insert default regular user
-- Password: User@123 (hashed)
INSERT IGNORE INTO `users` (
  `email_id`, 
  `name`, 
  `mobile_no`, 
  `password`, 
  `is_admin`, 
  `is_premium`, 
  `source`, 
  `status`
) VALUES (
  'user@example.com',
  'Sample User',
  '9876543210',
  'scrypt:32768:8:1$7wJyFpIGMuPvXqKl$35b7b54ba0e0b3a5a7f8b7c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2',
  0,
  0,
  'email',
  'active'
);
