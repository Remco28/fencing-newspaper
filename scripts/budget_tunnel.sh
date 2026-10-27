#!/usr/bin/env bash
# Start the budget server (if not running) and a Cloudflare Quick Tunnel to it,
# then print the temporary https://*.trycloudflare.com URL.
# No Cloudflare account needed. The URL changes every time the tunnel restarts.
# Logs go to /tmp (outside budget-demo/, which the server serves). Never commit them.
#   scripts/budget_tunnel.sh          start (or reuse) server + tunnel, print URL
#   scripts/budget_tunnel.sh stop     stop the tunnel (server keeps running)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${GAZETTE_PORT:-8766}"
LOG=/tmp/gazette-budget-tunnel.log
PIDF=/tmp/gazette-budget-tunnel.pid
SLOG=/tmp/gazette-budget-server.log

if [[ "${1:-}" == "stop" ]]; then
  [[ -f $PIDF ]] && kill "$(cat $PIDF)" 2>/dev/null && echo "tunnel stopped" || echo "no tunnel running"
  rm -f $PIDF; exit 0
fi

command -v cloudflared >/dev/null || { echo "cloudflared not installed (see https://github.com/cloudflare/cloudflared/releases)"; exit 1; }

if ! curl -fs -o /dev/null "http://127.0.0.1:$PORT/"; then
  (cd "$REPO/budget-demo" && nohup python3 server.py >"$SLOG" 2>&1 &)
  for _ in $(seq 20); do curl -fs -o /dev/null "http://127.0.0.1:$PORT/" && break; sleep 0.5; done
fi
echo "server: http://127.0.0.1:$PORT/ (pid $(pgrep -f 'python3 server.py' | head -1))"

url_from_log() { grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" 2>/dev/null | head -1; }

if [[ -f $PIDF ]] && kill -0 "$(cat $PIDF)" 2>/dev/null && [[ -n "$(url_from_log)" ]]; then
  echo "tunnel already running (pid $(cat $PIDF))"
else
  : >"$LOG"
  nohup cloudflared tunnel --no-autoupdate --url "http://127.0.0.1:$PORT" >"$LOG" 2>&1 &
  echo $! >"$PIDF"
  for _ in $(seq 60); do [[ -n "$(url_from_log)" ]] && break; sleep 0.5; done
fi
URL="$(url_from_log)"
[[ -n $URL ]] || { echo "no tunnel URL yet; see $LOG"; exit 1; }
for _ in $(seq 30); do grep -q "Registered tunnel connection" "$LOG" && break; sleep 0.5; done
if ! grep -q "Registered tunnel connection" "$LOG"; then
  echo "tunnel got URL $URL but never connected to the Cloudflare edge"
  echo "(cloudflared needs outbound port 7844 TCP/UDP; see $LOG). Stopping it."
  kill "$(cat $PIDF)" 2>/dev/null || true; rm -f $PIDF; exit 1
fi
echo "tunnel: $URL (pid $(cat $PIDF))"
