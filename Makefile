.PHONY: clean total build up

build:
	@echo "Building Docker images without cache."
	@docker-compose build --no-cache
	@echo "Building complete."

up:
	@echo "Starting Docker containers in detached mode."
	@docker-compose up -d
	@echo "Containers are up and running!"

setup_env:
	@echo "Setting up virtual environment and installing requirements..."
	@bash scripts/setup_environment.sh

migrate_local:
	@echo "Applying migrations locally..."
	@source venv/bin/activate && python manage.py migrate

#clean only containers, images, and networks, preserve volumes
clean:
	@echo "Stopping and removing all Docker containers..."
	@docker stop $$(docker ps -aq) || true
	@docker rm $$(docker ps -aq) || true
	@echo "Removing all Docker images..."
	@docker rmi -f $$(docker images -aq) || true
	@echo "Removing all unused Docker networks..."
	@docker network prune -f || true
	@echo "Cleanup complete! Persistent volumes are preserved."

#total cleanup: Removes containers, images, and networks -> dont preserve volumes (erases all prev saved data from mariadb)
total_clean:
	@echo "Stopping and removing all Docker containers..."
	@docker stop $$(docker ps -aq) || true
	@docker rm $$(docker ps -aq) || true
	@echo "Removing all Docker images..."
	@docker rmi -f $$(docker images -aq) || true
	@echo "Removing all Docker volumes..."
	@docker volume rm $$(docker volume ls -q) || true
	@echo "Removing all unused Docker networks..."
	@docker network prune -f || true
	@echo "Removing local virtual environment folder..."
	@rm -rf venv
	@echo "Complete cleanup done! All volumes, containers, images, networks, and the local venv have been removed."