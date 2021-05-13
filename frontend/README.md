# English Test Solver (frontend)

## Project setup
```
yarn install
```

### Compiles and hot-reloads for development
```
yarn serve
```

### Compiles and minifies for production
```
yarn build
```

### Lints and fixes files
```
yarn lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

## Run witch Docker

- Download Dockerfile
- Run for build the project: `docker build -t english_test_solver/front .`
- Run for start the Docker image: `docker run -it -p 8080:8080 --rm english_test_solver/front`
- Complete! Go to: `http://localhost:8080/`