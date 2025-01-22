# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

#Installing uv latest images from source code for the Python image selected
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/


# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
#expose the port in which we can visualize the app
EXPOSE 8080
# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the streamlit application by default
CMD ["streamlit", "run", "main.py","--server.port=8080", "--server.address=0.0.0.0"]