#!/bin/bash

# AutoML Platform - Quick Start Script
# This script starts both the backend and frontend servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}   AutoML Platform - Quick Start${NC}"
echo -e "${GREEN}==================================${NC}\n"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found!${NC}"
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env created${NC}"
        echo -e "${YELLOW}⚠ Please edit .env and add your Google API key!${NC}"
    else
        echo -e "${RED}✗ .env.example not found${NC}"
        exit 1
    fi
fi

# Check if LLM_API_KEY is set
if ! grep -q "LLM_API_KEY=" .env || grep "LLM_API_KEY=" .env | grep -q "your_"; then
    echo -e "${RED}✗ LLM_API_KEY not configured in .env${NC}"
    echo -e "${YELLOW}Please edit .env and add your Google API key from https://ai.google.dev${NC}"
    exit 1
fi

# Check Python
echo -e "${GREEN}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}✗ Python not found. Please install Python 3.10+${NC}"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

PYTHON_VERSION=$($PYTHON_CMD --version | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check Node.js
echo -e "${GREEN}Checking Node.js installation...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"

# Setup backend
echo -e "\n${GREEN}Setting up backend...${NC}"
if [ ! -d "backend" ]; then
    echo -e "${RED}✗ backend directory not found${NC}"
    exit 1
fi

if [ ! -f "backend/requirements.txt" ]; then
    echo -e "${RED}✗ backend/requirements.txt not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Installing Python dependencies...${NC}"
cd backend
$PYTHON_CMD -m pip install -r requirements.txt -q
echo -e "${GREEN}✓ Dependencies installed${NC}"
cd ..

# Setup frontend
echo -e "\n${GREEN}Setting up frontend...${NC}"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Node dependencies...${NC}"
    npm install -q
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Node dependencies already installed${NC}"
fi

# Success message
echo -e "\n${GREEN}==================================${NC}"
echo -e "${GREEN}   Setup Complete!${NC}"
echo -e "${GREEN}==================================${NC}\n"

echo -e "${YELLOW}Starting servers...${NC}\n"

# Create a simple startup function
start_servers() {
    # Start backend in background
    echo -e "${GREEN}Starting Backend Server (port 8000)...${NC}"
    cd backend
    $PYTHON_CMD main.py &
    BACKEND_PID=$!
    cd ..
    sleep 2

    # Start frontend
    echo -e "${GREEN}Starting Frontend Server (port 3000)...${NC}"
    npm run dev &
    FRONTEND_PID=$!

    # Handle cleanup on exit
    trap cleanup SIGINT SIGTERM
    cleanup() {
        echo -e "\n${YELLOW}Shutting down servers...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}Servers stopped${NC}"
        exit 0
    }

    wait
}

# Start both servers
start_servers
