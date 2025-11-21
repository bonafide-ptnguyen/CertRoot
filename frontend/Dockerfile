# ----------------------------
# Stage 1: Build the App
# ----------------------------
FROM node:20-alpine as builder

WORKDIR /app

# Copy package.json first to cache dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the code and build
COPY . .
RUN npm run build

# ----------------------------
# Stage 2: Serve with Nginx
# ----------------------------
FROM nginx:alpine

# Copy the build output ('dist' folder) from the builder stage to Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 (standard web port)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]