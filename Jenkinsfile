pipeline {
    agent any

    environment {
        AWS_REGION     = 'us-east-1'
        EC2_INSTANCE   = 'i-090065bd6065310a0'
        ECR_REPO       = '724270903230.dkr.ecr.us-east-1.amazonaws.com/pharmacy-stock-alert'
        APP_IMAGE_NAME = 'pharmacy-stock-alert'
        HOST_PORT      = '5001'
        CONTAINER_PORT = '5000'
        PATH           = "/opt/homebrew/bin:/usr/local/bin:/Users/rkalyan/.local/bin:/Users/rkalyan/.docker/bin:${env.PATH}"
    }

    stages {

        stage('Stage 1: Checkout') {
            steps {
                echo "Fetching latest source code from GitHub repository..."
                git branch: 'main',
                    url: 'https://github.com/kalyan4512-tech/pharmacy-stock-alert.git'
            }
        }

        stage('Stage 2: Validate') {
            steps {
                echo "Validating Python syntax and running automated unit tests..."
                sh '''
                    # Detect python3 binary
                    PYTHON_BIN=$(which python3 || echo "/opt/homebrew/bin/python3")
                    echo "Using Python binary: ${PYTHON_BIN}"
                    ${PYTHON_BIN} --version

                    # Check syntax of all Python source files
                    ${PYTHON_BIN} -m py_compile app/app.py app/database.py app/alerts.py app/models.py tests/test_alerts.py tests/test_app.py
                    echo "Python syntax verification passed successfully."

                    # Run unit tests in virtual environment or using pytest
                    if [ -f ".venv/bin/pytest" ]; then
                        .venv/bin/pytest tests/ -v
                    else
                        ${PYTHON_BIN} -m pip install -q -r app/requirements.txt pytest
                        ${PYTHON_BIN} -m pytest tests/ -v
                    fi
                '''
            }
        }

        stage('Stage 3: Docker Build') {
            steps {
                echo "Building Docker container image for linux/amd64 platform..."
                sh '''
                    DOCKER_BIN=$(which docker || echo "/Users/rkalyan/.docker/bin/docker")
                    echo "Using Docker: ${DOCKER_BIN}"
                    ${DOCKER_BIN} --version

                    # Build linux/amd64 production image
                    ${DOCKER_BIN} build --platform linux/amd64 -t ${APP_IMAGE_NAME}:latest ./app
                '''
            }
        }

        stage('Stage 4: ECR Authentication') {
            steps {
                echo "Authenticating Docker with Amazon ECR (${AWS_REGION})..."
                sh '''
                    AWS_BIN=$(which aws || echo "/usr/local/bin/aws")
                    DOCKER_BIN=$(which docker || echo "/Users/rkalyan/.docker/bin/docker")

                    echo "Testing AWS CLI identity..."
                    ${AWS_BIN} sts get-caller-identity

                    echo "Logging into Amazon ECR registry: ${ECR_REPO}..."
                    ${AWS_BIN} ecr get-login-password --region ${AWS_REGION} | \
                        ${DOCKER_BIN} login --username AWS --password-stdin ${ECR_REPO}
                '''
            }
        }

        stage('Stage 5: Push Image to ECR') {
            steps {
                echo "Tagging and pushing Docker image to Amazon ECR..."
                sh '''
                    DOCKER_BIN=$(which docker || echo "/Users/rkalyan/.docker/bin/docker")

                    ${DOCKER_BIN} tag ${APP_IMAGE_NAME}:latest ${ECR_REPO}:latest
                    ${DOCKER_BIN} tag ${APP_IMAGE_NAME}:latest ${ECR_REPO}:build-${BUILD_NUMBER}

                    echo "Pushing ${ECR_REPO}:latest..."
                    ${DOCKER_BIN} push ${ECR_REPO}:latest

                    echo "Pushing ${ECR_REPO}:build-${BUILD_NUMBER}..."
                    ${DOCKER_BIN} push ${ECR_REPO}:build-${BUILD_NUMBER}
                '''
            }
        }

        stage('Stage 6: Deployment to EC2 via AWS SSM') {
            steps {
                script {
                    echo "Deploying container to Amazon EC2 (${EC2_INSTANCE}) via AWS Systems Manager..."
                    def deployScript = """
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO}
                        docker pull ${ECR_REPO}:latest
                        mkdir -p /home/ec2-user/pharmacy-data && chmod 777 /home/ec2-user/pharmacy-data
                        docker stop ${APP_IMAGE_NAME} || true
                        docker rm ${APP_IMAGE_NAME} || true
                        docker run -d --name ${APP_IMAGE_NAME} --restart unless-stopped -p ${HOST_PORT}:${CONTAINER_PORT} -v /home/ec2-user/pharmacy-data:/app/data ${ECR_REPO}:latest
                    """.trim()

                    def commandId = sh(
                        script: """
                            AWS_BIN=\$(which aws || echo "/usr/local/bin/aws")
                            \${AWS_BIN} ssm send-command \
                                --instance-ids ${EC2_INSTANCE} \
                                --document-name "AWS-RunShellScript" \
                                --comment "Deploy MedStock PRO build ${BUILD_NUMBER}" \
                                --parameters 'commands=["aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO}","docker pull ${ECR_REPO}:latest","mkdir -p /home/ec2-user/pharmacy-data && chmod 777 /home/ec2-user/pharmacy-data","docker stop ${APP_IMAGE_NAME} || true","docker rm ${APP_IMAGE_NAME} || true","docker run -d --name ${APP_IMAGE_NAME} --restart unless-stopped -p ${HOST_PORT}:${CONTAINER_PORT} -v /home/ec2-user/pharmacy-data:/app/data ${ECR_REPO}:latest"]' \
                                --region ${AWS_REGION} \
                                --query 'Command.CommandId' \
                                --output text
                        """,
                        returnStdout: true
                    ).trim()

                    echo "AWS SSM Deployment Command ID: ${commandId}"

                    // Poll SSM execution until success or failure
                    sh """
                        AWS_BIN=\$(which aws || echo "/usr/local/bin/aws")
                        for i in {1..30}; do
                            STATUS=\$(\${AWS_BIN} ssm get-command-invocation \
                                --command-id ${commandId} \
                                --instance-id ${EC2_INSTANCE} \
                                --region ${AWS_REGION} \
                                --query 'Status' \
                                --output text 2>/dev/null || echo Pending)

                            echo "Deployment execution status: \${STATUS} (check \$i/30)"

                            if [ "\${STATUS}" = "Success" ]; then
                                echo "Remote container deployment succeeded on EC2."
                                exit 0
                            fi

                            if [ "\${STATUS}" = "Failed" ] || [ "\${STATUS}" = "Cancelled" ] || [ "\${STATUS}" = "TimedOut" ]; then
                                echo "ERROR: SSM Deployment command execution failed."
                                \${AWS_BIN} ssm get-command-invocation \
                                    --command-id ${commandId} \
                                    --instance-id ${EC2_INSTANCE} \
                                    --region ${AWS_REGION}
                                exit 1
                            fi

                            sleep 6
                        done

                        echo "ERROR: SSM Deployment command timed out."
                        exit 1
                    """
                }
            }
        }

        stage('Stage 7: Verification') {
            steps {
                echo "Verifying application container health on EC2..."
                sh '''
                    AWS_BIN=$(which aws || echo "/usr/local/bin/aws")

                    VERIFY_CMD_ID=$(${AWS_BIN} ssm send-command \
                        --instance-ids ${EC2_INSTANCE} \
                        --document-name "AWS-RunShellScript" \
                        --comment "Verify Health Endpoint" \
                        --parameters 'commands=["docker ps --filter name=pharmacy-stock-alert","curl -s -f http://127.0.0.1:5001/health || (sleep 3 && curl -s -f http://127.0.0.1:5001/health)"]' \
                        --region ${AWS_REGION} \
                        --query 'Command.CommandId' \
                        --output text)

                    echo "Verification Command ID: ${VERIFY_CMD_ID}"

                    for i in {1..15}; do
                        STATUS=$(${AWS_BIN} ssm get-command-invocation \
                            --command-id ${VERIFY_CMD_ID} \
                            --instance-id ${EC2_INSTANCE} \
                            --region ${AWS_REGION} \
                            --query 'Status' \
                            --output text 2>/dev/null || echo Pending)

                        if [ "${STATUS}" = "Success" ]; then
                            echo "Health check verification SUCCESSFUL on EC2!"
                            ${AWS_BIN} ssm get-command-invocation \
                                --command-id ${VERIFY_CMD_ID} \
                                --instance-id ${EC2_INSTANCE} \
                                --region ${AWS_REGION} \
                                --query 'StandardOutputContent' \
                                --output text
                            exit 0
                        fi

                        if [ "${STATUS}" = "Failed" ] || [ "${STATUS}" = "Cancelled" ]; then
                            echo "Health check verification FAILED on EC2."
                            ${AWS_BIN} ssm get-command-invocation \
                                --command-id ${VERIFY_CMD_ID} \
                                --instance-id ${EC2_INSTANCE} \
                                --region ${AWS_REGION}
                            exit 1
                        fi

                        sleep 4
                    done
                '''
            }
        }

        stage('Stage 8: Deployment Summary') {
            steps {
                script {
                    def publicIp = sh(
                        script: """
                            AWS_BIN=\$(which aws || echo "/usr/local/bin/aws")
                            \${AWS_BIN} ec2 describe-instances \
                                --instance-ids ${EC2_INSTANCE} \
                                --region ${AWS_REGION} \
                                --query "Reservations[0].Instances[0].PublicIpAddress" \
                                --output text 2>/dev/null || echo "13.223.206.23"
                        """,
                        returnStdout: true
                    ).trim()

                    echo """
                    ======================================================================
                     PHARMACY MEDICINE STOCK ALERT SYSTEM — DEPLOYMENT SUMMARY
                    ======================================================================
                     Status:           SUCCESS
                     Build Number:     ${BUILD_NUMBER}
                     ECR Image Tag:    ${ECR_REPO}:latest & build-${BUILD_NUMBER}
                     EC2 Instance:     ${EC2_INSTANCE} (${AWS_REGION})
                     Public IP:        ${publicIp}
                     Application URL:  http://${publicIp}:${HOST_PORT}
                     Health Endpoint:  http://${publicIp}:${HOST_PORT}/health
                     Database Storage: Persistent Volume (/home/ec2-user/pharmacy-data)
                    ======================================================================
                    """.stripIndent()
                }
            }
        }

    }

    post {
        success {
            echo "Pipeline completed successfully. MedStock PRO is live!"
        }
        failure {
            echo "Pipeline failed. Review the console logs above for diagnostics."
        }
    }
}
