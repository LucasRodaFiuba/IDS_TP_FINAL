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
    restriccion VARCHAR(20) CHECK (restriccion IN ('ninguno','sin lactosa', 'vegetariano', 'vegano', 'sin tacc')),
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
);
CREATE TABLE servicios_extra (
    id_servicio INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(250),
    descripcion VARCHAR(250)
);

INSERT INTO servicios_extra (nombre,descripcion) VALUES
('Rampa de acceso para sillas de ruedas','Facilitamos el acceso a todas las personas con una rampa especialmente 
diseñada para garantizar comodidad, seguridad y autonomía. 
Cada detalle está pensado para que todos puedan disfrutar de la experiencia sin barreras.'),
('Menu vegano','Una selección de platos frescos y equilibrados, elaborados con ingredientes de origen vegetal. 
Combinamos sabor, creatividad y nutrición para ofrecer opciones deliciosas sin productos animales.'),
('Mejor amigo','Tu mascota también es parte de la familia. Contamos con un espacio pensado para que pueda acompañarte cómodamente mientras disfrutás de tu comida,
 con ambiente seguro y amigable.'),
('Wifi','Disfrutá de conexión gratuita a internet en todo el local. 
Ya sea para trabajar, estudiar o compartir tu experiencia, te mantenemos siempre conectado.'),
('Un año mas','Convertimos tu cumpleaños en una experiencia única. Decoración especial, atención personalizada y la posibilidad de 
sorprender a esa persona especial con un momento inolvidable en Le Maison Gourmet.'),
('Niños','Un área pensada para los más pequeños, donde pueden divertirse de forma segura mientras los 
adultos disfrutan con tranquilidad. Un ambiente familiar, cómodo y supervisado.'),
('Terraza','Un espacio al aire libre rodeado de un ambiente cálido y relajado. Ideal para disfrutar de una comida tranquila, 
buena compañía y aire fresco en cualquier momento del día.');

CREATE TABLE reserva_servicios (
    id_reserva INT,
    id_servicio INT,

    FOREIGN KEY (id_reserva) REFERENCES reservas(id_reserva),
    FOREIGN KEY (id_servicio) REFERENCES servicios_extra(id_servicio)
);
