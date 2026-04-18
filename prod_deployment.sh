!#/bin/bash

cd frontend; sudo docker build -t h1.dev.virt/wp-management-tool-frontend:latest .
sudo docker push h1.dev.virt/wp-management-tool-frontend:latest

cd ../backend; sudo docker build -t h1.dev.virt/wp-management-tool-backend:latest .
sudo docker push h1.dev.virt/wp-management-tool-backend:latest

cd ../worker; sudo docker build -t h1.dev.virt/wp-management-tool-worker:latest .
sudo docker push h1.dev.virt/wp-management-tool-worker:latest

ssh h1.dev.virt "cd /etc/docker-compose/wp-management-tool; docker compose down; docker compose pull; docker compose up -d"