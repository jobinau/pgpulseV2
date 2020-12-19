\pset tuples_only
\echo '\\t'
\echo '\\r'
\echo COPY pg_get_activity (datid, pid ,usesysid ,application_name ,state ,query ,wait_event_type ,wait_event ,xact_start ,query_start ,backend_start ,state_change ,client_addr, client_hostname, client_port, backend_xid ,backend_xmin, backend_type,ssl ,sslversion ,sslcipher ,sslbits ,sslcompression ,ssl_client_dn ,ssl_client_serial,ssl_issuer_dn ,gss_auth ,gss_princ ,gss_enc) FROM stdin;
\copy (select * from  pg_stat_get_activity(NULL) where pid != pg_backend_pid()) to stdin
\echo '\\.'
--Following works individually
--SELECT pg_sleep(1); SELECT 'INSERT INTO pg_get_wait VALUES ('|| pid ||','|| CASE WHEN wait_event IS NULL THEN 'NULL);' ELSE '''' ||  wait_event ||''');' END from pg_stat_activity where state != 'idle';
--Wrapping for 10 times executoin
SELECT 'SELECT pg_sleep(1);  SELECT ''INSERT INTO pg_get_wait VALUES (''|| pid || '','' || CASE WHEN wait_event IS NULL THEN ''NULL);'' ELSE ''''''''|| wait_event ||'''''');'' END  FROM pg_stat_activity WHERE state != ''idle'';' FROM generate_series(1,10);
\gexec
--Ideas to try. Try writing to a seperate output file and run it here again
--If not possible, develop a clean up script using sed