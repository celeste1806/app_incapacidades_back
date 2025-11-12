-- =====================================================
-- COMANDOS SQL INDIVIDUALES PARA PARAMETRO_HIJO
-- =====================================================
-- Estos son ejemplos de comandos INSERT individuales
-- para la tabla parametro_hijo con parametro_id = 7 (Diagnosticos)

-- Ejemplo 1: Insertar un diagnostico individual
INSERT INTO parametro_hijo (parametro_id, nombre, descripcion, estado) VALUES
(7, 'A000', 'COLERA DEBIDO A VIBRIO CHOLERAE O1, BIOTIPO CHOLERAE', 1);

-- Ejemplo 2: Insertar varios diagnosticos en un solo comando
INSERT INTO parametro_hijo (parametro_id, nombre, descripcion, estado) VALUES
(7, 'A001', 'COLERA DEBIDO A VIBRIO CHOLERAE O1, BIOTIPO EL TOR', 1),
(7, 'A009', 'COLERA NO ESPECIFICADO', 1),
(7, 'A010', 'FIEBRE TIFOIDEA', 1),
(7, 'A011', 'FIEBRE PARATIFOIDEA A', 1),
(7, 'A012', 'FIEBRE PARATIFOIDEA B', 1);

-- Ejemplo 3: Insertar con caracteres especiales (escapados)
INSERT INTO parametro_hijo (parametro_id, nombre, descripcion, estado) VALUES
(7, 'A029', 'INFECCIÓN DEBIDA A SALMONELLA NO ESPECIFICADA', 1);

-- =====================================================
-- CONSULTAS DE VERIFICACION
-- =====================================================

-- Verificar total de diagnosticos
SELECT COUNT(*) as total_diagnosticos FROM parametro_hijo WHERE parametro_id = 7;

-- Mostrar algunos ejemplos
SELECT id_parametrohijo, nombre, descripcion, estado 
FROM parametro_hijo 
WHERE parametro_id = 7 
ORDER BY id_parametrohijo DESC 
LIMIT 10;

-- Buscar un diagnostico especifico
SELECT * FROM parametro_hijo WHERE parametro_id = 7 AND nombre = 'A000';

-- Buscar diagnosticos que contengan una palabra
SELECT * FROM parametro_hijo WHERE parametro_id = 7 AND descripcion LIKE '%COLERA%';

-- Verificar estructura de la tabla
DESCRIBE parametro_hijo;

-- =====================================================
-- COMANDOS DE LIMPIEZA (OPCIONAL)
-- =====================================================

-- Eliminar todos los diagnosticos (CUIDADO: Esto borra todos los registros)
-- DELETE FROM parametro_hijo WHERE parametro_id = 7;

-- Eliminar un diagnostico especifico
-- DELETE FROM parametro_hijo WHERE parametro_id = 7 AND nombre = 'A000';
