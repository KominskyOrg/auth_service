#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Assign environment variables with default values
readonly DB_HOST="${DB_HOST:-db}"
readonly DB_PORT="${DB_PORT:-3306}"
readonly DB_NAME="${DB_NAME:-auth_service}"
readonly DB_USER="${DB_USER:-auth_user}"
readonly DB_PASSWORD="${DB_PASSWORD:-password}"

# Function to wait for the MySQL database to be ready
wait_for_db() {
    echo "Waiting for MySQL database to be ready at ${DB_HOST}:${DB_PORT}..."
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        sleep 1
        echo -n "."
    done
    echo ""
    echo "MySQL database is up and running!"
}

# Function to run Alembic migrations using Flask-Migrate
run_migrations() {
    echo "Running Alembic migrations..."
    flask db upgrade
    echo "Alembic migrations completed successfully."
}

# Function to backup the database (optional)
backup_database() {
    if [ "$FLASK_ENV" = "production" ]; then
        echo "Backing up the production database..."
        mysqldump -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" > /backups/"$DB_NAME"_$(date +%F_%T).sql
        echo "Database backup completed."
    fi
}

# Wait for the database to be ready
wait_for_db

# Backup the database if in production
backup_database

# Run migrations
run_migrations

# Start the application
if [ "$FLASK_ENV" = "staging" ] || [ "$FLASK_ENV" = "production" ]; then
    echo "Starting uWSGI server..."
    exec uwsgi --ini uwsgi.ini
else
    echo "Starting Flask development server..."
    exec flask run --host=0.0.0.0 --port=5001 --reload
fi
