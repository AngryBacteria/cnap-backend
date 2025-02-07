# Use Python 3.11 slim image as the base
FROM python:3.11-slim

# Build arguments for flexibility
ARG USER_ID=1000
ARG GROUP_ID=1000

# Create a user with the same UID and GID as the host user to avoid permission issues
RUN groupadd -f -g ${GROUP_ID} dockeruser && useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash dockeruser

# Set the working directory and chown it
WORKDIR /home/dockeruser/workspace
COPY . .
RUN chown -R ${USER_ID}:${GROUP_ID} /home/dockeruser

# Change to the non-root user
USER dockeruser

# Install Python dependencies
RUN python -m venv /home/dockeruser/workspace/venv
RUN /home/dockeruser/workspace/venv/bin/pip install --no-cache-dir -r requirements.txt
RUN /home/dockeruser/workspace/venv/bin/pip install "fastapi[standard]"


# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Set a default value for RUN_TYPE
ENV RUN_TYPE=server
ENV PATH="/home/dockeruser/.local/bin:${PATH}"

# Use the entrypoint script
CMD ["./entrypoint.sh"]