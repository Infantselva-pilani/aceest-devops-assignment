pipeline {
    agent any

    environment {
        IMAGE_NAME = "aceest-fitness"
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        PYTHON_VERSION = "3.11"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out source code from GitHub..."
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    echo "Dependencies installed successfully."
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . venv/bin/activate
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                    echo "Lint check passed."
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest tests/ -v --junitxml=test-results.xml --cov=app --cov-report=xml
                    echo "All tests passed."
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                    echo "Docker image built: ${IMAGE_NAME}:${IMAGE_TAG}"
                '''
            }
        }

        stage('Docker Test') {
            steps {
                sh '''
                    docker run -d --name aceest-jenkins-test -p 5001:5000 ${IMAGE_NAME}:latest
                    sleep 5
                    curl --fail http://localhost:5001/health || (docker logs aceest-jenkins-test && exit 1)
                    docker stop aceest-jenkins-test
                    docker rm aceest-jenkins-test
                    echo "Container health check passed."
                '''
            }
        }

        stage('Cleanup') {
            steps {
                sh '''
                    rm -rf venv
                    echo "Build environment cleaned up."
                '''
            }
        }
    }

    post {
        success {
            echo "BUILD SUCCESSFUL - ACEest Fitness pipeline completed for build #${env.BUILD_NUMBER}"
        }
        failure {
            echo "BUILD FAILED - Check the logs above for details."
        }
        always {
            cleanWs()
        }
    }
}
