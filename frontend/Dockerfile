FROM node:22-slim AS base

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG API_PROXY_TARGET=http://localhost:8000
ENV API_PROXY_TARGET=${API_PROXY_TARGET}

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
