CREATE DATABASE Kora

USE Kora

-- BASE DE DATOS KORA - SISTEMA EDUCATIVO
-- Estructura de tablas basada en el documento de materias y programas
-- SINTAXIS PARA SQL SERVER

-- Tabla de materias principales
CREATE TABLE materias (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL UNIQUE,
    descripcion NTEXT,
    activa BIT DEFAULT 1,
    fecha_creacion DATETIME2 DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 DEFAULT GETDATE()
);

-- Tabla de ejes (Lectura, Escritura, etc.)
CREATE TABLE ejes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo NVARCHAR(10) NOT NULL UNIQUE, -- L, E, etc.
    nombre NVARCHAR(50) NOT NULL,
    descripcion NTEXT
);

-- Tabla de programas
CREATE TABLE programas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    materia_id INT NOT NULL,
    eje_id INT,
    nombre NVARCHAR(100) NOT NULL,
    nombre_comercial NVARCHAR(100),
    grado_inicio NVARCHAR(10), -- K, 1, 2, etc.
    grado_fin NVARCHAR(10),
    descripcion_breve NTEXT,
    prerrequisitos NTEXT,
    activo BIT DEFAULT 1,
    orden_secuencial INT,
    fecha_creacion DATETIME2 DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 DEFAULT GETDATE(),
    
    CONSTRAINT FK_programas_materia FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE,
    CONSTRAINT FK_programas_eje FOREIGN KEY (eje_id) REFERENCES ejes(id) ON DELETE SET NULL
);

-- Crear �ndices para programas
CREATE INDEX IX_programas_materia_grado ON programas(materia_id, grado_inicio, grado_fin);
CREATE INDEX IX_programas_orden ON programas(orden_secuencial);

-- Tabla de etapas dentro de cada programa
CREATE TABLE etapas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    programa_id INT NOT NULL,
    numero_etapa INT NOT NULL,
    nombre NVARCHAR(100) NOT NULL,
    prerrequisitos NTEXT,
    contenido NTEXT,
    objetivos NTEXT,
    evaluacion NTEXT,
    orden_secuencial INT,
    activa BIT DEFAULT 1,
    fecha_creacion DATETIME2 DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 DEFAULT GETDATE(),
    
    CONSTRAINT FK_etapas_programa FOREIGN KEY (programa_id) REFERENCES programas(id) ON DELETE CASCADE,
    CONSTRAINT UQ_etapas_programa_numero UNIQUE (programa_id, numero_etapa)
);

-- Crear �ndices para etapas
CREATE INDEX IX_etapas_programa_orden ON etapas(programa_id, orden_secuencial);

-- Tabla de tipos de actividades
CREATE TABLE tipos_actividades (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL UNIQUE,
    descripcion NTEXT
);

-- Tabla de actividades por etapa
CREATE TABLE actividades (
    id INT IDENTITY(1,1) PRIMARY KEY,
    etapa_id INT NOT NULL,
    tipo_actividad_id INT NOT NULL,
    nombre NVARCHAR(100) NOT NULL,
    descripcion NTEXT,
    instrucciones NTEXT,
    tiempo_estimado INT, -- en minutos
    orden_secuencial INT,
    activa BIT DEFAULT 1,
    fecha_creacion DATETIME2 DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 DEFAULT GETDATE(),
    
    CONSTRAINT FK_actividades_etapa FOREIGN KEY (etapa_id) REFERENCES etapas(id) ON DELETE CASCADE,
    CONSTRAINT FK_actividades_tipo FOREIGN KEY (tipo_actividad_id) REFERENCES tipos_actividades(id)
);

-- Crear �ndices para actividades
CREATE INDEX IX_actividades_etapa_tipo ON actividades(etapa_id, tipo_actividad_id);
CREATE INDEX IX_actividades_orden ON actividades(orden_secuencial);

-- Tabla de ejercicios espec�ficos
CREATE TABLE ejercicios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    actividad_id INT NOT NULL,
    nombre NVARCHAR(100) NOT NULL,
    enunciado NTEXT,
    tipo_respuesta NVARCHAR(50) DEFAULT 'opcion_multiple', -- opcion_multiple, texto_libre, verdadero_falso, ordenamiento, clasificacion
    contenido_ejercicio NVARCHAR(MAX), -- Para almacenar JSON con opciones, respuestas correctas, etc.
    puntuacion_maxima INT DEFAULT 100,
    tiempo_limite INT, -- en segundos
    orden_secuencial INT,
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME2 DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 DEFAULT GETDATE(),
    
    CONSTRAINT FK_ejercicios_actividad FOREIGN KEY (actividad_id) REFERENCES actividades(id) ON DELETE CASCADE,
    CONSTRAINT CK_ejercicios_tipo_respuesta CHECK (tipo_respuesta IN ('opcion_multiple', 'texto_libre', 'verdadero_falso', 'ordenamiento', 'clasificacion'))
);

