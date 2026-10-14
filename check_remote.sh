#!/bin/sh
# Abnahmetest: Der Server muss ohne Login ablehnen. Aufruf: ./check_remote.sh https://DEIN-NAME.onrender.com
URL="${1%/}"
echo "1) /health (muss 200 liefern):"
curl -s -o /dev/null -w "   Status %{http_code}\n" "$URL/health"
echo "2) MCP ohne Login (muss 401 liefern, NICHT 200):"
curl -s -o /dev/null -w "   Status %{http_code}\n" -X POST "$URL/mcp" \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
echo "Wenn bei 2) etwas anderes als 401 steht, den Server sofort abschalten und mir das Ergebnis schicken."
