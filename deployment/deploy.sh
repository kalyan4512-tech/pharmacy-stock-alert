#!/usr/bin/env bash
# ==============================================================================
# MedStock PRO — EC2 Automated Deployment Script
# Executed via AWS SSM Run Command or Direct Host Runner
# ==============================================================================

set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO="${ECR_REPO:-724270903230.dkr.ecr.us-east-1.amazonaws.com/pharmacy-stock-alert}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
CONTAINER_NAME="${CONTAINER_NAME:-pharmacy-stock-alert}"
HOST_PORT="${HOST_PORT:-5001}"
CONTAINER_PORT="${CONTAINER_PORT:-5000}"
HOST_DATA_DIR="${HOST_DATA_DIR:-/home/ec2-user/pharmacy-data}"

echo "=========================================================="
echo " Starting Pharmacy Stock Alert Deployment on EC2"
echo " Image: ${ECR_REPO}:${IMAGE_TAG}"
echo " Port: ${HOST_PORT}:${CONTAINER_PORT}"
echo " Host Persistent Volume: ${HOST_DATA_DIR}"
echo "=========================================================="

# 1. Ensure persistent database directory exists
mkdir -p "${HOST_DATA_DIR}"
chmod 777 "${HOST_DATA_DIR}"

# 2. Authenticate Docker with Amazon ECR
echo "[1/5] Authenticating Docker with Amazon ECR (${AWS_REGION})..."
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_REPO}"

# 3. Pull latest application image from ECR
echo "[2/5] Pulling latest image: ${ECR_REPO}:${IMAGE_TAG}..."
docker pull "${ECR_REPO}:${IMAGE_TAG}"

# 4. Stop and remove existing container if running
echo "[3/5] Gracefully stopping previous container if present..."
if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    docker stop "${CONTAINER_NAME}" || true
    docker rm "${CONTAINER_NAME}" || true
    echo "Previous container '${CONTAINER_NAME}' removed successfully."
fi

# 5. Start new container with persistent volume
echo "[4/5] Launching new application container..."
docker run -d \
    --name "${CONTAINER_NAME}" \
    --restart unless-stopped \
    -p "${HOST_PORT}:${CONTAINER_PORT}" \
    -v "${HOST_DATA_DIR}:/app/data" \
    "${ECR_REPO}:${IMAGE_TAG}"

# 6. Verify container health status
echo "[5/5] Verifying health check on localhost:${HOST_PORT}..."
HEALTH_SUCCESS=false
for i in {1..12}; do
    if curl -s -f "http://127.0.0.1:${HOST_PORT}/health" > /tmp/health_response.json 2>/dev/null; then
        echo "Health check succeeded! Response: $(cat /tmp/health_response.json)"
        HEALTH_SUCCESS=true
        break
    fi
    echo "Waiting for container startup (attempt $i/12)..."
    sleep 3
done

if [ "$HEALTH_SUCCESS" != "true" ]; then
    echo "ERROR: Container health check failed on localhost:${HOST_PORT}."
    docker logs --tail 50 "${CONTAINER_NAME}"
    exit 1
fi

echo "=========================================================="
echo " DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo " Application is live at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo '13.223.206.23'):${HOST_PORT}"
echo "=========================================================="

