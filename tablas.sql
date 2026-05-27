CREATE DATABASE IF NOT EXISTS restaurante_db;
USE restaurante_db;

CREATE TABLE IF NOT EXISTS menu (
    id_plato INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    vegetariano BOOLEAN DEFAULT FALSE,
    vegano BOOLEAN DEFAULT FALSE,
    sin_tacc BOOLEAN DEFAULT FALSE,
    sin_lactosa BOOLEAN DEFAULT FALSE,
    categoria VARCHAR(20) NOT NULL,
    imagen_url VARCHAR(255),
    CHECK (categoria IN ('bebida', 'entrada', 'postre', 'plato_principal'))
);