-- Crear �ndices para ejercicios
CREATE INDEX IX_ejercicios_actividad_orden ON ejercicios(actividad_id, orden_secuencial);
CREATE INDEX IX_ejercicios_tipo_respuesta ON ejercicios(tipo_respuesta);

-- Tabla para gestionar prerrequisitos entre programas
CREATE TABLE prerrequisitos_programas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    programa_id INT NOT NULL,
    prerrequisito_programa_id INT NOT NULL,
    obligatorio BIT DEFAULT 1,
    
    CONSTRAINT FK_prereq_prog_programa FOREIGN KEY (programa_id) REFERENCES programas(id) ON DELETE CASCADE,
    CONSTRAINT FK_prereq_prog_prerequisito FOREIGN KEY (prerrequisito_programa_id) REFERENCES programas(id),
    CONSTRAINT UQ_prerrequisitos_programas UNIQUE (programa_id, prerrequisito_programa_id),
    CONSTRAINT CK_prereq_prog_no_circular CHECK (programa_id != prerrequisito_programa_id)
);

-- Tabla para gestionar prerrequisitos entre etapas
CREATE TABLE prerrequisitos_etapas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    etapa_id INT NOT NULL,
    prerrequisito_etapa_id INT NOT NULL,
    obligatorio BIT DEFAULT 1,
    
    CONSTRAINT FK_prereq_etapa_etapa FOREIGN KEY (etapa_id) REFERENCES etapas(id) ON DELETE CASCADE,
    CONSTRAINT FK_prereq_etapa_prerequisito FOREIGN KEY (prerrequisito_etapa_id) REFERENCES etapas(id),
    CONSTRAINT UQ_prerrequisitos_etapas UNIQUE (etapa_id, prerrequisito_etapa_id),
    CONSTRAINT CK_prereq_etapa_no_circular CHECK (etapa_id != prerrequisito_etapa_id)
);

-- TRIGGER para actualizar fecha_actualizacion autom�ticamente en programas
GO
CREATE TRIGGER tr_programas_update
ON programas
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE programas 
    SET fecha_actualizacion = GETDATE()
    FROM programas p
    INNER JOIN inserted i ON p.id = i.id;
END;
GO

-- TRIGGER para actualizar fecha_actualizacion autom�ticamente en etapas
CREATE TRIGGER tr_etapas_update
ON etapas
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE etapas 
    SET fecha_actualizacion = GETDATE()
    FROM etapas e
    INNER JOIN inserted i ON e.id = i.id;
END;
GO

-- TRIGGER para actualizar fecha_actualizacion autom�ticamente en actividades
CREATE TRIGGER tr_actividades_update
ON actividades
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE actividades 
    SET fecha_actualizacion = GETDATE()
    FROM actividades a
    INNER JOIN inserted i ON a.id = i.id;
END;
GO

-- TRIGGER para actualizar fecha_actualizacion autom�ticamente en ejercicios
CREATE TRIGGER tr_ejercicios_update
ON ejercicios
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE ejercicios 
    SET fecha_actualizacion = GETDATE()
    FROM ejercicios e
    INNER JOIN inserted i ON e.id = i.id;
END;
GO

-- DATOS INICIALES
-- Insertar las materias principales
INSERT INTO materias (nombre, descripcion) VALUES 
(N'Literacidad', N'Desarrollo de habilidades de lectura y escritura'),
(N'Matem�ticas', N'Desarrollo de habilidades matem�ticas'),
(N'Investigaci�n', N'Desarrollo de habilidades de investigaci�n y an�lisis');

-- Insertar los ejes
INSERT INTO ejes (codigo, nombre, descripcion) VALUES 
(N'L', N'Lectura', N'Eje enfocado en habilidades de lectura y comprensi�n'),
(N'E', N'Escritura', N'Eje enfocado en habilidades de escritura y expresi�n'),
(N'M', N'Matem�ticas', N'Eje enfocado en habilidades matem�ticas'),
(N'I', N'Investigaci�n', N'Eje enfocado en habilidades de investigaci�n');

-- Insertar tipos de actividades comunes
INSERT INTO tipos_actividades (nombre, descripcion) VALUES 
(N'Clasificaci�n', N'Actividades donde el estudiante debe clasificar elementos'),
(N'Identificaci�n', N'Actividades donde el estudiante debe identificar elementos espec�ficos'),
(N'Comprensi�n', N'Actividades enfocadas en la comprensi�n lectora'),
(N'Escritura Creativa', N'Actividades de producci�n escrita'),
(N'Ejercicios Pr�cticos', N'Ejercicios de aplicaci�n pr�ctica');

