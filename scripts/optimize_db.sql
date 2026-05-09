-- ChaloGhumo Postgres Optimization & Maintenance Script
-- Recommended Execution: Once per week or after major data refreshes

-- 1. Update statistics for the query planner
ANALYZE destinations;

-- 2. Reclaim storage space from updated or deleted rows
-- Note: VACUUM FULL locks the table, plain VACUUM does not.
VACUUM destinations;

-- 3. Rebuild indices to ensure peak performance
REINDEX TABLE destinations;

-- 4. Check for duplicate records (Sanity Check)
SELECT iata_code, count(*) 
FROM destinations 
GROUP BY iata_code 
HAVING count(*) > 1;

-- 5. Monitor Table Size
SELECT pg_size_pretty(pg_total_relation_size('destinations')) AS total_size;
