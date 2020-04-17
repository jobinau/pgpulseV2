#!/usr/bin/python
from lib.devheader import *
strQryPgSettings="select now() as dttm, name,setting from pg_settings"
strQryPgStatStatements="select now() as dttm,* from pg_stat_statements"
strQryPgStatTables="select now() AS dttm , * , pg_total_relation_size(relid::regclass) as totalrelsize from pg_stat_user_tables"
strQryStatIndexes="select now()as dttm, * from pg_stat_user_indexes"
strQryPgLocks="select now()as dttm , * from pg_locks"
strQryPgActivity="select now()as dttm , * from pg_stat_activity"
strQryPgStatDatabase="select now()as dttm, * from pg_stat_database"
import sys,psycopg2
version="2.1"
Snap=1   ##No meaning for value, just a global varible

############################# 2 helper functions ##############################
def addSnapId(rows):
    for idx,tup in enumerate(rows):
        rows[idx] = (Snap,) + tup
    return rows

def copyData (connSourceDB,connRepoDB,repoTableName,queryStr):
  print("Copying to " + repoTableName + "...")
  curSource = connSourceDB.cursor()
  curSource.execute(queryStr)
  curRepo = connRepoDB.cursor()
  fieldListStr = "snap_id,"
  for i in range(0, len(curSource.description)):
      fieldListStr = fieldListStr + curSource.description[i][0] + ","
  fieldListStr = fieldListStr[:-1]
  strSql = 'INSERT INTO ' + repoTableName + '(' + fieldListStr + ') VALUES (' + ('%s,'*(len(curSource.description)+1))[:-1] + ')'
  rows = curSource.fetchmany(10000)
  while rows:
        rows = addSnapId(rows)
        curRepo.executemany(strSql,rows)
        curRepo.execute("COMMIT")
        sys.stdout.write(".")
        sys.stdout.flush()
        try:
           rows = curSource.fetchmany(10000)
        except:
           rows = None
  curRepo.execute("COMMIT")

################# MAIN SECTION. PROGRAM STARTS HERE ##############################
if __name__ == "__main__":
#### Connect to the Source database, from where snaps need to be collected
    print("Connecting to source database...")
    try:
        connSourceDB = psycopg2.connect(connStrSourceDB)
    except psycopg2.Error:
        print("Unable to establish connection to sourceDB")
    print("OK")
#### Connect to Repository database, where snapshots are to be stored
    print("Connecting to repository database...")
    try:
        connRepoDB = psycopg2.connect(connStrRepoDB)
    except psycopg2.Error:
        print("Unable to establish connection to repoDB")
    print("OK")
############ Generate Snap id ################################
    curRepo = connRepoDB.cursor()
    curRepo.execute("INSERT INTO " + schemaStrRepoDB +".snap (dttm) VALUES (now()) RETURNING snap_id")
    Snap=curRepo.fetchone()[0]
    curRepo.execute("COMMIT")
    curRepo.close()
############## Copy snaps to RepoDB, you can delete anything you don't want ########################
    copyData(connSourceDB,connRepoDB,schemaStrRepoDB+".snap_settings",strQryPgSettings)
    copyData(connSourceDB,connRepoDB,schemaStrRepoDB+".snap_user_tables",strQryPgStatTables)
    copyData(connSourceDB,connRepoDB,schemaStrRepoDB+".snap_indexes",strQryStatIndexes)
    copyData(connSourceDB,connRepoDB,schemaStrRepoDB+".snap_pg_locks",strQryPgLocks)
    copyData(connSourceDB,connRepoDB,schemaStrRepoDB+".snap_stat_activity",strQryPgActivity)
    copyData(connSourceDB,connRepoDB,schemaStrRepoDB+".snap_databases",strQryPgStatDatabase)
    copyData(connSourceDB,connRepoDB,schemaStrRepoDB+".snap_stat_statements",strQryPgStatStatements)