-- Ejemplo de programas para Literacidad (basado en el documento)
INSERT INTO programas (materia_id, eje_id, nombre, nombre_comercial, grado_inicio, grado_fin, descripcion_breve, orden_secuencial) VALUES 
(1, 1, N'Conciencia fonol�gica', NULL, N'K', N'1', N'Desarrollo de la conciencia fonol�gica', 1),
(1, 1, N'Decodificaci�n', N'Camino sil�bico', N'1', N'2', N'Desarrollo de habilidades de decodificaci�n', 2),
(1, 1, N'Lectura intermedia', NULL, N'3', N'4', N'Desarrollo de lectura intermedia', 3),
(1, 1, N'Lectura avanzada', NULL, N'5', N'6', N'Desarrollo de lectura avanzada', 4),
(1, 2, N'Grafemas', NULL, N'1', N'2', N'Aprendizaje de grafemas', 1),
(1, 2, N'Escritura intermedia', NULL, N'3', N'4', N'Desarrollo de escritura intermedia', 2),
(1, 2, N'Escritura avanzada', NULL, N'5', N'6', N'Desarrollo de escritura avanzada', 3),
(1, 2, N'Gram�tica', NULL, N'1', N'6', N'Aprendizaje de gram�tica', 4),
(1, 2, N'Ortograf�a', NULL, N'3', N'6', N'Desarrollo de habilidades ortogr�ficas', 5),
(1, 1, N'Comprensi�n lectora', NULL, N'1', N'6', N'Desarrollo de comprensi�n lectora', 5);

-- Establecer prerrequisito (Conciencia fonol�gica es prerrequisito de Decodificaci�n)
INSERT INTO prerrequisitos_programas (programa_id, prerrequisito_programa_id) VALUES 
(2, 1); -- Decodificaci�n requiere Conciencia fonol�gica

-- Ejemplo de etapa para el programa de Decodificaci�n
INSERT INTO etapas (programa_id, numero_etapa, nombre, prerrequisitos, contenido, objetivos, orden_secuencial) VALUES
(2, 1, N'Vocales', N'Discriminar sonidos. Habilidades relacionadas a la conciencia fonol�gica.', N'A E I O U', N'Identificar el sonido al inicio, medio y fin de una palabra. Reconocer la forma escrita.', 1);

-- ============================================
-- TABLAS DE AUTENTICACI�N
-- ============================================

-- Tabla de roles
CREATE TABLE roles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(50) NOT NULL UNIQUE,
    descripcion NTEXT,
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME2 DEFAULT GETDATE()
);

-- Tabla de usuarios
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    email NVARCHAR(100) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    nombre NVARCHAR(100),
    apellido NVARCHAR(100),
    rol_id INT NOT NULL,
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME2 DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 DEFAULT GETDATE(),

    CONSTRAINT FK_usuarios_rol FOREIGN KEY (rol_id) REFERENCES roles(id)
);

-- Crear �ndices para usuarios
CREATE INDEX IX_usuarios_rol ON usuarios(rol_id);
CREATE INDEX IX_usuarios_email ON usuarios(email);

-- TRIGGER para actualizar fecha_actualizacion autom�ticamente en usuarios
GO
CREATE TRIGGER tr_usuarios_update
ON usuarios
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE usuarios
    SET fecha_actualizacion = GETDATE()
    FROM usuarios u
    INNER JOIN inserted i ON u.id = i.id;
END;
GO

-- ============================================
-- TABLA DE ACTIVIDADES DE USUARIOS
-- ============================================

-- Tabla para rastrear el progreso de cada usuario en cada actividad
CREATE TABLE actividades_usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT NOT NULL,
    actividad_id INT NOT NULL,
    estado NVARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, in_progress, completed, abandoned
    fecha_inicio DATETIME2 NULL,
    fecha_completado DATETIME2 NULL,
    progreso_porcentaje DECIMAL(5,2) DEFAULT 0.00,
    tiempo_dedicado INT NULL, -- en minutos
    intentos INT DEFAULT 0,
    fecha_creacion DATETIME2 DEFAULT GETDATE(),
    fecha_actualizacion DATETIME2 DEFAULT GETDATE(),

    CONSTRAINT FK_actividades_usuarios_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT FK_actividades_usuarios_actividad FOREIGN KEY (actividad_id) REFERENCES actividades(id) ON DELETE CASCADE,
    CONSTRAINT CK_actividades_usuarios_estado CHECK (estado IN ('pending', 'in_progress', 'completed', 'abandoned')),
    CONSTRAINT UQ_actividades_usuarios_usuario_actividad UNIQUE (usuario_id, actividad_id)
);

