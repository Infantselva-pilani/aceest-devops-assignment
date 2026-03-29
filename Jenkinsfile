pipeline {
    agent any

    environment {
        IMAGE_NAME    = "aceest-fitness"
        IMAGE_TAG     = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = "aceest-fitness-app"
        APP_PORT      = "5000"
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
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip --quiet
                    pip install -r requirements.txt --quiet
                    echo "All dependencies installed successfully."
                '''
            }
        }

        stage('Lint') {
            steps {
                echo "========== STAGE 3: Lint =========="
                sh '''
                    . venv/bin/activate
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                    echo "Lint check passed — no syntax errors found."
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                echo "========== STAGE 4: Unit Tests =========="
                sh '''
                    . venv/bin/activate
                    pytest tests/ -v --junitxml=test-results.xml --cov=app --cov-report=xml
                    echo "All unit tests passed."
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
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                    echo "Docker image built successfully: ${IMAGE_NAME}:${IMAGE_TAG}"
                    docker images ${IMAGE_NAME}
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "========== STAGE 6: Deploy =========="
                sh '''
                    # Stop and remove any existing container
                    docker stop ${CONTAINER_NAME} 2>/dev/null || true
                    docker rm   ${CONTAINER_NAME} 2>/dev/null || true

                    # Run the new container
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:5000 \
                        --restart unless-stopped \
                        ${IMAGE_NAME}:latest

                    echo "Container deployed. Waiting for startup..."
                    sleep 5

                    # Health check
                    curl --fail --silent http://localhost:${APP_PORT}/health \
                        && echo "Health check PASSED — app is running at http://localhost:${APP_PORT}" \
                        || (docker logs ${CONTAINER_NAME} && echo "Health check FAILED" && exit 1)
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                echo "========== STAGE 7: Smoke Test =========="
                sh '''
                    # Verify key endpoints respond correctly
                    echo "Testing /health endpoint..."
                    curl --fail --silent http://localhost:${APP_PORT}/health

                    echo ""
                    echo "Testing /clients endpoint..."
                    curl --fail --silent http://localhost:${APP_PORT}/clients

                    echo ""
                    echo "Smoke tests passed — all key endpoints are responding."
                '''
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
            echo "BUILD FAILED — stopping and removing container if running."
            sh '''
                docker stop ${CONTAINER_NAME}  2>/dev/null || true
                docker rm   ${CONTAINER_NAME}  2>/dev/null || true
            '''
        }
        always {
            sh 'rm -rf venv || true'
            cleanWs()
        }
    }
}
