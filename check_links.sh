#!/bin/bash
# Link QC Check Script

echo "=== MedRoundTable Link Quality Check ==="
echo ""

# Check index.html links
echo "Checking index.html..."
grep -n "href=\"./" index.html | grep -v "href=\"./assets" | head -20
echo ""

# Check tools.html links  
echo "Checking tools.html..."
grep -n "href=" tools.html | head -10
echo ""

# Check login.html links
echo "Checking login.html..."
grep -n "href=" login.html | head -10
echo ""

echo "=== Check Complete ==="
