#!/bin/bash

# Setup script for tap-sigma with Snowflake
set -e

echo "🔧 Setting up tap-sigma with Snowflake..."

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version OK: $python_version"

# Install Meltano
echo "📦 Installing Meltano..."
pip3 install meltano

# Initialize Meltano project (if not already initialized)
if [ ! -f "meltano.yml" ]; then
    echo "🚀 Initializing Meltano project..."
    meltano init . --no_usage_stats
fi

# Install the tap in development mode
echo "🔌 Installing tap-sigma-computing..."
pip3 install -e .

# Add extractors and loaders
echo "➕ Adding Sigma Computing tap..."
meltano add --custom extractor tap-sigma-computing

echo "➕ Adding Snowflake target..."
meltano add loader target-snowflake --variant=transferwise

# Create environment file template
echo "📝 Creating environment template..."
cat > .env.template << EOF
# Sigma Computing API Credentials
TAP_SIGMA_COMPUTING_CLIENT_ID=your_client_id_here
TAP_SIGMA_COMPUTING_CLIENT_SECRET=your_client_secret_here
TAP_SIGMA_COMPUTING_BASE_URL=https://aws-api.sigmacomputing.com

# Snowflake Connection
TARGET_SNOWFLAKE_ACCOUNT=your_account.region
TARGET_SNOWFLAKE_DBNAME=your_database
TARGET_SNOWFLAKE_USER=your_username
TARGET_SNOWFLAKE_PASSWORD=your_password
TARGET_SNOWFLAKE_WAREHOUSE=your_warehouse
TARGET_SNOWFLAKE_DEFAULT_TARGET_SCHEMA=sigma_computing
EOF

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env and fill in your credentials"
echo "2. Run: meltano config tap-sigma-computing test"
echo "3. Run: meltano run tap-sigma-computing target-snowflake"
echo ""
echo "📖 See README.md for detailed instructions"
