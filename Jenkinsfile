pipeline {
    options {
        buildDiscarder(logRotator(numToKeepStr: '7', artifactNumToKeepStr: '7'))
    }
    environment{
        HOME = "${env.WORKSPACE}"
        CODECOV_TOKEN = credentials("codecov.io-torrent-tracker-scraper")
    }
    agent {
        docker {
            image 'python:3.8-slim-buster' 
            args '-u root:sudo -v $HOME/workspace/torrent-tracker-scraper:/torrent-tracker-scraper'
        }
    }
    stages {
        stage('Install') { 
            steps {
                sh('python --version')
                sh('pip install --user pipenv')
                sh '$HOME/.local/bin/pipenv lock --dev --requirements > requirements.txt' 
                sh 'pip install --user -r requirements.txt'
                sh 'apt-get update -y'
                sh 'apt install curl -y'
            }
        }
         stage('Test') { 
            steps {
                sh 'python -m pytest --cov=torrent_tracker_scraper/ --cov-report xml' 
            }
        }
        stage('Upload Coverage badge') { 
            steps {
                sh 'curl -s https://codecov.io/bash | bash -s'
            }
        }
        stage('Upload to PyPi') { 
            environment {
                TWINE_USERNAME = credentials('twine-username')
                TWINE_PASSWORD = credentials('twine-password')
            }
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh 'python setup.py sdist bdist_wheel' 
                    sh 'twine upload dist/*'
                }
            }
        }
    }
}
