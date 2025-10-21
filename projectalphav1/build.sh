#!/bin/bash
# Railway build script for Django + Vue

# Build Vue frontend
cd ../frontend_vue
npm ci
npm run build

# Copy Vue build output to Django static directory
cd ../projectalphav1
mkdir -p static
cp -r ../frontend_vue/dist/* static/

# Collect all static files for WhiteNoise
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput
