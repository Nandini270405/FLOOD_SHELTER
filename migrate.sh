#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting database migration..."

# Set FLASK_APP and FLASK_ENV for the migration command
export FLASK_APP=app.py
export FLASK_ENV=production

# Run database upgrade
python -m flask db upgrade

echo "Database migration finished."