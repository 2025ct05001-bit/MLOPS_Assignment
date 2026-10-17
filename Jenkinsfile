pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: python
    image: python:3.11-slim
    command: ['cat']
    tty: true
  - name: docker
    image: docker:cli
    command: ['cat']
    tty: true
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
  - name: helm
    image: alpine/helm:3.14.0
    command: ['cat']
    tty: true
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
'''
        }
    }

    environment {
        IMAGE_NAME = 'heart-disease-api'
        IMAGE_TAG = "v${BUILD_NUMBER}"
        NAMESPACE = 'heart-disease'
        RELEASE_NAME = 'heart-disease-release'
    }

    stages {
        stage('Unit Testing (CI)') {
            steps {
                // Route this step to the Python container
                container('python') {
                    echo 'Running automated tests...'
                    sh '''
                        python3 -m venv .jenkins-venv
                        . .jenkins-venv/bin/activate
                        pip install -r requirements.txt fastapi "uvicorn[standard]" pydantic pytest httpx prometheus-fastapi-instrumentator
                        # Set the model path so FastAPI loads the directory instead of the missing database
                        export MODEL_PATH="model_export"
                        pytest test_app.py -v
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                // Route this step to the Docker container
                container('docker') {
                    echo "Building container image ${IMAGE_NAME}:${IMAGE_TAG}..."
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        stage('Deploy to Kubernetes (CD)') {
            steps {
                // Route this step to the Helm container
                container('helm') {
                    echo 'Upgrading Helm release with zero downtime...'
                    sh """
                        helm upgrade ${RELEASE_NAME} ./heart-disease-api-chart \\
                            --namespace ${NAMESPACE} \\
                            --set image.tag=${IMAGE_TAG}
                    """
                }
            }
        }
    }

    post {
        always {
            container('python') {
                sh 'rm -rf .jenkins-venv || true'
            }
        }
    }
}