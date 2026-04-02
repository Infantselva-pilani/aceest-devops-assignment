pipeline {
    agent any

    environment {
        IMAGE_NAME     = "aceest-fitness"
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = "aceest-fitness-app"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "========== STAGE 1: Checkout =========="
                checkout scm
                echo "Source code checked out successfully."
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo "========== STAGE 2: Setup Python =========="
                bat '''
                py -m venv venv
                call venv\\Scripts\\activate.bat
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
                echo "Python environment ready."
            }
        }

        stage('Lint') {
            steps {
                echo "========== STAGE 3: Lint =========="
                bat '''
                call venv\\Scripts\\activate.bat
                flake8 . || exit /b 0
                '''
                echo "Lint check completed."
            }
        }

        stage('Unit Tests') {
            steps {
                echo "========== STAGE 4: Unit Tests =========="
                bat '''
                call venv\\Scripts\\activate.bat
                pytest --junitxml=test-results.xml --cov=. --cov-report=xml
                '''
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
                bat '''
                docker build -t %IMAGE_NAME%:%IMAGE_TAG% .
                docker tag %IMAGE_NAME%:%IMAGE_TAG% %IMAGE_NAME%:latest
                '''
                echo "Docker image built successfully."
            }
        }

        stage('Deploy') {
            steps {
                echo "========== STAGE 6: Deploy =========="
                bat '''
                REM Stop and remove old container (ignore errors)
                docker stop %CONTAINER_NAME% 2>nul
                docker rm %CONTAINER_NAME% 2>nul

                REM Run new container
                docker run -d -p 5000:5000 --name %CONTAINER_NAME% %IMAGE_NAME%:latest

                REM Wait for app to start
                timeout /t 10

                REM Health check
                curl --fail http://localhost:5000/health
                '''
                echo "Deployment successful."
            }
        }

        stage('Smoke Test') {
            steps {
                echo "========== STAGE 7: Smoke Test =========="
                bat 'curl http://localhost:5000/health'
            }
        }
    }

    post {
        always {
            echo "Cleaning workspace..."
            bat 'if exist venv rmdir /s /q venv'
            cleanWs()
        }
        success {
            echo "BUILD SUCCESS"
        }
        failure {
            echo "BUILD FAILED - Check logs"
            bat 'docker stop %CONTAINER_NAME% 2>nul'
        }
    }
}
