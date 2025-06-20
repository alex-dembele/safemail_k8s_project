#!/bin/bash
set -e

export MYSQL_HOST=$NXH_DATABASE_HOST
export MYSQL_PORT=$NXH_DATABASE_PORT
export MYSQL_NAME=$NXH_DATABASE_NAME
export MYSQL_USER=$NXH_DATABASE_USER
export MYSQL_PASSWORD=$NXH_DATABASE_PASSWORD

if [ -z "$MYSQL_HOST" ]; then echo "NXH_DATABASE_HOST is not set"; exit 1; fi

envsubst < /tmp/conf/dovecot.conf.template > /etc/dovecot/dovecot.conf
envsubst < /tmp/conf/dovecot-sql.conf.ext.template > /etc/dovecot/dovecot-sql.conf.ext

exec "$@"
