-- Script para eliminar privilegios especiales de nebulosa
-- Ejecutar este script en las bases de datos correspondientes

-- 1. En rights.db: Eliminar nebulosa de roles de admin (si existe)
-- DELETE FROM roles WHERE username = 'nebulosa';

-- 2. En rights.db: Eliminar nebulosa de opo_players (si existe como privilegiado)
-- DELETE FROM opo_players WHERE username = 'nebulosa' AND added_by = 'dvd';

-- 3. Verificar que nebulosa existe como usuario normal en users.db
-- Si quieres mantenerla como usuario normal, no elimines de users
-- Si quieres eliminarla completamente, descomenta las siguientes líneas:

-- En users.db:
-- DELETE FROM users WHERE username = 'nebulosa';

-- En transactions.db:
-- DELETE FROM transactions WHERE from_user = 'nebulosa' OR to_user = 'nebulosa';

-- En stats.db:
-- DELETE FROM sessions WHERE username = 'nebulosa';

-- En opo.db:
-- DELETE FROM opo_results WHERE username = 'nebulosa';
-- DELETE FROM opo_sessions WHERE username = 'nebulosa';

-- NOTA: Este script está comentado por seguridad.
-- Descomenta solo las líneas que necesites ejecutar.
