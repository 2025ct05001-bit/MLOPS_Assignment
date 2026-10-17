pipeline {
    // This tells Jenkins not to run everything on the host, but to wait for stage-level instructions
    agent none 

    environment {
        IMAGE_NAME = 'heart-disease-api'
        IMAGE_TAG = "v${BUILD_NUMBER}"
        NAMESPACE = 'heart-disease'
        RELEASE_NAME = 'heart-disease-release'
    }

    stages {
        stage('Unit Testing (CI)') {
            agent {
                docker {
                    // Spins up a clean, isolated Python environment just for this stage
                    image 'python:3.11-slim'
                    args '-u root'
                }
            }
            steps {
                echo 'Running automated tests inside an isolated Python container...'
                sh '''
                    # No virtual environment needed here because the entire container is our environment!
                    pip install --no-cache-dir -r requirements.txt fastapi "uvicorn[standard]" pydantic pytest httpx prometheus-fastapi-instrumentator
                    
                    export MODEL_PATH="model_export"
                    pytest test_app.py -v
                '''
            }
        }

        stage('Build Docker Image') {
            agent {
                docker {
                    image 'docker:cli'
                    // Add '-u root' before the socket mount
                    args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                echo "Building container image ${IMAGE_NAME}:${IMAGE_TAG}..."
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Push to Minikube Cache') {
            // We run this ONE command on your Mac natively. Minikube is a Mac VM manager, 
            // so running its CLI from inside a Linux container breaks certificate paths.
            agent any
            steps {
                echo 'Loading image into local Minikube cluster...'
                sh "minikube image load ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        stage('Deploy to Kubernetes (CD)') {
            agent {
                docker {
                    image 'alpine/helm:3.14.0'
                    // Maps your Mac's Kubernetes certificates into the Helm container 
                    // using the exact same file paths so Helm can authenticate securely.
                    args '-v /Users/goutham/.kube:/Users/goutham/.kube -v /Users/goutham/.minikube:/Users/goutham/.minikube -e KUBECONFIG=/Users/goutham/.kube/config'
                }
            }
            steps {
                echo 'Upgrading Helm release with zero downtime...'
                sh """
                    helm upgrade ${RELEASE_NAME} ./heart-disease-api-chart \\
                        --namespace ${NAMESPACE} \\
                        --set image.repository=${IMAGE_NAME} \\
                        --set image.tag=${IMAGE_TAG}
                """
            }
        }
    }
}