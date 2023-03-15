FROM node:18 AS builder

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm yarn install
COPY . .
RUN yarn build

FROM node:18 as production

ARG NODE_ENV=production
ENV NODE_ENV=${NODE_ENV}

WORKDIR /usr/src/app

COPY package*.json ./
RUN yarn install

COPY . .
COPY --from=builder /usr/src/app/dist ./dist

CMD ["node", "dist/main"]
