FROM node:lts-alpine

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

RUN npm install @vue/cli@5.0.8 -g

COPY package.json .
COPY babel.config.js .
COPY jsconfig.json .
COPY vue.config.js .

ADD src ./src

RUN npm install

CMD ["npm", "run", "serve"]