# Makefile for managing a uv-managed GitHub repository with pipx

.PHONY: install-pipx install-uv install-deps

# Install pipx in the system
install-pipx:
	@echo "Installing pipx..."
	pip install --user pipx
	python -m pipx ensurepath
	@echo "pipx installation complete. Please restart your terminal if this is the first time installing pipx."

# Install uv with pipx
install-uv: install-pipx
	@echo "Installing uv with pipx..."
	pipx install uv
	@echo "uv installation complete!"

# Install dependencies using uv
install-deps:
	@echo "Installing dependencies with uv..."
	uv install
	@echo "Dependencies installed successfully!"

# Default target to install both pipx, uv, and dependencies
all: install-uv install-deps
	@echo "Setup complete!"
