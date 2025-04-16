#!/bin/bash

# Exit on any error
set -e

# Get the tag from the first argument or default to latest
TAG=${1:-latest}

# Your Docker Hub username and repo names
USERNAME=dguilliams3

# Build both images with tags
docker build -t $USERNAME/sentiment-escalation-engine-classification:$TAG -f Dockerfile.classification .
docker build -t $USERNAME/sentiment-escalation-engine-escalation:$TAG -f Dockerfile.escalation .

# Push them to Docker Hub
docker push $USERNAME/sentiment-escalation-engine-classification:$TAG
docker push $USERNAME/sentiment-escalation-engine-escalation:$TAG
