FROM node:20-slim

# Set working directory
WORKDIR /app/dashboard

# Create a non-root user
RUN groupadd -r trader && useradd -r -g trader trader \
    && chown -R trader:trader /app

# Pre-install dependencies to speed up startup
COPY dashboard/package*.json ./
RUN npm install && npm cache clean --force

# Copy the rest of the dashboard code
COPY dashboard/ ./

# Ensure permissions
RUN chown -R trader:trader /app

# Switch to non-root user
USER trader

# Build the application
RUN npm run build

# Expose Next.js port
EXPOSE 3000

# Start production server
CMD ["npm", "start", "--", "-p", "3000", "-H", "0.0.0.0"]
