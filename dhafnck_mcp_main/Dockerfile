# Multi-stage Dockerfile for DhafnckMCP Server
# Target: Image size under 200MB with full functionality

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG PYTHONUNBUFFERED=1
ARG PYTHONDONTWRITEBYTECODE=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install uv for faster dependency resolution
RUN pip install uv

# Install dependencies
RUN uv sync --no-dev --frozen

# Copy source code
COPY src/ src/
COPY README.md ./

# Install the package
RUN uv pip install -e .

# Stage 2: Runtime stage
FROM python:3.11-slim as runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src
ENV FASTMCP_LOG_LEVEL=INFO
ENV FASTMCP_ENABLE_RICH_TRACEBACKS=0

# Create non-root user for security
RUN groupadd -r dhafnck && useradd -r -g dhafnck -s /bin/false dhafnck

# Create directories
WORKDIR /app
RUN mkdir -p /data /app/logs && \
    chown -R dhafnck:dhafnck /app /data

# Copy Python environment from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=builder /app/src /app/src
COPY --from=builder /app/README.md /app/

# Copy startup script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set proper ownership
RUN chown -R dhafnck:dhafnck /app

# Switch to non-root user
USER dhafnck

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server; \
                   server = create_dhafnck_mcp_server(); \
                   tools = server.get_tools(); \
                   print('Health check passed' if len(tools) > 0 else exit(1))"

# Default command
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "-m", "fastmcp.server.mcp_entry_point"] 