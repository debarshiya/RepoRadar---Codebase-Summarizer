#!/bin/bash
set -e
mkdir -p /root/.streamlit
cat >/root/.streamlit/config.toml <<'EOF'
[server]
headless = true
enableXsrfProtection = true
enableCORS = true
EOF
