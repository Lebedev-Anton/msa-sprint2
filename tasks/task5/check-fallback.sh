#!/bin/bash

set -e

echo "▶️ Testing fallback route..."
echo ""

# Находим один из подов v1 и гасим его
POD=$(kubectl get pods -l app=booking-service,version=v1 -o jsonpath='{.items[0].metadata.name}')
echo "🔴 Killing pod: $POD"
kubectl delete pod "$POD" --grace-period=0 --force 2>/dev/null || true

echo "⏳ Waiting 3 seconds..."
sleep 3

echo ""
echo "📡 Sending 10 requests (fallback should route to v2 or remaining v1 pod)..."
v1=0
v2=0
errors=0

for i in {1..10}; do
    response=$(curl -s --max-time 5 http://localhost:9090/ping || echo '{"error":"timeout"}')
    version=$(echo "$response" | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    if [ "$version" = "v1" ]; then
        v1=$((v1+1))
    elif [ "$version" = "v2" ]; then
        v2=$((v2+1))
    else
        errors=$((errors+1))
    fi
    echo "  Request $i: $response"
done

echo ""
echo "📊 Results:"
echo "  v1: $v1 responses"
echo "  v2: $v2 responses"
echo "  errors/timeouts: $errors"

if [ "$errors" -eq 0 ]; then
    echo "✅ Fallback working — no errors despite killed pod!"
else
    echo "⚠️  Some requests failed ($errors errors)"
fi

echo ""
echo "⏳ Waiting for Kubernetes to restart killed pod..."
kubectl rollout status deployment/booking-service-v1 --timeout=60s
echo "✅ Pod restarted successfully"
