FROM node:20-slim

WORKDIR /app

COPY FrontEnd/package*.json ./
RUN npm install

COPY FrontEnd ./

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
