#!/bin/bash

BASEDIR=/local/zoom/conf

. ${BASEDIR}/post-install.conf

sed \
    -e "s,%%KEY%%,${jwt_key}," \
    -e "s,%%SECRET%%,${jwt_secret}," \
    ${BASEDIR}/config.json.in \
    > ${BASEDIR}/config.json
