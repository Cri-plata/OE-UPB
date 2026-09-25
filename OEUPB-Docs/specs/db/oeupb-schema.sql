-- OE UPB: esquema de referencia del modelo SQLAlchemy actual.
-- Verificado: 2026-09-24.
-- No sustituye migraciones. Antes de ejecutar en un entorno real, comparar con la BD.

CREATE TABLE sedes (
    id INT NOT NULL,
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    activa BOOLEAN NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_sedes_codigo (codigo),
    UNIQUE KEY uq_sedes_nombre (nombre)
);

CREATE TABLE usuarios (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    sede_id INT NULL,
    debe_cambiar_contrasena BOOLEAN NOT NULL,
    credencial_temporal_expira_en DATETIME NULL,
    activo BOOLEAN NOT NULL,
    version_autorizacion INT NOT NULL,
    etiqueta VARCHAR(30) NULL,
    permisos JSON NOT NULL,
    programas JSON NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_usuarios_correo (correo),
    KEY ix_usuarios_id (id),
    KEY ix_usuarios_correo (correo),
    CONSTRAINT fk_usuarios_sede FOREIGN KEY (sede_id) REFERENCES sedes (id)
);

CREATE TABLE auditoria_cuentas (
    id INT NOT NULL AUTO_INCREMENT,
    accion VARCHAR(30) NOT NULL,
    actor_id INT NOT NULL,
    actor_correo VARCHAR(100) NOT NULL,
    objetivo_id INT NOT NULL,
    objetivo_correo VARCHAR(100) NOT NULL,
    objetivo_rol VARCHAR(50) NOT NULL,
    sede_id INT NULL,
    motivo TEXT NOT NULL,
    fecha DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY ix_auditoria_cuentas_id (id)
);

CREATE TABLE egresados (
    numero_documento VARCHAR(50) NOT NULL,
    primer_nombre VARCHAR(100) NULL,
    primer_apellido VARCHAR(100) NULL,
    programa VARCHAR(150) NULL,
    fecha_grado DATETIME NULL,
    PRIMARY KEY (numero_documento),
    KEY ix_egresados_numero_documento (numero_documento)
);

CREATE TABLE egresados_sedes (
    id INT NOT NULL AUTO_INCREMENT,
    egresado_documento VARCHAR(50) NOT NULL,
    sede_id INT NOT NULL,
    creado_por_id INT NOT NULL,
    fecha_creacion DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_egresado_sede (egresado_documento, sede_id),
    CONSTRAINT fk_egresados_sedes_egresado FOREIGN KEY (egresado_documento) REFERENCES egresados (numero_documento),
    CONSTRAINT fk_egresados_sedes_sede FOREIGN KEY (sede_id) REFERENCES sedes (id),
    CONSTRAINT fk_egresados_sedes_actor FOREIGN KEY (creado_por_id) REFERENCES usuarios (id)
);

CREATE TABLE auditoria_egresados (
    id INT NOT NULL AUTO_INCREMENT,
    accion VARCHAR(20) NOT NULL,
    actor_id INT NOT NULL,
    actor_correo VARCHAR(100) NOT NULL,
    sede_id INT NOT NULL,
    egresado_documento VARCHAR(50) NOT NULL,
    cambios JSON NOT NULL,
    motivo TEXT NOT NULL,
    fecha DATETIME NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_auditoria_egresados_actor FOREIGN KEY (actor_id) REFERENCES usuarios (id),
    CONSTRAINT fk_auditoria_egresados_sede FOREIGN KEY (sede_id) REFERENCES sedes (id)
);

