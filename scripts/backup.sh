#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python manage.py backup
printf 'PENTING: salin backup ke server lain / storage aman secara rutin.\n'
