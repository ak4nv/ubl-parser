name = webware24
network = my-network
PG_PWD ?= pg_password

all: build

uv:
	@if ! command -v uv > /dev/null 2>&1; then \
		echo "Install uv python package manager using this script"; \
		echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo ""; \
		echo "See docs: https://docs.astral.sh/uv/getting-started/installation/"; \
		false; \
	fi

build: uv
	@uv sync

repl: uv
	@uv run python

run: uv
	@uv run fastapi dev

# Commands for image manipulation

net:
	@podman network exists $(network) && exit || \
	podman network create $(network)

pg:
	@podman image exists postgres && exit || \
	podman create --name postgres -p 5432:5432 postgres:latest
	@podman container exists postgres && exit || \
	@podman create \
	--network $(network) \
	--name postgres \
	-e POSTGRES_PASSWORD=$(PG_PWD) \
	-p 5432:5432 \
	postgres

db: net pg
	@podman start postgres > /dev/null

psql: pg
	@podman exec -it postgres psql -Upostgres $(name)

image-build:
	@podman image exists $(name):dev && exit || \
	podman build --no-cache --dns=1.1.1.1 -t $(name):dev .

image-run: db image-build
	@echo $(PG_PWD)
	@podman run --rm \
	-p 8080:80 \
	-e DATABASE_NAME=$(name) \
	-e DATABASE_HOST=postgres \
	-e DATABASE_PASSWORD=$(PG_PWD) \
	--network $(network) \
	--name $(name) \
	$(name):dev

.PHONY: pg psql uv
