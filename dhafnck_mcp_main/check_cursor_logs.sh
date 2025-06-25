#!/bin/bash

echo "🔍 Checking Cursor Logs for MCP Connection Issues"
echo "================================================="
echo ""

# Check if Cursor logs directory exists
CURSOR_LOGS_DIR="$HOME/.config/cursor/logs"
if [[ ! -d "$CURSOR_LOGS_DIR" ]]; then
    echo "❌ Cursor logs directory not found at: $CURSOR_LOGS_DIR"
    echo "💡 Try these alternative locations:"
    echo "   - Windows: %APPDATA%/cursor/logs/"
    echo "   - macOS: ~/Library/Logs/cursor/"
    echo "   - Snap: ~/snap/cursor/common/.config/cursor/logs/"
    exit 1
fi

echo "✅ Found Cursor logs directory: $CURSOR_LOGS_DIR"
echo ""

# List recent log files
echo "📁 Recent log files:"
ls -la "$CURSOR_LOGS_DIR" | head -10
echo ""

# Check for MCP-related errors in recent logs
echo "🔍 Searching for MCP-related errors..."
echo "======================================"

# Search for dhafnck_mcp errors
echo "🔍 dhafnck_mcp errors:"
find "$CURSOR_LOGS_DIR" -name "*.log" -mtime -1 -exec grep -l "dhafnck" {} \; 2>/dev/null | while read logfile; do
    echo "📋 Found in: $logfile"
    grep -n -A2 -B2 "dhafnck" "$logfile" | tail -20
    echo ""
done

# Search for general MCP errors
echo "🔍 General MCP errors:"
find "$CURSOR_LOGS_DIR" -name "*.log" -mtime -1 -exec grep -l -i "mcp\|model.*context.*protocol" {} \; 2>/dev/null | while read logfile; do
    echo "📋 Found in: $logfile"
    grep -n -A2 -B2 -i "mcp\|model.*context.*protocol" "$logfile" | tail -20
    echo ""
done

# Search for server startup errors
echo "🔍 Server startup errors:"
find "$CURSOR_LOGS_DIR" -name "*.log" -mtime -1 -exec grep -l -i "server.*error\|spawn.*error\|enoent\|connection.*failed" {} \; 2>/dev/null | while read logfile; do
    echo "📋 Found in: $logfile"
    grep -n -A2 -B2 -i "server.*error\|spawn.*error\|enoent\|connection.*failed" "$logfile" | tail -20
    echo ""
done

# Check main.log specifically
MAIN_LOG="$CURSOR_LOGS_DIR/main.log"
if [[ -f "$MAIN_LOG" ]]; then
    echo "🔍 Recent entries in main.log:"
    echo "=============================="
    tail -50 "$MAIN_LOG" | grep -i -A2 -B2 "mcp\|dhafnck\|server\|error" || echo "No MCP-related entries found in recent main.log"
    echo ""
fi

# Check renderer logs
RENDERER_LOGS=$(find "$CURSOR_LOGS_DIR" -name "renderer*.log" -mtime -1 | head -3)
if [[ -n "$RENDERER_LOGS" ]]; then
    echo "🔍 Checking renderer logs for MCP errors:"
    echo "========================================"
    for log in $RENDERER_LOGS; do
        echo "📋 Checking: $log"
        tail -30 "$log" | grep -i -A2 -B2 "mcp\|dhafnck\|server.*error" || echo "No MCP-related entries found"
        echo ""
    done
fi

echo "💡 Tips:"
echo "1. If no errors found, the issue might be that Cursor isn't trying to start the server"
echo "2. Check Cursor Developer Console (Ctrl+Shift+I) for real-time errors"
echo "3. Try restarting Cursor after ensuring .cursor/mcp.json is correct"
echo "4. Monitor logs in real-time: tail -f $CURSOR_LOGS_DIR/main.log" 