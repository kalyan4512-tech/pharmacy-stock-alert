
pipeline {
    agent any

    environment {
        DOCKER = '/Users/rkalyan/.docker/bin/docker'
        AWS = '/Users/rkalyan/.local/bin/aws'
        AWS_REGION = 'us-east-1'
        EC2_INSTANCE = 'i-090065bd6065310a0'
        ECR_REPO = '724270903230.dkr.ecr.us-east-1.amazonaws.com/pharmacy-stock-alert'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/kalyan4512-tech/pharmacy-stock-alert.git'
            }
        }

        stage('Check Docker') {
            steps {
                sh '${DOCKER} --version'
                sh '${DOCKER} info'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '${DOCKER} build --platform linux/amd64 -t pharmacy-stock-alert ./app'
            }
        }

        stage('ECR Login') {
            steps {
                sh '''
                    ${AWS} ecr get-login-password --region ${AWS_REGION} |
                    ${DOCKER} login --username AWS --password-stdin ${ECR_REPO}
                '''
            }
        }

        stage('Push Image to ECR') {
            steps {
                sh '''
                    ${DOCKER} tag pharmacy-stock-alert:latest ${ECR_REPO}:latest
                    ${DOCKER} push ${ECR_REPO}:latest
                '''
            }
        }

        stage('Test Docker Image') {
            steps {
                sh '${DOCKER} images pharmacy-stock-alert'
            }
        }

        stage('Test AWS SSM') {
            steps {
                sh '${AWS} sts get-caller-identity'

                sh '''
                    ${AWS} ssm send-command \
                        --instance-ids ${EC2_INSTANCE} \
                        --document-name "AWS-RunShellScript" \
                        --parameters 'commands=["echo Jenkins to EC2 SSM working"]' \
                        --region ${AWS_REGION}
                '''
            }
        }

        stage('Deploy to EC2') {
            steps {
                script {
                    def commandId = sh(
                        script: """
                            ${AWS} ssm send-command \
                                --instance-ids ${EC2_INSTANCE} \
                                --document-name "AWS-RunShellScript" \
                                --parameters 'commands=["aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO}","docker pull ${ECR_REPO}:latest","docker stop pharmacy-stock-alert || true","docker rm pharmacy-stock-alert || true","docker run -d --name pharmacy-stock-alert -p 5001:5000 ${ECR_REPO}:latest"]' \
                                --region ${AWS_REGION} \
                                --query 'Command.CommandId' \
                                --output text
                        """,
                        returnStdout: true
                    ).trim()

                    echo "SSM Deployment Command ID: ${commandId}"

                    sh """
                        for i in {1..30}; do
                            STATUS=\$(${AWS} ssm get-command-invocation \
                                --command-id ${commandId} \
                                --instance-id ${EC2_INSTANCE} \
                                --region ${AWS_REGION} \
                                --query 'Status' \
                                --output text 2>/dev/null || echo Pending)

                            echo "Deployment status: \$STATUS"

                            if [ "\$STATUS" = "Success" ]; then
                                exit 0
                            fi

                            if [ "\$STATUS" = "Failed" ] || [ "\$STATUS" = "Cancelled" ] || [ "\$STATUS" = "TimedOut" ]; then
                                ${AWS} ssm get-command-invocation \
                                    --command-id ${commandId} \
                                    --instance-id ${EC2_INSTANCE} \
                                    --region ${AWS_REGION}
                                exit 1
                            fi

                            sleep 10
                        done

                        echo "Deployment timed out"
                        exit 1
                    """
                }
            }
        }

    }
}
