#!/bin/sh
set -e

echo "Initializing database..."
python scripts/init_db.py

if [ "${SEED_DATASET}" = "true" ]; then
  echo "Seeding dataset (if empty)..."
  python scripts/seed_dataset.py
fi

echo "Starting application..."
exec "$@"
