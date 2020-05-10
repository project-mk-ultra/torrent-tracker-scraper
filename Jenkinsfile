pipeline {
    options {
        buildDiscarder(logRotator(numToKeepStr: '7', artifactNumToKeepStr: '7'))
    }
    agent {
        docker {
            image 'python:3.8-slim-buster' 
        }
    }
    stages {
        stage('Install') { 
            steps {
                sh('pip install pipenv')
                sh 'pipenv lock --requirements > requirements.txt' 
                sh 'pip install -r requirements.txt'
            }
        }
         stage('Test') { 
            steps {
                sh 'pytest' 
            }
        }
    }
}