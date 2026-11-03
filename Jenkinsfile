
pipeline {
    agent any

    environment {
        DOCKER = '/Users/rkalyan/.docker/bin/docker'
        AWS_REGION = 'us-east-1'
        EC2_INSTANCE = 'i-090065bd6065310a0'
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
                sh '${DOCKER} build -t pharmacy-stock-alert ./app'
            }
        }

        stage('Test') {
            steps {
                sh '${DOCKER} images pharmacy-stock-alert'
            }
        }

        stage('Test AWS SSM') {
            steps {
                sh 'aws sts get-caller-identity'

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
