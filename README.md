# English Test Solver

This project has a goal to create a simple app for solving tests of English knowledge using modern techniques of NLP. 

## Architecture

The app starts inside docker containers and use a browser to interact with a user.

Backend part uses DjangoRestFramework.

Frontend part (to describe).

## Available test solvers

### Choose a suitable word from a given list

This task is solved using `bert-base-uncased` model on user's CPU.

## Installation

1. Install Docker.
2. Install Docker Compose
3. To explain later...

## Development

To develop frontent you need to run backend server. To do this you should:
1. Install Docker.
2. Build Dockerfile from backend folder.
3. Run docker container with option `-p 8000:8000`.

After this, you can make requests to server on localhost:8000 from localhost:3000.
