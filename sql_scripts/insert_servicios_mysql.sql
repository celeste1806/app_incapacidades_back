-- =====================================================
-- INSERT para tabla parametro_hijo con parametro_id = 9 (Servicios)
-- Generado automaticamente desde servicios.txt
-- Base de datos: MySQL
-- Total de servicios: 29
-- =====================================================

-- Configuracion inicial para MySQL
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Limpiar datos existentes (opcional)
-- DELETE FROM parametro_hijo WHERE parametro_id = 9;

-- Lote 1 de 1 (registros 1-29)
INSERT INTO parametro_hijo (parametro_id, nombre, descripcion, estado) VALUES
(9, 'CALIDAD', 'SERVICIO', 1),
(9, 'CANGURO', 'SERVICIO', 1),
(9, 'CARTERA', 'SERVICIO', 1),
(9, 'CENTRAL ESTERILIZACION', 'SERVICIO', 1),
(9, 'CITAS', 'SERVICIO', 1),
(9, 'QUIROFANO', 'SERVICIO', 1),
(9, 'CONSULTA EXTERNA', 'SERVICIO', 1),
(9, 'SALA DE PARTOS', 'SERVICIO', 1),
(9, 'CONTABILIDAD', 'SERVICIO', 1),
(9, 'DEPARTAMENTO DE ENFERMERIA', 'SERVICIO', 1),
(9, 'FACTURACION', 'SERVICIO', 1),
(9, 'FARMACIA', 'SERVICIO', 1),
(9, 'GERENCIA', 'SERVICIO', 1),
(9, 'HOSPITALIZACION', 'SERVICIO', 1),
(9, 'IMAGENES DIAGNOSTICAS', 'SERVICIO', 1),
(9, 'LABORATORIO', 'SERVICIO', 1),
(9, 'MANTENIMIENTO', 'SERVICIO', 1),
(9, 'PLANEACION Y CALIDAD', 'SERVICIO', 1),
(9, 'CIRUGIA', 'SERVICIO', 1),
(9, 'MANTENIMIENTO', 'SERVICIO', 1),
(9, 'PLANEACION Y CALIDAD', 'SERVICIO', 1),
(9, 'SISTEMAS', 'SERVICIO', 1),
(9, 'SUBGERENCIA ASISTENCIAL', 'SERVICIO', 1),
(9, 'TALENTO HUMANO', 'SERVICIO', 1),
(9, 'UCI', 'SERVICIO', 1),
(9, 'UCIA', 'SERVICIO', 1),
(9, 'CONSULTA PRIORITARIA', 'SERVICIO', 1),
(9, 'UCIN', 'SERVICIO', 1),
(9, 'AMBIENTE SEGURO', 'SERVICIO', 1);

-- Restaurar configuracion
SET FOREIGN_KEY_CHECKS = 1;

-- Verificar insercion
SELECT COUNT(*) as total_servicios FROM parametro_hijo WHERE parametro_id = 9;

-- Mostrar algunos ejemplos
SELECT id_parametrohijo, nombre, descripcion FROM parametro_hijo WHERE parametro_id = 9 LIMIT 10;