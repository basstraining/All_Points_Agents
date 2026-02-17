#!/bin/bash
# Deploy the All Points MCP server to Arcade Cloud.
# Usage:  ./deploy.sh              (deploy)
#         ./deploy.sh status       (check status)
#
# Prerequisites:
#   - arcade CLI installed (uv tool install arcade-mcp)
#   - authenticated (arcade login)
#   - database generated (python3 setup_database.py)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

show_status() {
    echo "Checking deployed servers..."
    echo ""
    arcade server list
}

if [ "${1:-}" = "status" ]; then
    show_status
    exit 0
fi

# Ensure database exists
if [ ! -f "$SCRIPT_DIR/shared/database/allpoints.db" ]; then
    echo "Database not found. Running setup..."
    python3 "$SCRIPT_DIR/setup_database.py"
    echo ""
fi

echo "Deploying All Points MCP server to Arcade Cloud..."
echo "(Single server with 29 tools across 6 domains)"
echo ""

arcade deploy -e mcp_servers/allpoints_server.py

echo ""
echo "Next steps:"
echo "  1. Go to the Arcade Dashboard → MCP Gateways"
echo "  2. Create a Gateway and add tools from the 'allpoints' server"
echo "  3. Add Gmail, Google Slides, and Slack integrations to the Gateway"
echo "  4. Copy the Gateway URL into your chatbot .env"
echo ""
echo "Gateway URL format: https://api.arcade.dev/mcp/<your-gateway-slug>"
echo ""
echo "To check status:  ./deploy.sh status"
echo "To view logs:      arcade server logs allpoints"
