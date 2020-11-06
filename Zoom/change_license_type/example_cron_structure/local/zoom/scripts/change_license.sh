#!/bin/bash
BASEDIR=/local/zoom
echo "Finding non-basic users not logged in for 90 days"
python3 ${BASEDIR}/libexec/change_license_type.py \
    -e 90 -c ${BASEDIR}/work/current.csv \
    -j ${BASEDIR}/conf/config.json

echo "Converting users found above to basic users"
if [ $? -eq 0 ];then
    python3 ${BASEDIR}/libexec/change_license_type.py \
        -a -b -f ${BASEDIR}/work/current.csv \
        -j ${BASEDIR}/conf/config.json
fi

rm ${BASEDIR}/work/current.csv
