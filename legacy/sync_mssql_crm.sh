#!/bin/bash
# --
# sync_mssql_crm.sh - sync script to sync ms crm based on mssql with otrs customer_user
# Copyright 2011 SECTOR NORD AG
# Joerg Folckers, 2011-10-20
# --
# 2016_08_08, studo
# /opt/otrs/scripts/tools/sync_mssql_crm.sh --sync

PROGNAME=`basename $0`
VERSION="1.0.0"

if [ "$1" != "--sync" ] ;  then
  echo "["$(date +"%F %T")"] $PROGNAME: Parameter --sync missing"
  exit 1
fi

# --
# global settings for db access etc
# --

STAMP=$(date +"%s")

DUMP_OUT="/tmp/crm_otrs_dump-"$STAMP".csv"
DUMP_ERR="/tmp/crm_otrs_dump-"$STAMP".err"

SEPARATOR=";"

CRM_SERVER="MSSQL-CRM"
CRM_USER="SECTORNORD\\ldapreaduser"
CRM_PWD="86QLBo3%"
CRM_TABLE="Sector_Nord_AG_MSCRM.dbo.OTRSCustomerContact"

OTRS_USER="root"
OTRS_PWD="sector"
OTRS_TABLE="otrs.customer_user_crm"

# --
# start main 
# --

echo "["$(date +"%F %T")"] $PROGNAME: starting"

# --
# retrieve data from crm 
# --

#echo "select * from $CRM_TABLE;\ngo" | isql "$CRM_SERVER" "$CRM_USER" "$CRM_PWD" -b -x0x09 -c 
locale
export LC_CTYPE=de_DE.UTF-8

export LANG=POSIX
export LC_CTYPE=de_DE.UTF-8
LC_CTYPE=de_DE.UTF-8
locale

echo -e "SELECT * FROM $CRM_TABLE;\ngo\n" | tsql -S "$CRM_SERVER"  -U "$CRM_USER" -P "$CRM_PWD" -t "$SEPARATOR" -o qf >$DUMP_OUT 2>$DUMP_ERR

RETURN_CODE=$?

# --
# check for bad return code
# --

if [ $RETURN_CODE -ne 0 ] ; then
  echo "["$(date +"%F %T")"] $PROGNAME: Error retrieving data from crm ($RETURN_CODE)"
  cat $DUMP_ERR
  /bin/rm -f $DUMP_ERR
  /bin/rm -f $DUMP_OUT
  echo "["$(date +"%F %T")"] $PROGNAME: exiting"
  exit 1
fi

# --
# check for empty data 
# --

LINES=`cat $DUMP_OUT | wc -l`
if [ "$LINES" -le "1" ] ; then
  echo "["$(date +"%F %T")"] $PROGNAME: Error only $LINES lines found"
  /bin/rm -f $DUMP_ERR
  /bin/rm -f $DUMP_OUT
  echo "["$(date +"%F %T")"] $PROGNAME: exiting"
  exit 1
fi

LINES=$(($LINES - 1))

echo "["$(date +"%F %T")"] $PROGNAME: $LINES (+1) lines found"

# --
# extract the columns on the first line 
# the column names on line 1 are: 
# "Address1_City;Address1_Country;Address1_Line1;Address1_PostalCode;Name;AccountNumber;WebSiteURL;FirstName;Salutation;LastName;EMailAddress1;Department;Telephone1;Telephone2;Fax;MobilePhone;AccountRoleCode;AccountId;CustomerTypeCode;Expr1;ContactId;JobTitle;OwnerId;Owner"
# --

