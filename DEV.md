# Development Guide

Engineer is a Python 2.7 static site generator. This guide explains how to run and test Engineer using Docker.

## Prerequisites

- Docker and Docker Compose installed

## Running Engineer with Docker Compose

The Docker setup mounts the `./site` directory into the container at `/site`. Place your Engineer site files in this directory.

### Build the image

```bash
docker compose build
```

### Run Engineer commands

The container's entrypoint is the `engineer` command, so you can pass any Engineer subcommand directly:

```bash
# Show help
docker compose run --rm engineer --help

# Build a site
docker compose run --rm engineer build

# Serve the site locally (with port mapping)
docker compose run --rm -p 8000:8000 engineer serve

# Clean the output directory
docker compose run --rm engineer clean
```

### Using a different site directory

To process a site in a different location, override the volume mount:

```bash
docker compose run --rm -v /path/to/your/site:/site engineer build
```

### Using the sample site

To try Engineer with the included sample site:

```bash
docker compose run --rm -v ./engineer/sample_site/default:/site engineer build
```

## Running Tests

Tests use tox. To run them inside the container:

```bash
docker compose run --rm --entrypoint "" engineer tox
```

Or run pytest directly:

```bash
docker compose run --rm --entrypoint "" engineer python -m pytest engineer/unittests/
```

## Interactive Shell

To get a shell inside the container for debugging:

```bash
docker compose run --rm --entrypoint /bin/bash engineer
```

## Site Structure

An Engineer site typically contains:

```
site/
  config.yaml     # Site configuration
  posts/          # Markdown posts
  templates/      # Custom templates (optional)
  archives/       # Archived posts (optional)
```

See `engineer/sample_site/default/` for an example.
