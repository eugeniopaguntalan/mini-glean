#!/bin/bash
# Mock Mode Setup - No API keys needed!
# Perfect for portfolio screenshots and demos

set -e

echo "🎭 MiniGlean Mock Mode Setup"
echo "=============================="
echo "No OpenAI API key required!"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Clean up any existing mock volumes to ensure fresh start
echo "🧹 Cleaning up old data..."
docker-compose -f docker-compose.mock.yml down -v 2>/dev/null || true

echo "🐳 Starting services in mock mode..."
docker-compose -f docker-compose.mock.yml up -d

# Wait for database
echo "⏳ Waiting for database..."
max_attempts=30
attempt=0
until docker-compose -f docker-compose.mock.yml exec -T db pg_isready -U postgres &> /dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Database failed to start"
        docker-compose -f docker-compose.mock.yml logs db
        exit 1
    fi
    sleep 1
done

echo "✅ Database ready"
echo ""

# Run migrations
echo "📊 Running database migrations..."
docker-compose -f docker-compose.mock.yml exec -T api alembic upgrade head

# Load mock data
echo "📚 Loading mock demo data..."
docker-compose -f docker-compose.mock.yml exec -T db psql -U postgres -d miniglean -f /mock_data.sql

echo ""
echo "=============================="
echo "🎉 Mock Mode Ready!"
echo "=============================="
echo ""
echo "Your MiniGlean demo is running at:"
echo "  🌐 http://localhost:3000"
echo ""
echo "✨ Everything is mocked - no API calls!"
echo ""
echo "Pre-loaded documents:"
echo "  📄 rental-contract.pdf"
echo "  📄 fastapi-notes.pdf"
echo "  📝 Team Meeting - June 14"
echo ""
echo "Try these questions:"
echo "  • How much notice do I need to give to end my lease?"
echo "  • What are the action items from the team meeting?"
echo "  • Tell me about FastAPI"
echo ""
echo "To stop:"
echo "  docker-compose -f docker-compose.mock.yml down"
echo ""
