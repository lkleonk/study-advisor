FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ARG NEXT_PUBLIC_ENABLE_DEV_TOOLS=false
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
ENV NEXT_PUBLIC_ENABLE_DEV_TOOLS=${NEXT_PUBLIC_ENABLE_DEV_TOOLS}

RUN npm run build

FROM caddy:2-alpine AS static-server

COPY Caddyfile.preview /etc/caddy/Caddyfile
COPY --from=builder /app/out /srv

EXPOSE 80
