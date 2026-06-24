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
    fecha_cancelacion DATETIME NULL,
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
    id_reserva INT NULL,

    puntuacion INT NOT NULL CHECK (puntuacion BETWEEN 1 AND 5),

    comentario TEXT,

    fecha_resena DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario)
    REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_reserva)
    REFERENCES reservas(id_reserva)

    FOREIGN KEY (id_plato)
    REFERENCES menu(id_plato)
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
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
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
('Silla para bebes','Disponemos de sillas especialmente diseñadas para bebés y niños pequeños, brindando mayor comodidad y seguridad para toda la familia.'),
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
-- =========================
-- DATOS DE PRUEBA
-- =========================




INSERT INTO usuarios
(nombre, apellido, email, password, telefono, id_rol)
VALUES
('Miguel','Ruiz','miguel@gmail.com','$2b$12$xdgqem4X2/xPM68/.m4VDOpVDAju31dggj6HhTBgr9HFYO/ut.K.e','1134567890',1),
('Sofía','Gómez','sofia@gmail.com','$2b$12$xdgqem4X2/xPM68/.m4VDOpVDAju31dggj6HhTBgr9HFYO/ut.K.e','1165478921',2),
('Lucas','Fernández','lucas@gmail.com','$2b$12$xdgqem4X2/xPM68/.m4VDOpVDAju31dggj6HhTBgr9HFYO/ut.K.e','1178954632',2),
('Martina','López','martina@gmail.com','$2b$12$xdgqem4X2/xPM68/.m4VDOpVDAju31dggj6HhTBgr9HFYO/ut.K.e','1198765432',2),
('Juan','Pérez','juan@gmail.com','$2b$12$xdgqem4X2/xPM68/.m4VDOpVDAju31dggj6HhTBgr9HFYO/ut.K.e','1122334455',2),
('Valentina','Torres','valentina@gmail.com','$2b$12$xdgqem4X2/xPM68/.m4VDOpVDAju31dggj6HhTBgr9HFYO/ut.K.e','1145678912',2),
('Tomás','Martínez','tomas@gmail.com','$2b$12$xdgqem4X2/xPM68/.m4VDOpVDAju31dggj6HhTBgr9HFYO/ut.K.e     ','1167891234',2),
('Camila','Suárez','camila@gmail.com','$2b$12$xdgqem4X2/xPM68/.m4VDOpVDAju31dggj6HhTBgr9HFYO/ut.K.e','1154321987',2),
('Franco','Romero','franco@gmail.com','$2b$12$xdgqem4X2/xPM68/.m4VDOpVDAju31dggj6HhTBgr9HFYO/ut.K.e','1171234567',2),
('Julieta','Castro','julieta@gmail.com','$2b$12$xdgqem4X2/xPM68/.m4VDOpVDAju31dggj6HhTBgr9HFYO/ut.K.e','1198761111',2);


/* =========================
   MESAS
   ========================= */
INSERT INTO mesas (capacidad, ubicacion, disponible) VALUES
(2, 'Ventana', TRUE)
(2, 'Barra', TRUE)
(3, 'Centro', TRUE)
(4, 'Salón principal', TRUE),
(6, 'Terraza', TRUE);


/* =========================
   CATEGORÍAS
   ========================= */

INSERT INTO categorias_menu(nombre)
VALUES
('Entradas'),
('Platos Principales'),
('Postres'),
('Bebidas');


/* =========================
   MENÚ
   ========================= */

INSERT INTO menu
(nombre,descripcion,precio,restriccion,imagen,categoria)
VALUES

('Empanadas Criollas',
'Empanadas de carne cortada a cuchillo.',
3200,
'ninguno',
'empanadas.jpg',
'entrada'),

('Provoleta',
'Provoleta a la parrilla con orégano.',
4800,
'vegetariano',
'provoleta.jpg',
'entrada'),

('Mollejas',
'Mollejas crocantes a la parrilla.',
6900,
'ninguno',
'mollejas.jpg',
'entrada'),

('Bife de Chorizo',
'Bife premium acompañado con papas rústicas.',
18900,
'ninguno',
'bife.jpg',
'plato_principal'),

