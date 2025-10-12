SSR_PATH=/opt/sqlbot/g2-ssr
APP_PATH=/opt/sqlbot/app

# Initialize PostgreSQL if not already initialized
if [ ! -d "/var/lib/postgresql/data/base" ]; then
    echo "Initializing PostgreSQL cluster..."
    mkdir -p /var/lib/postgresql/data
    chown -R postgres:postgres /var/lib/postgresql
    su - postgres -c "/usr/lib/postgresql/*/bin/initdb -D /var/lib/postgresql/data"

    # Configure PostgreSQL
    echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf
    echo "listen_addresses = '*'" >> /var/lib/postgresql/data/postgresql.conf
fi

# Start internal PostgreSQL
su - postgres -c "/usr/lib/postgresql/*/bin/pg_ctl -D /var/lib/postgresql/data -l /var/lib/postgresql/data/logfile start"
echo -e "\033[1;32mPostgreSQL started.\033[0m"

# Wait for PostgreSQL to be ready
wait-for-it 127.0.0.1:5432 --timeout=120 --strict -- echo -e "\033[1;32mPostgreSQL is ready.\033[0m"

# Create database and user if first time
su - postgres -c "psql -lqt | cut -d \| -f 1 | grep -qw ${POSTGRES_DB}" || \
su - postgres -c "psql -c \"CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}' SUPERUSER;\" && \
                   psql -c \"CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};\""

nohup node $SSR_PATH/app.js &

nohup uvicorn main:mcp_app --host 0.0.0.0 --port 8001 &

cd $APP_PATH
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 --proxy-headers
