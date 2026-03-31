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
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip --quiet
                            pip install -r requirements.txt --quiet
                            echo "All dependencies installed."
                        '''
                    } else {
                        bat '''
                            python -m venv venv
                            call venv\\Scripts\\activate.bat
                            pip install --upgrade pip --quiet
                            pip install -r requirements.txt --quiet
                            echo All dependencies installed.
                        '''
                    }
                }
            }
        }

        stage('Lint') {
            steps {
                echo "========== STAGE 3: Lint =========="
                script {
                    if (isUnix()) {
                        sh '. venv/bin/activate && flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics'
                    } else {
                        bat 'call venv\\Scripts\\activate.bat && flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics'
                    }
                }
                echo "Lint check passed."
            }
        }

        stage('Unit Tests') {
            steps {
                echo "========== STAGE 4: Unit Tests =========="
                script {
                    if (isUnix()) {
                        sh '. venv/bin/activate && pytest tests/ -v --junitxml=test-results.xml --cov=app --cov-report=xml'
                    } else {
                        bat 'call venv\\Scripts\\activate.bat && pytest tests/ -v --junitxml=test-results.xml --cov=app --cov-report=xml'
                    }
                }
                echo "All unit tests passed."
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
                script {
                    if (isUnix()) {
                        sh '''
                            docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                            docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                        '''
                    } else {
                        bat """
                            docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                            docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                        """
                    }
                }
                echo "Docker image built: ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        stage('Deploy') {
            steps {
                echo "========== STAGE 6: Deploy =========="
                script {
                    if (isUnix()) {
                        sh '''
                            docker stop ${CONTAINER_NAME} 2>/dev/null || true
                            docker rm   ${CONTAINER_NAME} 2>/dev/null || true
                            docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:5000 --restart unless-stopped ${IMAGE_NAME}:latest
                            sleep 5
                            curl --fail http://localhost:${APP_PORT}/health && echo "Health check PASSED"
                        '''
                    } else {
                        bat """
                            docker stop ${CONTAINER_NAME} 2>nul || exit /b 0
                            docker rm   ${CONTAINER_NAME} 2>nul || exit /b 0
                            docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:5000 --restart unless-stopped ${IMAGE_NAME}:latest
                        """
                        sleep(5)
                        bat "curl --fail http://localhost:${APP_PORT}/health"
                    }
                }
            }
        }

        stage('Smoke Test') {
            steps {
                echo "========== STAGE 7: Smoke Test =========="
                script {
                    if (isUnix()) {
                        sh '''
                            curl --fail --silent http://localhost:${APP_PORT}/health
                            curl --fail --silent http://localhost:${APP_PORT}/clients
                            echo "Smoke tests passed."
                        '''
                    } else {
                        bat "curl --fail http://localhost:${APP_PORT}/health"
                        bat "curl --fail http://localhost:${APP_PORT}/clients"
                    }
                }
                echo "All endpoints responding correctly."
            }
        }
    }

    post {
        success {
            echo "=========================================="
            echo "BUILD & DEPLOY SUCCESSFUL"
            echo "App running at http://localhost:${APP_PORT}"
            echo "Build #${env.BUILD_NUMBER} completed."
            echo "=========================================="
        }
        failure {
            echo "BUILD FAILED — cleaning up container."
            script {
                if (isUnix()) {
                    sh "docker stop ${CONTAINER_NAME} 2>/dev/null || true"
                } else {
                    bat "docker stop ${CONTAINER_NAME} 2>nul || exit /b 0"
                }
            }
        }
        always {
            script {
                if (isUnix()) {
                    sh 'rm -rf venv || true'
                } else {
                    bat 'if exist venv rmdir /s /q venv'
                }
            }
            cleanWs()
        }
    }
}
