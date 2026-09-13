FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        minimap2 \
        samtools \
        seqkit \
        gzip \
        gawk \
        sed \
        diffutils \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------
# Python dependencies
#
# Copy dependency metadata BEFORE source code.
# This lets Docker reuse this expensive layer
# when only our Python source changes.
# -----------------------------------------
COPY pyproject.toml README.md ./

# pyproject.toml expects src/mitochime to exist,
# so create a temporary minimal package.
RUN mkdir -p src/mitochime && \
    touch src/mitochime/__init__.py && \
    pip install \
        --no-cache-dir \
        --default-timeout=1000 \
        --retries 10 \
        . && \
    rm -rf src

# CPU-only PyTorch
RUN pip install \
    --no-cache-dir \
    --default-timeout=1000 \
    --retries 10 \
    torch==2.14.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# -----------------------------------------
# Actual MitoChime application
# -----------------------------------------
COPY src/ src/
COPY scripts/ scripts/
COPY models/ models/

# Reinstall the real package,
# but dependencies are already present.
RUN pip install --no-cache-dir --no-deps .

ENTRYPOINT ["mitochime"]
