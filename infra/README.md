# Using Docker Compose

## Ensure docker compose is installed

Installation documentation can be found [here](https://docs.docker.com/compose/install/)


## Pre-requirements

Ensure your docker environment has at least 4GB of memory. Default is 2.0GB for windows and Mac.

> Some users report 4GB may not be enough for latest versions of elasticsearch. 6.0GB seems to work fine

## Bringing up the containers

```bash
TAG=6.2.1 docker-compose up
```