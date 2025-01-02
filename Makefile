.PHONY: clean build up


build:
	@echo "Building Docker images without cache."
	@docker-compose build --no-cache
	@echo "Building complete."

up:
	@echo "Starting Docker containers in detached mode."
	@docker-compose up -d
	@echo "Containers are up and running!"

# Clean all Docker containers, images, volumes, and networks
clean:
	@echo "Stopping and removing all Docker containers..."
	@docker stop $$(docker ps -aq) || true
	@docker rm $$(docker ps -aq) || true
	@echo "Removing all Docker images..."
	@docker rmi -f $$(docker images -aq) || true
	@echo "Removing all Docker volumes..."
	@docker volume rm $$(docker volume ls -q) || true
	@echo "Removing all unused Docker networks..."
	@docker network prune -f || true
	@echo "Cleanup complete!"