COLUMNS=$(head -1 $DUMP_OUT)
COLUMNS=${COLUMNS//$SEPARATOR/, }
#echo "["$(date +"%F %T")"] $PROGNAME: Columns are \"$COLUMNS\""

# --
# insert data into mysql  
# --

chmod a+r $DUMP_OUT

FIELD_ENCLOSE="\""
FIELD_ESCAPE='\\\\'

### echo "TRUNCATE TABLE $OTRS_TABLE; LOAD DATA INFILE '$DUMP_OUT' INTO TABLE $OTRS_TABLE CHARACTER SET utf8 FIELDS TERMINATED BY '$SEPARATOR' OPTIONALLY ENCLOSED BY '$FIELD_ENCLOSE' ESCAPED BY '$FIELD_ESCAPE' IGNORE 1 LINES ($COLUMNS); SELECT COUNT(*) AS amount FROM $OTRS_TABLE;" 
MYSQLOUT=$(echo -e "TRUNCATE TABLE $OTRS_TABLE; LOAD DATA INFILE '$DUMP_OUT' INTO TABLE $OTRS_TABLE CHARACTER SET utf8 FIELDS TERMINATED BY '$SEPARATOR' OPTIONALLY ENCLOSED BY '$FIELD_ENCLOSE' ESCAPED BY '$FIELD_ESCAPE' IGNORE 1 LINES ($COLUMNS); SELECT COUNT(*) AS amount FROM $OTRS_TABLE;" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )

RETURN_CODE=$?

# --
# check for bad return code
# --

if [ $RETURN_CODE -ne 0 ] ; then
  echo "["$(date +"%F %T")"] $PROGNAME: Error inserting data into otrs ($RETURN_CODE)"
  cat $DUMP_ERR
  /bin/rm -f $DUMP_ERR
  /bin/rm -f $DUMP_OUT
  echo "["$(date +"%F %T")"] $PROGNAME: exiting"
  exit 1
fi

# --
# check for invalid amount of inserted data 
# --

MYSQLOUT=$(echo $MYSQLOUT)
FOUND=${MYSQLOUT//amount /}

if [ "$LINES" != "$FOUND" ] ; then
  echo "["$(date +"%F %T")"] $PROGNAME: Error only $FOUND lines instead of $LINES lines inserted"
  /bin/rm -f $DUMP_ERR
  /bin/rm -f $DUMP_OUT
  echo "["$(date +"%F %T")"] $PROGNAME: exiting"
  exit 1
fi

echo "["$(date +"%F %T")"] $PROGNAME: all $FOUND lines successfully inserted"

# --
# Christopher Kreft - Convert telephone numbers to into valid style +49441290101042
# --

echo "["$(date +"%F %T")"] $PROGNAME: Converting telephone numbers to into valid style"
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone1 = REPLACE(Telephone1,' ','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone1 = REPLACE(Telephone1,'(','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone1 = REPLACE(Telephone1,')','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone1 = REPLACE(Telephone1,'/','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone1 = REPLACE(Telephone1,'–','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone1 = REPLACE(Telephone1,'-','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone1 = REPLACE(Telephone1,'.','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone1 = REPLACE(Telephone1,'[','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone1 = REPLACE(Telephone1,']','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )

MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone2 = REPLACE(Telephone2,' ','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone2 = REPLACE(Telephone2,'(','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone2 = REPLACE(Telephone2,')','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone2 = REPLACE(Telephone2,'/','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone2 = REPLACE(Telephone2,'–','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone2 = REPLACE(Telephone2,'-','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone2 = REPLACE(Telephone2,'.','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone2 = REPLACE(Telephone2,'[','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone2 = REPLACE(Telephone2,']','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )

MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET MobilePhone = REPLACE(MobilePhone,' ','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET MobilePhone = REPLACE(MobilePhone,'(','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET MobilePhone = REPLACE(MobilePhone,')','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET MobilePhone = REPLACE(MobilePhone,'/','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET MobilePhone = REPLACE(MobilePhone,'–','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET MobilePhone = REPLACE(MobilePhone,'-','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET MobilePhone = REPLACE(MobilePhone,'.','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET MobilePhone = REPLACE(MobilePhone,'[','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET MobilePhone = REPLACE(MobilePhone,']','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )

MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Fax = REPLACE(Fax,' ','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Fax = REPLACE(Fax,'(','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Fax = REPLACE(Fax,')','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Fax = REPLACE(Fax,'/','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Fax = REPLACE(Fax,'–','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Fax = REPLACE(Fax,'-','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Fax = REPLACE(Fax,'.','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Fax = REPLACE(Fax,'[','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Fax = REPLACE(Fax,']','');" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )

MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone1 = CONCAT('+49',SUBSTRING(Telephone1 FROM 2)) WHERE SUBSTRING(Telephone1,1,1) = '0';" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Telephone2 = CONCAT('+49',SUBSTRING(Telephone2 FROM 2)) WHERE SUBSTRING(Telephone2,1,1) = '0';" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET MobilePhone = CONCAT('+49',SUBSTRING(MobilePhone FROM 2)) WHERE SUBSTRING(MobilePhone,1,1) = '0';" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )
MYSQLOUT=$(echo -e "UPDATE $OTRS_TABLE SET Fax = CONCAT('+49',SUBSTRING(Fax FROM 2)) WHERE SUBSTRING(Fax,1,1) = '0';" | mysql --user=$OTRS_USER --password=$OTRS_PWD 2>$DUMP_ERR )

echo "["$(date +"%F %T")"] $PROGNAME: done"

#/bin/rm -f $DUMP_ERR
#/bin/rm -f $DUMP_OUT

exit 0

# --
# END
# --
