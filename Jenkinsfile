pipeline {
    agent any

    environment {
        IMAGE_NAME     = "aceest-fitness"
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = "aceest-fitness-app"
        APP_PORT       = "5000"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "========== STAGE 1: Checkout =========="
                checkout scm
                echo "Source code checked out from GitHub successfully."
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo "========== STAGE 2: Setup Python =========="
                bat '''
                    py -m venv venv
                    call venv\\Scripts\\activate.bat
                    py -m pip install --upgrade pip --quiet
                    py -m pip install -r requirements.txt --quiet
                    echo All dependencies installed.
                '''
            }
        }

        stage('Lint') {
            steps {
                echo "========== STAGE 3: Lint =========="
                bat '''
                    call venv\\Scripts\\activate.bat
                    py -m flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                    echo Lint check passed.
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                echo "========== STAGE 4: Unit Tests =========="
                bat '''
                    call venv\\Scripts\\activate.bat
                    py -m pytest tests/ -v --junitxml=test-results.xml --cov=app --cov-report=xml
                    echo All unit tests passed.
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
                echo "========== STAGE 5: Docker Build =========="
                bat """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                    echo Docker image built: ${IMAGE_NAME}:${IMAGE_TAG}
                """
            }
        }

        stage('Deploy') {
            steps {
                echo "========== STAGE 6: Deploy =========="
                bat """
                    docker stop ${CONTAINER_NAME} 2>nul & exit /b 0
                    docker rm   ${CONTAINER_NAME} 2>nul & exit /b 0
                    docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:5000 --restart unless-stopped ${IMAGE_NAME}:latest
                """
                sleep(8)
                bat "curl --fail http://localhost:${APP_PORT}/health"
                echo "Health check PASSED — app is live at http://localhost:${APP_PORT}"
            }
        }

        stage('Smoke Test') {
            steps {
                echo "========== STAGE 7: Smoke Test =========="
                bat """
                    curl --fail http://localhost:${APP_PORT}/health
                    curl --fail http://localhost:${APP_PORT}/clients
                    echo Smoke tests passed.
                """
            }
        }
    }

    post {
        success {
            echo "=========================================="
            echo "BUILD AND DEPLOY SUCCESSFUL"
            echo "App is running at http://localhost:${APP_PORT}"
            echo "Build #${env.BUILD_NUMBER} completed."
            echo "=========================================="
        }
        failure {
            echo "BUILD FAILED - check logs above."
            bat "docker stop ${CONTAINER_NAME} 2>nul & exit /b 0"
        }
        always {
            bat 'if exist venv rmdir /s /q venv'
            cleanWs()
        }
    }
}
