pipeline {
    agent any

    environment {
        DOCKER = '/Users/rkalyan/.docker/bin/docker'
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
    }
}
