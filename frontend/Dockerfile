FROM node:18-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Build the app
RUN npm run build

# Expose the port
EXPOSE 3000

# Command to run the application
CMD ["npm", "run", "dev", "--", "--host"]