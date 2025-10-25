FROM node:18-alpine

WORKDIR /app

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances
RUN npm install --legacy-peer-deps

# Copie du code source
COPY . .

# Exposition du port
EXPOSE 3000

# Commande de démarrage
CMD ["npm", "start"]
