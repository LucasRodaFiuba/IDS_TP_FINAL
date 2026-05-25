CREATE DATABASE IF NOT EXISTS restaurante_db;
USE restaurante_db;

-- =========================
-- ROLES
-- =========================

CREATE TABLE roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO roles (nombre)
VALUES
('admin'),
('cliente');


CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    telefono VARCHAR(30),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_rol INT NOT NULL,

    FOREIGN KEY (id_rol)
    REFERENCES roles(id_rol)
);


CREATE TABLE mesas (
    numero_mesa INT AUTO_INCREMENT PRIMARY KEY,
    capacidad INT NOT NULL,
    ubicacion VARCHAR(100),
    disponible BOOLEAN DEFAULT TRUE
);


CREATE TABLE reservas (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    numero_mesa INT NOT NULL,
    fecha_reserva DATE NOT NULL,
    hora_reserva TIME NOT NULL,
    cantidad_personas INT NOT NULL,
    
    estado ENUM(
        'pendiente',
        'confirmada',
        'cancelada',
        'finalizada'
    ) DEFAULT 'pendiente',

    codigo_qr VARCHAR(255),
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario)
    REFERENCES usuarios(id_usuario),

    FOREIGN KEY (numero_mesa)
    REFERENCES mesas(numero_mesa)
);


CREATE TABLE categorias_menu (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE menu (
    id_plato INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
   precio DECIMAL(10,2) NOT NULL,
    vegetariano BOOLEAN DEFAULT FALSE,
    vegano BOOLEAN DEFAULT FALSE,
    sin_tacc BOOLEAN DEFAULT FALSE,
    sin_lactosa BOOLEAN DEFAULT FALSE,
    imagen VARCHAR(255),
    categoria VARCHAR(20)  NOT NULL CHECK (categoria IN ('bebida', 'entrada', 'postre', 'plato_principal'))
);


CREATE TABLE resenas (
    id_resena INT AUTO_INCREMENT PRIMARY KEY,

    id_usuario INT NOT NULL,
    id_reserva INT NOT NULL,

    puntuacion INT NOT NULL CHECK (puntuacion BETWEEN 1 AND 5),

    comentario TEXT,

    fecha_resena DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario)
    REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_reserva)
    REFERENCES reservas(id_reserva)
);



CREATE TABLE logs (
    id_log INT AUTO_INCREMENT PRIMARY KEY,

    id_usuario INT,

    accion VARCHAR(255) NOT NULL,

    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario)
    REFERENCES usuarios(id_usuario)
)
