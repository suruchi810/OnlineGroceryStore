echo "🚀 Starting build process..."

# Install Python dependencies
python3.13.5 -m pip install -r requirements.txt

# Run migrations
python3.13.5 manage.py collectstatic --noinput --clear

echo "Build process completed!"