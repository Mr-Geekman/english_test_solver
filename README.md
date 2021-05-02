# English Test Solver

This project has a goal to create a simple app for solving tests of English knowledge using modern techniques of NLP. 

## Architecture

The app starts inside docker containers and use external ports to interact with a user using web-browser.

Backend part uses Django Rest API.

Frontend part (to describe).

## Available test solvers

1. Choose a suitable word from the list.

This task is solved using BERT base model on user's CPU.

## Installation

1. Install Docker.
2. Take Dockerfile from this repository.
3. Build docker image.
4. Run docker with opening XXXX port to the host machine.
