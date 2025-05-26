#!/bin/bash

# Change to the project directory
cd /path/to/your/ParkingSystem

# Activate virtual environment if you're using one
# source /path/to/your/venv/bin/activate

# Run the management command
python manage.py update_daily_logistics

# Log the execution
echo "Logistics update completed at $(date)" >> /path/to/your/ParkingSystem/logs/logistics_update.log 