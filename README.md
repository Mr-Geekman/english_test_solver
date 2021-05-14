# English Test Solver

This project has a goal to create a simple app for solving tests of English knowledge using modern techniques of NLP. 

## Architecture

The app starts inside docker containers and use a browser to interact with a user.

Backend part uses DjangoRestFramework.

Frontend part uses Vue.js.

## Available test solvers

### Choose a suitable word from a given list

This task is solved using `bert-base-uncased` model on user's CPU.

## Installation

1. Install Docker
2. Install Docker Compose
3. Copy and run `prepare.sh` to download the smallest amount of necessary files
4. Run `docker-compose up` to start services
5. Open `http://localhost:8080/` and use!

To stop containers run `docker-compose stop`.

## Development

Look at REAMDE files of frontend and backend parts.