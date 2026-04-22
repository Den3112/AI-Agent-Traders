FROM node:20-slim

# Set working directory
WORKDIR /app/dashboard

# We assume the dashboard directory is mounted or copied
# For development, we just need to install dependencies if they are not there
# But we'll do it in the entrypoint or during build if we want it to be faster.

# Pre-install dependencies to speed up startup
COPY dashboard/package*.json ./
RUN npm install

# Expose Next.js port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "-p", "3000", "-H", "0.0.0.0"]
