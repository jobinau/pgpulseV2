Experimental schema for using with gather.sql v1
```
CREATE TABLE pg_get_activity (
datid oid, 
pid integer,
usesysid oid,
application_name text,
state text,
query text,
wait_event_type text,
wait_event text,
xact_start timestamp with time zone,
query_start timestamp with time zone,
backend_start timestamp with time zone,
state_change timestamp with time zone,
client_addr inet,
client_hostname text,
client_port integer,
backend_xid xid,
backend_xmin xid,
backend_type text,
ssl boolean,
sslversion text,
sslcipher text,
sslbits integer,
sslcompression boolean,
ssl_client_dn text,
ssl_client_serial numeric,
ssl_issuer_dn text,
gss_auth boolean,
gss_princ text,
gss_enc boolean
);
```
Test
```
INSERT INTO pg_get_activity SELECT * FROM pg_stat_get_activity(null);
```


