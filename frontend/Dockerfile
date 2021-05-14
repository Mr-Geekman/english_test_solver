FROM node:lts-alpine

# download dependencies for frontend
RUN apk upgrade --update
RUN apk add git
RUN git clone https://github.com/Mr-Geekman/english_test_solver.git

# change working directory for instructions below
WORKDIR english_test_solver/frontend

# install simple http server for serving static content
RUN npm install -g http-server

# install project dependencies
RUN npm install

# build app for production with minification
RUN npm run build

# run server
EXPOSE 8080
CMD [ "http-server", "dist" ]
