#!/bin/bash
# Portfolio Demo Setup Script
# Run this to get MiniGlean ready for screenshots/recording in under 2 minutes

set -e  # Exit on any error

echo "🚀 MiniGlean Portfolio Setup"
echo "=============================="
echo ""

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check for .env file
if [ ! -f "apps/api/.env" ]; then
    echo "⚙️  Setting up environment file..."
    cp apps/api/.env.example apps/api/.env
    echo ""
    echo "📝 IMPORTANT: Edit apps/api/.env and add your OpenAI API key"
    echo "   Get one at: https://platform.openai.com/api-keys"
    echo ""
    echo "   After adding the key, run this script again."
    exit 0
fi

# Check if API key is set
if ! grep -q "OPENAI_API_KEY=sk-" apps/api/.env; then
    echo "⚠️  No OpenAI API key found in apps/api/.env"
    echo ""
    echo "   Edit apps/api/.env and add your key:"
    echo "   OPENAI_API_KEY=sk-your-key-here"
    echo ""
    echo "   Get one at: https://platform.openai.com/api-keys"
    exit 1
fi

echo "✅ Prerequisites checked"
echo ""

# Start services
echo "🐳 Starting services (this may take 30-60 seconds)..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database..."
max_attempts=30
attempt=0
until docker-compose exec -T db pg_isready -U postgres &> /dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Database failed to start"
        exit 1
    fi
    sleep 1
done

echo "✅ Database ready"
echo ""

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T api alembic upgrade head

echo "✅ Migrations complete"
echo ""

# Seed demo data
echo "📚 Seeding demo documents..."
cd demo
if [ ! -d "node_modules" ]; then
    npm install tsx --silent
fi
NEXT_PUBLIC_API_URL=http://localhost:8000 npx tsx seed.ts
cd ..

echo ""
echo "✅ Demo data loaded"
echo ""
echo "=============================="
echo "🎉 Setup Complete!"
echo "=============================="
echo ""
echo "Your MiniGlean demo is ready at:"
echo "  🌐 http://localhost:3000"
echo ""
echo "Try these questions:"
echo "  • How much notice do I need to give to end my lease?"
echo "  • What are the action items from the team meeting?"
echo "  • Tell me about FastAPI"
echo ""
echo "Follow demo/demo-script.md for a full walkthrough."
echo ""
echo "To stop:"
echo "  docker-compose down"
echo ""
