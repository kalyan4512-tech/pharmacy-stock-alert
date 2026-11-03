
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


        stage('Test') {
            steps {
                sh '${DOCKER} images pharmacy-stock-alert'
            }
        }

        stage('Test AWS SSM') {
            steps {
                sh '${AWS} sts get-caller-identity'

                sh '''
                    aws ssm send-command \
                        --instance-ids ${EC2_INSTANCE} \
                        --document-name "AWS-RunShellScript" \
                        --parameters 'commands=["echo Jenkins to EC2 SSM working"]' \
                        --region ${AWS_REGION}
                '''
            }
        }
    }
}
