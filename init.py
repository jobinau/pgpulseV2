#!/usr/bin/python
import sys,os,psycopg2
try:
  import json
except ImportError:
  import simplejson as json

#############GLOBAL VARIABLES#############
version="2.1"
cmdargs = sys.argv
#######################################

def print_version():
	print("pgPulse Version: " + version)

def getTableDDL(connSourceDB,tabName):
    try:
        print("DDL for " + tabName)
        cur=connSourceDB.cursor()
        cur.execute("SELECT column_name, data_type, is_nullable from information_schema.columns WHERE table_name = \'"+ tabName +"\';")
        if cur.rowcount < 1 :
            print("Unable to get DDL for " + tabName)
            return
        strDDL = ""
        for rec in cur:
            strDDL = strDDL + '\n'+rec[0]+ ' ' + rec[1] + ','
        strDDL = strDDL[:-1]
        return strDDL
    except psycopg2.Error:
        print("Unable to get DDL for table :"+ tabName)

def createSnapshotSchemaFromSourceDB(connRepoDB,connSourceDB,schemaName):
    try:
        cursor2=connRepoDB.cursor()
        cursor2.execute("create schema " + schemaName +";")
        cursor2.execute("create table " + schemaName +".snap (snap_id serial,dttm timestamp with time zone)")
        cursor2.execute("create table " + schemaName +".snap_stat_activity (snap_id int,dttm timestamp with time zone," + getTableDDL(connSourceDB,"pg_stat_activity") + ')')
        cursor2.execute("create table " + schemaName +".snap_user_tables (snap_id int,dttm timestamp with time zone," + getTableDDL(connSourceDB,"pg_stat_user_tables") + ',totalrelsize bigint)')
        cursor2.execute("create table " + schemaName +".snap_pg_locks(snap_id int,dttm timestamp with time zone," + getTableDDL(connSourceDB,"pg_locks") + ')' )
        cursor2.execute("create table " + schemaName +".snap_indexes (snap_id int,dttm timestamp with time zone," + getTableDDL(connSourceDB,"pg_stat_user_indexes") + ')')
        #print("create table " + schemaName +".snap_databases (snap_id int,dttm timestamp with time zone," + getTableDDL(connSourceDB,"pg_stat_database") + ')')
        cursor2.execute("create table " + schemaName +".snap_databases (snap_id int,dttm timestamp with time zone," + getTableDDL(connSourceDB,"pg_stat_database") + ')' )
        cursor2.execute("create table " + schemaName +".snap_settings (snap_id int,dttm timestamp with time zone,name text, setting text)")
        if getTableDDL(connSourceDB,"pg_stat_statements") is not None:
            cursor2.execute("create table " + schemaName +".snap_stat_statements (snap_id int,dttm timestamp with time zone," + getTableDDL(connSourceDB,"pg_stat_statements") + ')' )
        else:
            print("IMPORTANT NOTE: Appears that there is no pg_stat_statements. so skipping..")
            print("if you need to capture pg_stat_statements, \n 1. make sure that extension is present")
            print(" 2. DROP SCHEMA "+schemaName+" CASCADE;\n 3.Rerun this script again")
        cursor2.execute("create index idx_snap_user_tables_snap_id on " + schemaName +".snap_user_tables(snap_id)" )
        cursor2.execute("COMMIT;")
        cursor2.close()
    except psycopg2.Error:
        print("Unable to create Schema \n Schema for repository could be already existing. So skipping...")

