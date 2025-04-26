.PHONY: build up logs stop clean

#build images
build:
	@echo "building images"
	docker-compose build --no-cache

#start docker compose in detached mode
up:
	@echo "🚀 Bringing up services…"
	docker-compose up -d

#following logs
logs:
	docker-compose logs -f

#stop all services
stop:
	docker-compose down

#remove containers & local images
clean:
	docker-compose down --rmi local

#remove all inc images
destroy:
	docker-compose down --rmi all -v
