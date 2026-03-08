FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]