CREATE TABLE cargas (
    id INT NOT NULL AUTO_INCREMENT,
    nombre_archivo VARCHAR(255) NOT NULL,
    hash_archivo VARCHAR(64) NOT NULL,
    fecha_carga DATETIME NOT NULL,
    usuario_id INT NOT NULL,
    sede_id INT NOT NULL,
    momento INT NOT NULL,
    anio_grado INT NOT NULL,
    estado VARCHAR(30) NOT NULL,
    version INT NOT NULL,
    registros INT NOT NULL,
    errores JSON NULL,
    reemplaza_carga_id INT NULL,
    PRIMARY KEY (id),
    KEY ix_cargas_id (id),
    KEY ix_cargas_alcance (sede_id, momento, anio_grado, estado),
    CONSTRAINT ck_cargas_momento CHECK (momento IN (0, 1, 5)),
    CONSTRAINT fk_cargas_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
    CONSTRAINT fk_cargas_reemplazo FOREIGN KEY (reemplaza_carga_id) REFERENCES cargas (id),
    CONSTRAINT fk_cargas_sede FOREIGN KEY (sede_id) REFERENCES sedes (id)
);

CREATE TABLE mediciones (
    id INT NOT NULL AUTO_INCREMENT,
    carga_id INT NOT NULL,
    egresado_documento VARCHAR(50) NULL,
    momento INT NOT NULL,
    anio INT NOT NULL,
    sede_id INT NOT NULL,
    intento INT NOT NULL,
    fecha_registro DATETIME NOT NULL,
    respuestas JSON NOT NULL,
    PRIMARY KEY (id),
    KEY ix_mediciones_id (id),
    KEY ix_mediciones_carga_id (carga_id),
    CONSTRAINT fk_mediciones_cargas
        FOREIGN KEY (carga_id)
        REFERENCES cargas (id),
    UNIQUE KEY uq_mediciones_intento_identificado (egresado_documento, sede_id, momento, anio, intento),
    CONSTRAINT ck_mediciones_momento CHECK (momento IN (0, 1, 5)),
    CONSTRAINT fk_mediciones_sede FOREIGN KEY (sede_id) REFERENCES sedes (id),
    CONSTRAINT fk_mediciones_egresados
        FOREIGN KEY (egresado_documento)
        REFERENCES egresados (numero_documento)
);

CREATE TABLE eventos_eliminacion_carga (
    id INT NOT NULL AUTO_INCREMENT,
    carga_id_eliminada INT NOT NULL,
    actor_id INT NOT NULL,
    actor_correo VARCHAR(100) NOT NULL,
    sede_id INT NOT NULL,
    momento INT NOT NULL,
    anio_grado INT NOT NULL,
    version INT NOT NULL,
    registros INT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    hash_archivo VARCHAR(64) NOT NULL,
    motivo TEXT NOT NULL,
    fecha DATETIME NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_evento_carga_actor FOREIGN KEY (actor_id) REFERENCES usuarios (id),
    CONSTRAINT fk_evento_carga_sede FOREIGN KEY (sede_id) REFERENCES sedes (id)
);

CREATE TABLE publicaciones_graficas (
    id INT NOT NULL AUTO_INCREMENT,
    grafica_key VARCHAR(100) NOT NULL,
    titulo VARCHAR(180) NOT NULL,
    sede_id INT NOT NULL,
    coordinador_id INT NOT NULL,
    coordinador_correo VARCHAR(100) NOT NULL,
    programas JSON NOT NULL,
    permiso_requerido VARCHAR(40) NOT NULL,
    definicion JSON NOT NULL,
    metricas JSON NOT NULL,
    version INT NOT NULL,
    aprobada_privacidad BOOLEAN NOT NULL,
    estado VARCHAR(20) NOT NULL,
    fecha_creacion DATETIME NOT NULL,
    fecha_publicacion DATETIME NOT NULL,
    fecha_retiro DATETIME NULL,
    retirado_por_id INT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_publicaciones_grafica_version (sede_id, grafica_key, version),
    KEY ix_publicaciones_audiencia (estado, sede_id, permiso_requerido),
    CONSTRAINT ck_publicaciones_estado CHECK (estado IN ('publicada', 'retirada', 'reemplazada')),
    CONSTRAINT fk_publicaciones_sede FOREIGN KEY (sede_id) REFERENCES sedes (id),
    CONSTRAINT fk_publicaciones_coordinador FOREIGN KEY (coordinador_id) REFERENCES usuarios (id),
    CONSTRAINT fk_publicaciones_retirado_por FOREIGN KEY (retirado_por_id) REFERENCES usuarios (id)
);
