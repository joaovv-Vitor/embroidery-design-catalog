# Build the Vue application with the API URL supplied by Dokploy at build time.
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
COPY frontend/package.json ./frontend/package.json
COPY app/package.json ./app/package.json
COPY packages/shared/package.json ./packages/shared/package.json
RUN npm ci --workspace @catalogo-bordados/web --include-workspace-root

COPY frontend ./frontend
COPY packages/shared ./packages/shared

WORKDIR /app/frontend

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Serve the static SPA with Nginx.
FROM nginx:1.27-alpine

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/frontend/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
