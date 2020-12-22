---- Gather Performance Info Script
---- Version 1 for PG 12+ 

\pset tuples_only
\echo '\\t'
\echo '\\r'

\echo COPY pg_connction FROM stdin;
\conninfo
\echo '\\.'

\echo COPY pg_collection FROM stdin;
COPY (SELECT current_timestamp,current_user,current_database(),version(),pg_postmaster_start_time(),pg_is_in_recovery(),inet_client_addr(),inet_server_addr(),pg_conf_load_time() ) TO stdin;
\echo '\\.'

\echo COPY pg_get_activity (datid, pid ,usesysid ,application_name ,state ,query ,wait_event_type ,wait_event ,xact_start ,query_start ,backend_start ,state_change ,client_addr, client_hostname, client_port, backend_xid ,backend_xmin, backend_type,ssl ,sslversion ,sslcipher ,sslbits ,sslcompression ,ssl_client_dn ,ssl_client_serial,ssl_issuer_dn ,gss_auth ,gss_princ ,gss_enc) FROM stdin;
\copy (select * from  pg_stat_get_activity(NULL) where pid != pg_backend_pid()) to stdin
\echo '\\.'
\a

--INSERT statements
--SELECT 'SELECT pg_sleep(1);  SELECT ''INSERT INTO pg_get_wait VALUES (' || g ||',''|| pid || '','' || CASE WHEN wait_event IS NULL THEN ''NULL);'' ELSE ''''''''|| wait_event ||'''''');'' END  FROM pg_stat_activity WHERE state != ''idle'';' FROM generate_series(1,10) g;
--\gexec
\echo COPY pg_get_wait (itr,pid,wait_event) FROM stdin;
SELECT 'SELECT pg_sleep(1);  SELECT ''' || g ||'''||E''\t''|| pid || E''\t'' || CASE WHEN wait_event IS NULL THEN ''\N'' ELSE  wait_event END  FROM pg_stat_get_activity(NULL) WHERE state != ''idle'';' FROM generate_series(1,10) g;
\gexec
\echo '\\.'
\a
--Ideas to try. Try writing to a seperate output file and run it here again
--If not possible, develop a clean up script using sed

--Database level information
\echo COPY pg_get_db (datid,datname,xact_commit,xact_rollback,blks_fetch,blks_hit,tup_returned,tup_fetched,tup_inserted,tup_updated,tup_deleted,temp_files,temp_bytes,deadlocks,blk_read_time,blk_write_time,db_size) FROM stdin;
COPY (SELECT d.oid, d.datname, 
pg_stat_get_db_xact_commit(d.oid) AS xact_commit,
pg_stat_get_db_xact_rollback(d.oid) AS xact_rollback,
pg_stat_get_db_blocks_fetched(d.oid) AS blks_fetch,
pg_stat_get_db_blocks_hit(d.oid) AS blks_hit,
pg_stat_get_db_tuples_returned(d.oid) AS tup_returned,
pg_stat_get_db_tuples_fetched(d.oid) AS tup_fetched,
pg_stat_get_db_tuples_inserted(d.oid) AS tup_inserted,
pg_stat_get_db_tuples_updated(d.oid) AS tup_updated,
pg_stat_get_db_tuples_deleted(d.oid) AS tup_deleted,
pg_stat_get_db_temp_files(d.oid) AS temp_files,
pg_stat_get_db_temp_bytes(d.oid) AS temp_bytes,
pg_stat_get_db_deadlocks(d.oid) AS deadlocks,
pg_stat_get_db_blk_read_time(d.oid) AS blk_read_time,
pg_stat_get_db_blk_write_time(d.oid) AS blk_write_time,
pg_database_size(d.oid) AS db_size
FROM pg_database d) TO stdin;
\echo '\\.'

--pg_settings information
\echo COPY pg_get_confs (name,setting,unit,context) FROM stdin;
COPY ( SELECT name,setting,unit,context FROM pg_settings ) TO stdin;
\echo '\\.'

--Major tables and indexes in current schema
\echo COPY pg_get_class FROM stdin;
COPY (SELECT oid,relname,relkind,relnamespace FROM pg_class WHERE relnamespace NOT IN (SELECT oid FROM pg_namespace WHERE nspname like 'pg%_temp_%' OR nspname in ('pg_catalog','information_schema'))) TO stdin;
\echo '\\.'

--Index usage info
\echo COPY pg_get_index FROM stdin;
COPY (SELECT indexrelid,indrelid,indisunique,indisprimary, pg_stat_get_numscans(indexrelid) from pg_index) TO stdin;
\echo '\\.'

