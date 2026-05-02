# Stage 1: Build the React app
FROM node:20.14.0-alpine3.19 AS build

# Set working directory
WORKDIR /front-end

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install --production

# Copy the rest of the application code
COPY . .

# Build the React app for production
RUN npm run build

# Stage 2: Serve the built application
FROM node:20.14.0-alpine3.19

# Install a lightweight static file server
RUN npm install -g serve

# Set working directory
WORKDIR /front-end

# Copy the build artifacts from the previous stage
COPY --from=build /front-end/build ./build

# Expose port 3000
EXPOSE 3000

# Serve the built application
CMD ["serve", "-s", "build", "-l", "3000"]