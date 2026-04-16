#!/bin/bash

set -e

echo "▶️ Checking canary release (90% v1, 10% v2)..."
echo "Sending 100 requests to http://localhost:9090/ping..."

v1=0
v2=0

for i in {1..100}; do
    response=$(curl -s http://localhost:9090/ping)
    version=$(echo "$response" | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    if [ "$version" = "v1" ]; then
        v1=$((v1+1))
    elif [ "$version" = "v2" ]; then
        v2=$((v2+1))
    fi
done

echo ""
echo "📊 Results:"
echo "  v1: $v1 requests (expected ~90)"
echo "  v2: $v2 requests (expected ~10)"

if [ "$v1" -ge 80 ] && [ "$v2" -ge 5 ]; then
    echo "✅ Canary split looks correct!"
else
    echo "⚠️  Unexpected distribution. Check VirtualService config."
fi
