SSR_PATH=/opt/sqlbot/g2-ssr
APP_PATH=/opt/sqlbot/app

# Wait for external PostgreSQL to be ready
wait-for-it sqlbot-postgres-dev:5432 --timeout=120 --strict -- echo -e "\033[1;32mExternal PostgreSQL is ready.\033[0m"

nohup node $SSR_PATH/app.js &

nohup uvicorn main:mcp_app --host 0.0.0.0 --port 8001 &

cd $APP_PATH
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 --proxy-headers
