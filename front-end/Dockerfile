# Use Node.js image
FROM node:20.18.0

# Set working directory
WORKDIR /front-end

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React app for production
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Serve the built application
CMD ["npm","start"]
