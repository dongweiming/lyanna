#/bin/sh

# Init DB
python manage.py initdb
# Create default superuser
python manage.py adduser --name admin --password admin123 --email admin@admin.com