('Salmón Grillado',
'Salmón con vegetales salteados.',
20500,
'sin lactosa',
'salmon.jpg',
'plato_principal'),

('Ravioles de Verdura',
'Pasta casera con salsa fileto.',
12400,
'vegetariano',
'ravioles.jpg',
'plato_principal'),

('Milanesa Napolitana',
'Con papas fritas.',
14900,
'ninguno',
'milanesa.jpg',
'plato_principal'),

('Flan Casero',
'Con dulce de leche y crema.',
3900,
'vegetariano',
'flan.jpg',
'postre'),

('Volcán de Chocolate',
'Con helado de vainilla.',
5600,
'vegetariano',
'volcan.jpg',
'postre'),

('Cheesecake',
'Con frutos rojos.',
5400,
'vegetariano',
'cheesecake.jpg',
'postre'),

('Limonada',
'Limonada con menta y jengibre.',
2800,
'vegano',
'limonada.jpg',
'bebida'),

('Malbec Reserva',
'Copa de vino Malbec.',
5200,
'ninguno',
'malbec.jpg',
'bebida'),

('Agua Mineral',
'Con o sin gas.',
1800,
'vegano',
'agua.jpg',
'bebida'),

('Cerveza Artesanal',
'Pinta de cerveza rubia.',
4200,
'ninguno',
'cerveza.jpg',
'bebida');


/* =========================
   RESERVAS
   ========================= */

INSERT INTO reservas
(id_usuario,numero_mesa,fecha_reserva,hora_reserva,cantidad_personas,estado,codigo_qr)
VALUES
(2,1,'2026-06-28','20:30:00',2,'confirmada','QR001'),
(3,4,'2026-06-29','21:00:00',4,'pendiente','QR002'),
(4,7,'2026-06-30','20:00:00',6,'confirmada','QR003'),
(5,2,'2026-07-01','22:00:00',2,'cancelada','QR004'),
(6,5,'2026-07-03','20:30:00',4,'finalizada','QR005'),
(7,9,'2026-07-05','21:30:00',8,'confirmada','QR006'),
(8,6,'2026-07-07','20:00:00',4,'pendiente','QR007'),
(9,3,'2026-07-08','19:30:00',2,'confirmada','QR008'),
(10,8,'2026-07-10','21:00:00',6,'confirmada','QR009');


/* =========================
   RESEÑAS
   ========================= */

INSERT INTO resenas
(id_usuario,id_reserva,puntuacion,comentario)
VALUES
(2,1,5,'Excelente atención y comida espectacular.'),
(3,2,4,'Muy buena experiencia, volvería sin dudas.'),
(4,3,5,'La carne estaba en su punto justo.'),
(5,NULL,3,'Buen ambiente, aunque demoró un poco la comida.'),
(6,5,5,'El mejor restaurante que visité este año.'),
(7,6,4,'Muy recomendable para ir en familia.'),
(8,7,5,'La atención fue impecable y los platos deliciosos.'),
(9,8,4,'Muy lindo lugar y excelente servicio.'),
(10,9,5,'Todo perfecto, desde la entrada hasta el postre.');


/* =========================
   LOGS
   ========================= */

INSERT INTO logs
(id_usuario,accion)
VALUES
(1,'Inicio de sesión'),
(2,'Creó una reserva'),
(3,'Modificó una reserva'),
(4,'Canceló una reserva'),
(5,'Publicó una reseña'),
(6,'Creó una reserva'),
(7,'Publicó una reseña'),
(8,'Actualizó sus datos'),
(9,'Realizó una reserva'),
(10,'Canceló una reserva'),
(1,'Agregó un servicio extra'),
(1,'Actualizó un plato del menú');


/* =========================
   RESERVA - SERVICIOS
   ========================= */

INSERT INTO reserva_servicios
(id_reserva,id_servicio)
VALUES
(1,1),
(1,2),
(2,7),
(3,5),
(3,6),
(4,4),
(5,6),
(6,3),
(7,2),
(8,1),
(8,7),
(9,5);