#!/bin/bash

# Exit on error
set -e

# Configuration
SERVICE_NAME="notion_status"
APP_DIR="$(pwd)"
VENV_DIR="$APP_DIR/venv"
PORT=11999

echo "Installing $SERVICE_NAME service..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Install required system packages
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3-venv python3-pip

# Create and activate virtual environment
echo "Setting up virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment and install Python dependencies
echo "Installing Python dependencies..."
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt
deactivate

# Create systemd service file
echo "Creating systemd service..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Notion Status Monitoring Service
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
echo "Enabling and starting service..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

# Check service status
echo "Checking service status..."
systemctl status $SERVICE_NAME

echo "Installation complete!"
echo "Service is running on port $PORT"
echo "To check service status: systemctl status $SERVICE_NAME"
echo "To view logs: journalctl -u $SERVICE_NAME -f" 