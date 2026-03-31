-- ============================================================
-- Índices recomendados para mef.gasto_anual
-- Ejecutar en PostgreSQL con permisos de DBA.
-- Los índices se crean con CONCURRENTLY para no bloquear la tabla.
-- ============================================================

-- Año de ejecución (filtro principal en casi todas las consultas)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_ano_eje
    ON mef.gasto_anual (ano_eje);

-- Geografía ejecutora (filtro de ubigeo)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_geo_ejecutora
    ON mef.gasto_anual (departamento_ejecutora, provincia_ejecutora, distrito_ejecutora);

-- Tipo actividad/proyecto
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_tipo_act_proy
    ON mef.gasto_anual (tipo_act_proy);

-- Nivel de gobierno (drill-down nivel)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_nivel_gobierno
    ON mef.gasto_anual (nivel_gobierno);

-- Sector (drill-down sector)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_sector
    ON mef.gasto_anual (sector);

-- Pliego (drill-down pliego)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_pliego
    ON mef.gasto_anual (pliego);

-- Ejecutora (drill-down ejecutora)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_sec_ejec
    ON mef.gasto_anual (sec_ejec);

-- Función y programa presupuestal (dropdowns de filtros)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_funcion
    ON mef.gasto_anual (funcion);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_programa_ppto
    ON mef.gasto_anual (programa_ppto);

-- Índice compuesto para la consulta más frecuente:
-- año + geografía + tipo de actividad
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_main_query
    ON mef.gasto_anual (ano_eje, departamento_ejecutora, provincia_ejecutora, tipo_act_proy);

-- Producto/proyecto (búsqueda por nombre de proyecto)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_producto_proyecto
    ON mef.gasto_anual (producto_proyecto);

-- Búsqueda por nombre de proyecto (ILIKE '%texto%')
-- Requiere extensión pg_trgm
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_producto_nombre_trgm
    ON mef.gasto_anual USING GIN (producto_proyecto_nombre gin_trgm_ops);

-- Gráficos históricos (ano_eje >= 2012)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ga_historico
    ON mef.gasto_anual (ano_eje, departamento_ejecutora, tipo_act_proy, nivel_gobierno)
    WHERE ano_eje >= 2012;

-- ============================================================
-- Verificar índices creados:
-- SELECT indexname, indexdef FROM pg_indexes
-- WHERE schemaname = 'ide' AND tablename = 'gasto_anual';
-- ============================================================
