# Use an official Node runtime as a parent image
FROM node:20

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in package.json
RUN npm install

# Uncomment if you dont use this image behind a reverse proxy like nginx
# EXPOSE 3000

# Run app.js when the container launches
CMD ["npm", "run", "api"]