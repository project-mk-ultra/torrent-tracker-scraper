pipeline {
    options {
        buildDiscarder(logRotator(numToKeepStr: '7', artifactNumToKeepStr: '7'))
    }
    environment{
        CODECOV_TOKEN = credentials("codecov.io-torrent-tracker-scraper")
        HOME = "${env.WORKSPACE}"
        TWINE_USERNAME    = credentials('twine-username')
        TWINE_PASSWORD = credentials('twine-password')
    }
    agent {
        docker {
            image 'python:3.8-slim-buster' 
            args '-u root:sudo -v $HOME/workspace/torrent-tracker-scraper:/torrent-tracker-scraper'
        }
    }
    stages {
        stage('Install system-wide dependencies') { 
            steps {
                sh 'apt-get update -y'
                sh 'apt install curl git -y'   
            }
        }
        stage('Install Python dependencies') { 
            steps {
                sh('python --version')
                sh('pip install --user pipenv')
                sh '$HOME/.local/bin/pipenv lock --dev --requirements > requirements.txt' 
                sh 'pip install --user -r requirements.txt'
            }
        }
        stage('Test') { 
            steps {
                sh 'python -m pytest --cov=torrent_tracker_scraper/ --cov-report xml' 
            }
        }
        stage('Generate changelog') { 
            environment {
                VERSION = """${sh(
                returnStdout: true,
                script: 'python -m bump'
                )}"""
            }
            when {
                branch "develop"
            }
            steps {
                sh 'echo ${VERSION}'
                sh 'git config user.name jenkins'
                sh 'git config user.email kenokech94@gmail.com'
                sh 'git stash save setup.py'
                sh 'git checkout develop'
                sh 'git stash pop'
                sh 'git add CHANGELOG.md setup.py'
                sh 'python -m gitchangelog.gitchangelog > CHANGELOG.md ^3.1.4 HEAD'
                sh 'git commit -am "chg: doc: bump to ${VERSION}"'
                sh 'git tag -f ${VERSION}'
                withCredentials([usernamePassword(credentialsId: 'github-torrent-tracker-scraper', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                    sh('git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/project-mk-ultra/torrent-tracker-scraper.git') 
                    sh('git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/project-mk-ultra/torrent-tracker-scraper.git --tags')
                }
            }
        }
        stage('Upload coverage badge') { 
            steps {
                sh 'curl -s https://codecov.io/bash | bash -s'
            }
        }
        stage('Upload to PyPi') { 
            when {
                branch "master"
            }
            steps {
                sh 'python setup.py sdist bdist_wheel' 
                sh 'twine upload dist/*'
            }
        }
    }
}
