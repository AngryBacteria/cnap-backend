# Use Python 3.11 slim image as the base
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install "fastapi[standard]"

# Copy the rest of the application code
COPY . .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Set a default value for RUN_TYPE
ENV RUN_TYPE=server

# Use the entrypoint script
CMD ["./entrypoint.sh"]