#!/usr/bin/env bash
set -euo pipefail

PUBLIC_ORIGIN="${MRT_PUBLIC_ORIGIN:-https://medroundtable.cn}"

echo "MedRoundTable official production verification"
echo "Website: ${PUBLIC_ORIGIN}/"
echo "Observatory: ${PUBLIC_ORIGIN}/real-analysis.html"

curl -fsS "${PUBLIC_ORIGIN}/api/health"
printf '\n'
curl -fsS "${PUBLIC_ORIGIN}/api/v1/relay/health"
printf '\n'
curl -fsSI "${PUBLIC_ORIGIN}/real-analysis.html" | sed -n '1p'

echo "Production verification passed. Deployment instructions: DEPLOYMENT.md"
