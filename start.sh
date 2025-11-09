#!/bin/bash
set -e

# Show versions in web logs for debugging
python -V || true
python -m pip -V || true
python -m pip show streamlit || true
python -m pip show gitpython || true

# Run Streamlit on the EB port
exec streamlit run src/app.py --server.address 0.0.0.0 --server.port "${PORT:-8000}"
