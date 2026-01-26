#!/bin/bash
set -e

echo "=== Kraken Greenfoot Development Setup ==="

BENCH_DIR="/home/frappe/frappe-bench"
SITE_NAME="kraken.localhost"

# Check if bench already initialized
if [ ! -d "$BENCH_DIR/apps/frappe" ]; then
    echo "Initializing Frappe Bench..."
    cd /home/frappe
    bench init --skip-redis-config-generation --frappe-branch version-15 frappe-bench

    cd "$BENCH_DIR"

    # Configure Redis
    bench set-config -g redis_cache "redis://redis-cache:6379"
    bench set-config -g redis_queue "redis://redis-queue:6379"
    bench set-config -g redis_socketio "redis://redis-queue:6379"

    # Configure MariaDB
    bench set-config -g db_host mariadb
    bench set-config -gp db_port 3306

    # Get ERPNext
    echo "Getting ERPNext..."
    bench get-app --branch version-15 erpnext
else
    echo "Bench already initialized, skipping..."
    cd "$BENCH_DIR"
fi

# Link custom apps from workspace
echo "Linking custom apps..."

# Remove existing symlinks if they exist
rm -rf "$BENCH_DIR/apps/kraken_theme" 2>/dev/null || true
rm -rf "$BENCH_DIR/apps/warranties" 2>/dev/null || true

# Create symlinks to mounted workspace apps
ln -sf /workspace/apps/kraken_theme "$BENCH_DIR/apps/kraken_theme"
ln -sf /workspace/apps/warranties "$BENCH_DIR/apps/warranties"

# Update apps.txt to include custom apps
if ! grep -q "kraken_theme" "$BENCH_DIR/sites/apps.txt" 2>/dev/null; then
    echo "kraken_theme" >> "$BENCH_DIR/sites/apps.txt"
fi
if ! grep -q "warranties" "$BENCH_DIR/sites/apps.txt" 2>/dev/null; then
    echo "warranties" >> "$BENCH_DIR/sites/apps.txt"
fi

# Create site if it doesn't exist
if [ ! -d "$BENCH_DIR/sites/$SITE_NAME" ]; then
    echo "Creating site: $SITE_NAME"

    # Wait for MariaDB to be ready
    echo "Waiting for MariaDB..."
    while ! mysqladmin ping -h mariadb -u root -p123 --silent 2>/dev/null; do
        sleep 2
    done
    echo "MariaDB is ready!"

    bench new-site "$SITE_NAME" \
        --mariadb-root-password 123 \
        --admin-password admin \
        --no-mariadb-socket

    # Set as default site
    bench use "$SITE_NAME"

    # Install apps
    echo "Installing ERPNext..."
    bench --site "$SITE_NAME" install-app erpnext

    echo "Installing Kraken Theme..."
    bench --site "$SITE_NAME" install-app kraken_theme

    echo "Installing Warranties..."
    bench --site "$SITE_NAME" install-app warranties

    # Enable developer mode
    bench --site "$SITE_NAME" set-config developer_mode 1
    bench --site "$SITE_NAME" clear-cache
else
    echo "Site $SITE_NAME already exists"
    bench use "$SITE_NAME"

    # Run migrations in case apps were updated
    echo "Running migrations..."
    bench --site "$SITE_NAME" migrate
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start the development server, run:"
echo "  cd /home/frappe/frappe-bench && bench start"
echo ""
echo "Access the site at: http://localhost:8000"
echo "Login: Administrator / admin"
echo ""
