DROP DATABASE IF EXISTS smart_club;
CREATE DATABASE smart_club;
USE smart_club;

CREATE TABLE members (
    id_member INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events (
    id_event INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    date_event DATETIME NOT NULL,
    price DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attendance (
    id_member INT,
    id_event INT,
    status ENUM('present', 'absent') DEFAULT 'present',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_member, id_event),
    FOREIGN KEY (id_member) REFERENCES members(id_member) ON DELETE CASCADE,
    FOREIGN KEY (id_event) REFERENCES events(id_event) ON DELETE CASCADE
);

CREATE TABLE payments (
    id_payment INT AUTO_INCREMENT PRIMARY KEY,
    id_member INT,
    id_event INT,
    amount DECIMAL(10, 2) NOT NULL,
    date_payment DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50),
    FOREIGN KEY (id_member) REFERENCES members(id_member) ON DELETE SET NULL,
    FOREIGN KEY (id_event) REFERENCES events(id_event) ON DELETE SET NULL
);
