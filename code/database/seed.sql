USE smart_club;

INSERT INTO members (full_name, email, class_name) VALUES 
('Alice Johnson', 'alice@example.com', '10A'),
('Bob Smith', 'bob@example.com', '10B'),
('Charlie Brown', 'charlie@example.com', '11A');

INSERT INTO events (title, description, date_event, price) VALUES 
('Welcome Party', 'Opening ceremony for the club', '2024-09-01 14:00:00', 5.00),
('Coding Workshop', 'Learn Python basics', '2024-09-15 10:00:00', 0.00),
('Pizza Night', 'Social gathering', '2024-10-01 18:00:00', 10.00);

INSERT INTO attendance (id_member, id_event, status) VALUES 
(1, 1, 'present'),
(2, 1, 'present'),
(3, 1, 'absent'),
(1, 2, 'present');

INSERT INTO payments (id_member, id_event, amount, payment_method) VALUES 
(1, 1, 5.00, 'Cash'),
(2, 1, 5.00, 'Cash'),
(1, 3, 10.00, 'Card');
