#!/usr/bin/sh
################# pgPulse data collector as single shell script ######
# Strongly recommends pgBouncer for connection pooling for this script
#   Jan/2018
######################################################################

SOURCEDB="host=sourcedb.host port=5432 user=postgres password=vagrant  dbname=postgres"
REPODB="host=repdb.host port=5433 user=postgres password=password123  dbname=postgres"
schemaStrRepoDB="pulsesnaps"
PGHOME=$HOME/bigsql/pg96
PATH=$PATH:$PGHOME/bin
SNAP_ID=`psql "$REPODB" -A -c "insert into $schemaStrRepoDB.snap (dttm) values (now()) returning snap_id" | sed -n '2p'`
echo $SNAP_ID
psql "$SOURCEDB" -c "COPY (select $SNAP_ID,now() as dttm, name,setting from pg_settings) TO STDOUT" | psql "$REPODB" -c "COPY $schemaStrRepoDB.snap_settings FROM STDIN"
psql "$SOURCEDB" -c "COPY (select $SNAP_ID,now() as dttm, * , pg_total_relation_size(relid::regclass) as totalrelsize from pg_stat_user_tables) TO STDOUT" | psql "$REPODB" -c "COPY $schemaStrRepoDB.snap_user_tables FROM STDIN"
psql "$SOURCEDB" -c "COPY (select $SNAP_ID,now() as dttm, * from pg_stat_user_indexes) TO STDOUT" | psql "$REPODB" -c "COPY $schemaStrRepoDB.snap_indexes FROM STDIN"
psql "$SOURCEDB" -c "COPY (select $SNAP_ID,now() as dttm, * from pg_locks) TO STDOUT" | psql "$REPODB" -c "COPY $schemaStrRepoDB.snap_pg_locks FROM STDIN"
psql "$SOURCEDB" -c "COPY (select $SNAP_ID,now() as dttm, * from pg_stat_activity) TO STDOUT" | psql "$REPODB" -c "COPY $schemaStrRepoDB.snap_stat_activity FROM STDIN"
psql "$SOURCEDB" -c "COPY (select $SNAP_ID,now() as dttm, * from pg_stat_database) TO STDOUT" | psql "$REPODB" -c "COPY $schemaStrRepoDB.snap_databases FROM STDIN"
psql "$SOURCEDB" -c "COPY (select $SNAP_ID,now() as dttm, * from pg_stat_statements) TO STDOUT" | psql "$REPODB" -c "COPY $schemaStrRepoDB.snap_stat_statements FROM STDIN"
