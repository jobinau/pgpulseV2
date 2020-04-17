
#pgPulse
pgPulse is a database performance snapshoting tool to capture database performance and sizeing related information available within the database

Historical performance information can be maintained in same or remote database. These historical performace and sizing data can be used for analysis purpose.

#History
 This repository is a fork of original pgpluse repository of Avinash Vallarapu. Which is again inspired by other projects like PgOn (Openwatch)

This is an effort to modernize code base and consolidate different scripts which are already existing to address the similar problem.
As of now, code is diverged so from the upstream.
Master  Repo: https://bitbucket.org/jobinau/pgpulse-v2
Upstream Repo : https://bitbucket.org/avinash_vallarapu/pgpulse

##Features
* Fully developed in Python for portability
* configuration file in JSON format
* External configuration file allows scheduling against different databases.

##V2 improvements
* Only external package to be installed is psycopg2 on most of the Linux environments.
* Proper error handing and messages
* Highly optimized, light weight code for scheduling
* Works with all versions of PostgreSQL from Version 8.2
* Works with all Python version 2.4 onwards
* Optional psql only implimentation (No need of python atall)

##Setup
* Git Clone will create a pgpulse directory
* Edit configuration file (databaseconfig.json)  to have database credentials or create another json file with same format.
* Run for setting up pre requirements

        ./init.py  --config databaseconfig.json --outfile pgPulse_TestDB.py

    This will connect to repository database and create schema as specified in the configuration file.
    This will generate and output file as specified. in this case it is pgPulse_TestDB.py

##Notes:
* For very old python versions like 2.4, simplejson module need to be installed
* A quick presentation and demo is available : https://youtu.be/BJVaKhWW18M ( Demo starts from 2:17 )