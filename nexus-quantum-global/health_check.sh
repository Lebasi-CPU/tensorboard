#!/bin/bash

# Check Stealth API [8]
echo "Checking stealth API: ${API_STEALTH_URL}"

curl -f -s ${API_STEALTH_URL} > /dev/null

if [ $? -eq 0 ]; then
    echo "Stealth API is healthy."
    exit 0 # Si ambos están bien [8]
else
    echo "Stealth API is NOT healthy."
    exit 1 # Si alguno falla [8]
fi
