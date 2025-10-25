# Multi-stage build for optimized frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./
COPY tsconfig.json ./
COPY next.config.js ./
COPY tailwind.config.ts ./
COPY postcss.config.js ./

# Installer les dépendances
RUN npm ci

# Copier le code source
COPY app ./app
COPY components ./components
COPY hooks ./hooks
COPY lib ./lib
COPY store ./store
COPY types ./types
COPY public ./public

# Builder l'app Next.js
RUN npm run build

# Runtime stage
FROM node:18-alpine

WORKDIR /app

# Copier package.json
COPY package*.json ./

# Installer les dépendances de production
RUN npm ci --only=production

# Copier le build depuis le builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./

# Exposer le port
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Démarrer l'app
CMD ["npm", "start"]
