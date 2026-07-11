#!/bin/bash

# Navigate to the project directory
cd /home/nkustic/alumni/IC_alumni

# Activate the virtual environment
source venv-alumni/bin/activate

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port_process() {
    local port=$1
    echo "Port $port is in use. Attempting to kill existing process..."
    local pid=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "Killing process $pid on port $port..."
        kill -9 $pid
        sleep 2
        # Check if process was killed successfully
        if check_port $port; then
            echo "Failed to kill process on port $port"
            exit 1
        else
            echo "Successfully killed process on port $port"
        fi
    fi
}

# Check if port 7001 is in use
if check_port 7001; then
    echo "Port 7001 is already in use."
    kill_port_process 7001
fi

# Start Gunicorn
# [資安修補 INFO] 綁定 127.0.0.1，僅供本機 nginx 反向代理使用，避免應用埠直接對外暴露。
echo "Starting Gunicorn on 127.0.0.1:7001..."
gunicorn --workers 3 --bind 127.0.0.1:7001 IC_alumni.wsgi:application
