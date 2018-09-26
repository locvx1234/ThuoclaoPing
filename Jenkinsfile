pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'tox -e flake8'
            }
        }

        stage('Deploy') {
            steps {
                sh './rebuild_docker.sh'
            }
        }
    }
}
