FROM node:20-slim

# Set working directory
WORKDIR /app/dashboard

# Create a non-root user
RUN groupadd -r trader && useradd -r -g trader trader \
    && chown -R trader:trader /app

# Pre-install dependencies to speed up startup
COPY dashboard/package*.json ./
RUN npm install

# Copy the rest of the dashboard code
COPY dashboard/ ./

# Ensure permissions
RUN chown -R trader:trader /app

# Switch to non-root user
USER trader

# Expose Next.js port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "-p", "3000", "-H", "0.0.0.0"]
