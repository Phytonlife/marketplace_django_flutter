# Stage 1: Build the Flutter web app
FROM cirrusci/flutter:stable AS build

# Set working directory
WORKDIR /app

# Copy Flutter project files
COPY . .

# Get dependencies
RUN flutter pub get

# Build the web application
RUN flutter build web --release

# Stage 2: Serve the built web app with Nginx
FROM nginx:stable-alpine

# Copy the built files from the build stage
COPY --from=build /app/build/web /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Nginx will be started by default
CMD ["nginx", "-g", "daemon off;"]
