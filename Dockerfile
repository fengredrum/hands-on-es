# Stage 1: Builder/Compiler
FROM python:3.6-slim AS compile-image

# Update and install packages
RUN apt update && apt upgrade -y && \
    apt install --no-install-recommends -y gcc gcc-multilib && \
    apt clean && rm -rf /var/lib/apt/lists/*
# Install dependencies
COPY requirements.txt /
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir --user -r /requirements.txt

# Stage 2: Runtime
FROM python:3.6-slim AS runtime-image
COPY --from=compile-image /root/.local /root/.local
# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH
