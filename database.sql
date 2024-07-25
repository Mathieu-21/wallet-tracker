CREATE DATABASE IF NOT EXISTS wallet_tracker;

USE wallet_tracker;

CREATE TABLE IF NOT EXISTS referentielfonds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
);

CREATE TABLE IF NOT EXISTS referentielinstruments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) -- Savoir si c'est une action, obligation, titre d'état
);

CREATE TABLE IF NOT EXISTS positions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fund_id INT,
    instrument_id INT,
    weight DECIMAL(5, 2),
    FOREIGN KEY (fund_id) REFERENCES referentielfonds(id),
    FOREIGN KEY (instrument_id) REFERENCES referentielinstruments(id)
);

-- INSERTION DES DONNÉES

INSERT INTO referentielfonds (name, description) VALUES 
('Fonds Croissance'),
('Fonds Income'),
('Fonds Équilibré');


INSERT INTO referentielinstruments (name, type) VALUES 
('Apple Inc.', 'Action'),
('TotalEnergies', 'Action'),
('Obligation d`État France', 'Obligation');


INSERT INTO positions (fund_id, instrument_id, weight) VALUES 
(1, 1, 40.00),
(1, 2, 20.00),
(2, 3, 50.00),
(2, 2, 30.00),
(3, 1, 30.00),
(3, 2, 20.00),
(3, 3, 20.00);
