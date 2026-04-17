#!/bin/bash
date > backend/app/COMMIT_HASH;
docker compose down;
docker compose up -d --build;
