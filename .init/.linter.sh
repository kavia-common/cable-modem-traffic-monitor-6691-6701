#!/bin/bash
cd /home/kavia/workspace/code-generation/cable-modem-traffic-monitor-6691-6701/traffic_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

