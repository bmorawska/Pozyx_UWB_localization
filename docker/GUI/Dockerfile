FROM node:16
WORKDIR /usr/src/app
COPY  ../../GUI/package*.json ./
RUN npm install
COPY ../../GUI/. .
EXPOSE 3000
CMD [ "node", "server.js" ]