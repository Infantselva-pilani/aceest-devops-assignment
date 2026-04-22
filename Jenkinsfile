pipeline {
    agent any

    environment {
        IMAGE_NAME      = "aceest-fitness"
        DOCKERHUB_USER  = "selva015"
        DOCKERHUB_IMAGE = "${DOCKERHUB_USER}/${IMAGE_NAME}"
        IMAGE_TAG       = "${env.BUILD_NUMBER}"
        CONTAINER_NAME  = "aceest-fitness-app"
        APP_PORT        = "5000"
        SONAR_HOST      = "http://localhost:9000"
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                echo "========== STAGE 1: Checkout =========="
                checkout scm
                echo "Source code checked out from GitHub."
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo "========== STAGE 2: Setup Python =========="
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate.bat
                    python -m pip install --upgrade pip --quiet
                    pip install -r requirements.txt --quiet
                    echo Dependencies installed successfully.
                '''
            }
        }

        stage('Lint') {
            steps {
                echo "========== STAGE 3: Lint =========="
                bat '''
                    call venv\\Scripts\\activate.bat
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                    echo Lint check passed.
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                echo "========== STAGE 4: Unit Tests =========="
                bat '''
                    call venv\\Scripts\\activate.bat
                    python -m pytest tests/ -v --junitxml=test-results.xml --cov=app --cov-report=xml
                    echo All unit tests passed.
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "========== STAGE 5: SonarQube Analysis =========="
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    bat """
                        call venv\\Scripts\\activate.bat
                        sonar-scanner ^
                          -Dsonar.projectKey=aceest-fitness ^
                          -Dsonar.sources=. ^
                          -Dsonar.exclusions=venv/**,tests/**,**/__pycache__/** ^
                          -Dsonar.python.coverage.reportPaths=coverage.xml ^
                          -Dsonar.host.url=${SONAR_HOST} ^
                          -Dsonar.token=%SONAR_TOKEN%
                        echo SonarQube analysis complete.
                    """
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo "========== STAGE 6: Docker Build =========="
                bat """
                    docker build -t ${DOCKERHUB_IMAGE}:${IMAGE_TAG} .
                    docker tag ${DOCKERHUB_IMAGE}:${IMAGE_TAG} ${DOCKERHUB_IMAGE}:latest
                    echo Docker image built: ${DOCKERHUB_IMAGE}:${IMAGE_TAG}
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo "========== STAGE 7: Push to Docker Hub =========="
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_TOKEN'
                )]) {
                    bat """
                        echo %DOCKER_TOKEN% | docker login -u %DOCKER_USER% --password-stdin
                        docker push ${DOCKERHUB_IMAGE}:${IMAGE_TAG}
                        docker push ${DOCKERHUB_IMAGE}:latest
                        echo Pushed to Docker Hub successfully.
                        docker logout
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                echo "========== STAGE 8: Deploy =========="
                bat """
                    docker stop ${CONTAINER_NAME} 2>nul
                    docker rm   ${CONTAINER_NAME} 2>nul
                    docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:5000 --restart unless-stopped ${DOCKERHUB_IMAGE}:latest
                    ping 127.0.0.1 -n 10 > nul
                    curl --retry 5 --retry-delay 3 --fail http://localhost:${APP_PORT}/health
                    echo Health check PASSED
                """
            }
        }

        stage('Smoke Test') {
            steps {
                echo "========== STAGE 9: Smoke Test =========="
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
            echo "BUILD AND DEPLOY SUCCESSFUL"
            echo "Image pushed: ${DOCKERHUB_IMAGE}:${IMAGE_TAG}"
            echo "App running at http://localhost:${APP_PORT}"
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
