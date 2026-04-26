# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

# Serve stage
FROM node:18-alpine AS serve
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
EXPOSE 5173
CMD ["node", "node_modules/.bin/vite", "--host", "0.0.0.0", "--port", "5173"]
