#!/usr/bin/env bash
# setup.sh — install Java 17 JDK + Maven for yoga-api local development
# Run once with: bash setup.sh

set -e

echo "=== Checking Java ==="
if java -version 2>/dev/null; then
    echo "Java already installed."
else
    echo "Installing OpenJDK 17..."
    sudo apt-get update -q
    sudo apt-get install -y openjdk-17-jdk
fi

echo ""
echo "=== Checking Maven ==="
if mvn -version 2>/dev/null; then
    echo "Maven already installed."
else
    echo "Installing Maven..."
    sudo apt-get install -y maven
fi

echo ""
echo "=== Verifying ==="
java -version
mvn -version

echo ""
echo "Setup complete. Run the project with:"
echo "  cd yoga-api && mvn spring-boot:run"
echo ""
echo "Or with Docker (no local Java needed):"
echo "  cd yoga-api && docker compose up --build"
