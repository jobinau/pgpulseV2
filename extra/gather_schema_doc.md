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
```
CREATE TABLE pg_get_wait(
    itr integer,
    pid integer,
    wait_event text
);
```
```
SELECT 'SELECT pg_sleep(1); SELECT ''INSERT INTO pg_get_wait VALUES ('''''|| now()||''''');'';';
```
```
SELECT 'SELECT pg_sleep(1); SELECT ''INSERT INTO pg_get_wait VALUES ('''''||COPY (select pid,wait_event from pg_stat_activity where state != 'idle') TO stdin with CSV FORCE QUOTE wait_event  DELIMITER ',' NULL 'NULL'||''''');'';';
COPY (select pid,wait_event from pg_stat_activity where state != 'idle') TO stdin with CSV FORCE QUOTE wait_event  DELIMITER ',' NULL 'NULL'
```
```
CREATE TABLE pg_get_db (
    datid oid,
    datname text,
    xact_commit bigint,
    xact_rollback bigint,
    blks_fetch bigint,
    blks_hit bigint,
    tup_returned bigint,
    tup_fetched bigint,
    tup_inserted bigint,
    tup_updated bigint,
    tup_deleted bigint,
    temp_files bigint,
    temp_bytes bigint,
    deadlocks bigint,
    blk_read_time double precision,
    blk_write_time double precision,
    db_size bigint
);

cleanup output using sed
```
sed -i '/^Pager/d; /^Tuples/d; /^Output/d; /^SELECT/d' out.txt
``` 