def generatepgPulse(connSourceDB,cfg,outfile):
    print("Generating script \"" + outfile + "\" which can be scheduled for data collection...")
    outFile = os.fdopen(os.open(outfile,os.O_CREAT|os.O_WRONLY,511), 'w')
    outFile.write('#!/usr/bin/python')
    outFile.write('\n###### pgPulse #####')
    outFile.write('\n###This is the final pgPulse script generated with specific sourceDB and repoDB')
    outFile.write('\n###This can be scheduled for periodic data collection')
    outFile.write('\n##########')
    outFile.write('\nconnStrSourceDB=\"'+ 'host=' + cfg['sourceDB']['host'] + ' user=' + cfg['sourceDB']['user'] + ' password=' + cfg['sourceDB']['passwd'] + ' port=' + cfg['sourceDB']['port'] + ' dbname='+ cfg['sourceDB']['db'] + '\"')
    outFile.write('\nconnStrRepoDB=\"'+ 'host=' + cfg['repoDB']['host'] + ' user=' + cfg['repoDB']['user'] + ' password=' + cfg['repoDB']['passwd'] + ' port=' + cfg['repoDB']['port'] + ' dbname='+ cfg['repoDB']['db'] + '\"')
    outFile.write('\nschemaStrRepoDB=\"'+ cfg['repoDB']['schema']+'\"\n')
    stubFile = open("pgPulsestub.py")
    ##discard first 2 lines
    lineNum=0
    for line in stubFile.readlines():
        lineNum += 1
	if lineNum > 2:
		outFile.write(line)
    outFile.close()
    print("Script generation completed.")

if __name__ == "__main__":
### main() function. Program execution starts from here
    print_version()

if len(cmdargs)== 5 and cmdargs[1] == '--config' and cmdargs[3] == '--outfile' :
    configfile=cmdargs[2]
####Parse the configuration file
    sys.stdout.write("Checking and parsing specified configuration file \"" +configfile+ "\"...")
    try:
        cfg = json.load(open(configfile))
    except ValueError:
        print("Invalid configuration file")
        print(ValueError)
        sys.exit()
    print("OK")
####Connect to the Source database, from where snaps need to be collected
    sys.stdout.write("Connecting to source database...")
    try:
        connSourceDB = psycopg2.connect("host=" + cfg['sourceDB']['host'] + " user=" + cfg['sourceDB']['user'] + " password=" + cfg['sourceDB']['passwd'] + " port=" + cfg['sourceDB']['port'] + " dbname="+ cfg['sourceDB']['db'])
    except psycopg2.Error:
        print("Unable to establish connection to sourceDB")
        sys.exit()
    print("OK")

####Connect to Repository database, where snapshots are to be stored
    sys.stdout.write("Connecting to repository database instance...")
    try:
        connRepoDB = psycopg2.connect("host=" + cfg['repoDB']['host'] + " user=" + cfg['repoDB']['user'] + " password=" + cfg['repoDB']['passwd'] + " port=" + cfg['repoDB']['port'] )
    except psycopg2.Error:
        print("Unable to establish connection to repoDB instance.")
	sys.exit()
    print("OK")
    sys.stdout.write("Checking whethether Repository database : " + cfg['repoDB']['db'] + " exists ...")
    connRepoDB.set_isolation_level(0)
    cur = connRepoDB.cursor()
    cur.execute("select count(1) as count from pg_stat_database where datname = '"+ cfg['repoDB']['db'] + "'")
    for i in cur.fetchone():
        if i == 1:
            print ("Database \""+ cfg['repoDB']['db'] + "\" to Store Snapshots already exists. Trying to connect to that...")
        elif i == 0:
            cur.execute("create database "+ cfg['repoDB']['db'] +";")
            print ("Database to Store Snapshots does not exist. Creating the Database : "+ cfg['repoDB']['db'])
            cur.close()
    connRepoDB.close()
    connRepoDB = psycopg2.connect("host=" + cfg['repoDB']['host'] + " user=" + cfg['repoDB']['user'] + " password=" + cfg['repoDB']['passwd'] + " port=" + cfg['repoDB']['port'] + " dbname="+ cfg['repoDB']['db'] )
    createSnapshotSchemaFromSourceDB(connRepoDB,connSourceDB,cfg['repoDB']['schema'])
    generatepgPulse(connSourceDB,cfg,cmdargs[4])
    print("init completed .. SUCCESS")
else:
    print("USAGE : ./init.py --config databaseconfig.json --outfile pgPulseFinal.py")
