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
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh('python --version')
                    sh('pip install --user pipenv')
                    sh '$HOME/.local/bin/pipenv lock --dev --requirements > requirements.txt' 
                    sh 'pip install --user -r requirements.txt'
                }
            }
        }
         stage('Test') { 
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh 'python -m pytest' 
                }
            }
        }
    }
}