-- Crear �ndices para actividades_usuarios
CREATE INDEX IX_actividades_usuarios_usuario ON actividades_usuarios(usuario_id);
CREATE INDEX IX_actividades_usuarios_actividad ON actividades_usuarios(actividad_id);
CREATE INDEX IX_actividades_usuarios_estado ON actividades_usuarios(estado);

-- TRIGGER para actualizar fecha_actualizacion autom�ticamente en actividades_usuarios
GO
CREATE TRIGGER tr_actividades_usuarios_update
ON actividades_usuarios
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE actividades_usuarios
    SET fecha_actualizacion = GETDATE()
    FROM actividades_usuarios au
    INNER JOIN inserted i ON au.id = i.id;
END;
GO

-- Insert initial roles
INSERT INTO roles (nombre, descripcion, activo) VALUES
(N'student', N'Student of the educational system', 1),
(N'teacher', N'Teacher of the educational system', 1),
(N'admin', N'System administrator', 1);

-- ============================================
-- VISTAS �TILES
-- Vista para obtener informaci�n completa de programas
GO
CREATE VIEW vista_programas_completa AS
SELECT 
    p.id,
    p.nombre as programa_nombre,
    p.nombre_comercial,
    m.nombre as materia_nombre,
    e.nombre as eje_nombre,
    e.codigo as eje_codigo,
    CONCAT(p.grado_inicio, N'-', p.grado_fin) as rango_grados,
    p.descripcion_breve,
    p.prerrequisitos,
    p.orden_secuencial,
    p.activo
FROM programas p
INNER JOIN materias m ON p.materia_id = m.id
LEFT JOIN ejes e ON p.eje_id = e.id
WHERE p.activo = 1 AND m.activa = 1;
GO

-- Vista para obtener la secuencia completa: materia -> programa -> etapa
CREATE VIEW vista_secuencia_completa AS
SELECT
    m.nombre as materia,
    p.nombre as programa,
    et.numero_etapa,
    et.nombre as etapa,
    CONCAT(p.grado_inicio, N'-', p.grado_fin) as grados,
    et.contenido,
    et.objetivos
FROM materias m
INNER JOIN programas p ON m.id = p.materia_id
INNER JOIN etapas et ON p.id = et.programa_id
WHERE m.activa = 1 AND p.activo = 1 AND et.activa = 1;
GO

-- Vista para obtener el progreso de usuarios en actividades
CREATE VIEW vista_progreso_usuarios AS
SELECT
    u.id as usuario_id,
    u.username,
    u.nombre as usuario_nombre,
    u.apellido as usuario_apellido,
    r.nombre as rol,
    a.id as actividad_id,
    a.nombre as actividad_nombre,
    ta.nombre as tipo_actividad,
    et.nombre as etapa_nombre,
    p.nombre as programa_nombre,
    m.nombre as materia_nombre,
    au.estado,
    au.progreso_porcentaje,
    au.fecha_inicio,
    au.fecha_completado,
    au.tiempo_dedicado,
    au.intentos
FROM usuarios u
INNER JOIN roles r ON u.rol_id = r.id
LEFT JOIN actividades_usuarios au ON u.id = au.usuario_id
LEFT JOIN actividades a ON au.actividad_id = a.id
LEFT JOIN tipos_actividades ta ON a.tipo_actividad_id = ta.id
LEFT JOIN etapas et ON a.etapa_id = et.id
LEFT JOIN programas p ON et.programa_id = p.id
LEFT JOIN materias m ON p.materia_id = m.id
WHERE u.activo = 1;
GO

-- Vista para actividades pendientes por usuario
CREATE VIEW vista_actividades_pendientes AS
SELECT
    u.id as usuario_id,
    u.username,
    u.nombre as usuario_nombre,
    a.id as actividad_id,
    a.nombre as actividad_nombre,
    ta.nombre as tipo_actividad,
    et.nombre as etapa_nombre,
    p.nombre as programa_nombre,
    au.estado,
    au.progreso_porcentaje
FROM usuarios u
INNER JOIN actividades_usuarios au ON u.id = au.usuario_id
INNER JOIN actividades a ON au.actividad_id = a.id
INNER JOIN tipos_actividades ta ON a.tipo_actividad_id = ta.id
INNER JOIN etapas et ON a.etapa_id = et.id
INNER JOIN programas p ON et.programa_id = p.id
WHERE u.activo = 1
  AND au.estado IN ('pending', 'in_progress')
  AND a.activa = 1;