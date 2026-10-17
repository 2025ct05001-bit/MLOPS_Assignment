pipeline {
    agent any

    environment {
        // Define global variables for the pipeline
        IMAGE_NAME = 'heart-disease-api'
        IMAGE_TAG = "v${BUILD_NUMBER}"
        NAMESPACE = 'heart-disease'
        RELEASE_NAME = 'heart-disease-release'
    }

    stages {
        stage('Unit Testing (CI)') {
            steps {
                echo 'Running automated tests...'
                sh '''
                    # Create a temporary virtual environment for testing
                    python3 -m venv .jenkins-venv
                    source .jenkins-venv/bin/activate
                    
                    # Install testing dependencies from your root requirements file
                    pip install -r requirements.txt fastapi "uvicorn[standard]" pydantic pytest httpx
                    
                    # Execute the pytest suite
                    pytest test_app.py -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building container image ${IMAGE_NAME}:${IMAGE_TAG}..."
                // Build the image using Jenkins' dynamic BUILD_NUMBER as the tag
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Push to Minikube Cache') {
            steps {
                echo 'Loading image into local Minikube cluster...'
                // Replaces a traditional 'docker push' to a remote registry
                sh "minikube image load ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        stage('Deploy to Kubernetes (CD)') {
            steps {
                echo 'Upgrading Helm release with zero downtime...'
                // Use --set to dynamically inject the new Jenkins build tag into your values.yaml
                sh """
                    helm upgrade ${RELEASE_NAME} ./heart-disease-api-chart \\
                        --namespace ${NAMESPACE} \\
                        --set image.tag=${IMAGE_TAG}
                """
            }
        }
    }

    post {
        success {
            echo "Deployment successful! ${IMAGE_NAME}:${IMAGE_TAG} is live."
        }
        failure {
            echo "Pipeline failed. Please check the stage logs for errors."
        }
        always {
            // Clean up the temporary test environment
            sh 'rm -rf .jenkins-venv'
        }
    }
}