#!/bin/bash
set -e

# Mapper les variables d'environnement NXH_* vers celles attendues par les templates
export MYSQL_HOST=$NXH_DATABASE_HOST
export MYSQL_PORT=$NXH_DATABASE_PORT
export MYSQL_NAME=$NXH_DATABASE_NAME
export MYSQL_USER=$NXH_DATABASE_USER
export MYSQL_PASSWORD=$NXH_DATABASE_PASSWORD

if [ -z "$MYSQL_HOST" ] || [ -z "$MYSQL_USER" ] || [ -z "$MYSQL_PASSWORD" ] || [ -z "$MYSQL_NAME" ]; then
  echo "Erreur: Une ou plusieurs variables de base de données (NXH_DATABASE_*) ne sont pas définies."
  exit 1
fi

# Remplace les variables dans les templates et les place dans /etc/postfix
envsubst < /tmp/conf/main.cf.template > /etc/postfix/main.cf
envsubst < /tmp/conf/mysql-virtual-alias-maps.cf.template > /etc/postfix/mysql-virtual-alias-maps.cf
envsubst < /tmp/conf/mysql-virtual-mailbox-domains.cf.template > /etc/postfix/mysql-virtual-mailbox-domains.cf
envsubst < /tmp/conf/mysql-virtual-mailbox-maps.cf.template > /etc/postfix/mysql-virtual-mailbox-maps.cf

# Démarrer le service
exec "$@"
