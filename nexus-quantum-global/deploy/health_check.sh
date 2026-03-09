#!/bin/bash

# Check Stealth API [8]
echo "Checking stealth API: ${API_STEALTH_URL}"

# Simulate check (use curl in real environment)
if [ -n "${API_STEALTH_URL}" ]; then
    echo "Stealth API is healthy (Simulated)."
    exit 0
else
    echo "Stealth API is NOT configured."
    exit 1
fi
