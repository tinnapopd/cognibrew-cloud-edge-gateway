#!/usr/bin/env bash

set -x
set -eo pipefail

if ! [ -x "$(command -v docker)" ]; then
    echo >&2 "Error: Docker is not installed."
    exit 1
fi

# RustFS / MinIO settings – override via environment variables
S3_ACCESS_KEY=${S3_ACCESS_KEY:-rustfsadmin}
S3_SECRET_KEY=${S3_SECRET_KEY:-rustfsadmin}
S3_PORT=${S3_PORT:-9000}
S3_CONSOLE_PORT=${S3_CONSOLE_PORT:-9001}
S3_BUCKET_NAME=${S3_BUCKET_NAME:-cognibrew-raw}

# Launch RustFS (MinIO-compatible) using Docker
# Use: SKIP_DOCKER=1 ./scripts/init_rustfs.sh
if [[ -z "${SKIP_DOCKER}" ]]; then
    # Remove any previous rustfs container
    docker rm -f rustfs || true
    docker run \
        --name rustfs \
        -e RUSTFS_ROOT_USER=$S3_ACCESS_KEY \
        -e RUSTFS_ROOT_PASSWORD=$S3_SECRET_KEY \
        -p $S3_PORT:9000 \
        -p $S3_CONSOLE_PORT:9001 \
        -d rustfs/rustfs:latest \
        server /data --console-address ":9001"
fi

# Wait for RustFS to be ready
until curl -sf "http://localhost:${S3_PORT}/minio/health/live"; do
    >&2 echo "RustFS is still unavailable - sleeping"
    sleep 1
done

>&2 echo "RustFS is up and running on port $S3_PORT!"

# Create the default bucket using mc (MinIO Client)
if [ -x "$(command -v mc)" ]; then
    mc alias set local "http://localhost:${S3_PORT}" "$S3_ACCESS_KEY" "$S3_SECRET_KEY"
    mc mb --ignore-existing "local/${S3_BUCKET_NAME}"
    >&2 echo "Bucket '${S3_BUCKET_NAME}' is ready!"
else
    >&2 echo "Warning: 'mc' (MinIO Client) not found. Install it to auto-create buckets."
    >&2 echo "  brew install minio/stable/mc"
    >&2 echo "Or create the bucket manually via the console at http://localhost:${S3_CONSOLE_PORT}"
fi