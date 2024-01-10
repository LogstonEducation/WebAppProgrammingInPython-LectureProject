#!/usr/bin/env bash

# Exit on error.
set -o errexit

# Install reqs as usual.
pip install -r requirements.txt

# Run migrations if needed.
python manage.py migrate

# Add django admin user if not exists.
cat <<EOF | python manage.py shell
from django.contrib.auth.models import User

username = (os.environ.get('SU_USERNAME') or '').lower()
email = (os.environ.get('SU_EMAIL') or '').lower()
password = (os.environ.get('SU_PASSWORD') or '').lower()

if not User.objects.filter(username=username):
    User.objects.create_superuser(username, email, password)
EOF