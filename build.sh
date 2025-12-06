#!/bin/bash
# Build script for Render to use Python 3.10.12 and install ODBC drivers

set -e  # Exit on error

# Install Microsoft ODBC Driver for SQL Server
echo "Installing Microsoft ODBC Driver for SQL Server..."

# Add Microsoft repository and install ODBC Driver 18
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Update package list
apt-get update

# Install ODBC Driver 18 for SQL Server
ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Also install unixODBC-dev (required by pyodbc)
apt-get install -y unixodbc-dev

echo "ODBC Driver installed successfully"

# Use Python 3.10 explicitly
python3.10 --version || python3 --version

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

