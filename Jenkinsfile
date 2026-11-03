pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/kalyan4512-tech/pharmacy-stock-alert.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t pharmacy-stock-alert ./app'
            }
        }

        stage('Test') {
            steps {
                sh 'docker images pharmacy-stock-alert'
            }
        }
    }
}
