\echo COPY pg_get_activity (datid, pid ,usesysid ,application_name ,state ,query ,wait_event_type ,wait_event ,xact_start ,query_start ,backend_start ,state_change ,client_addr, client_hostname, client_port, backend_xid ,backend_xmin, backend_type,ssl ,sslversion ,sslcipher ,sslbits ,sslcompression ,ssl_client_dn ,ssl_client_serial,ssl_issuer_dn ,gss_auth ,gss_princ ,gss_enc) FROM stdin;
\copy (select * from  pg_stat_get_activity(NULL) where pid != pg_backend_pid()) to stdin
\echo '\\.'
