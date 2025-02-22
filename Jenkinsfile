pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'  // Set your AWS region
        FUNCTION_NAME = 'sum-it-up'  // AWS Lambda function name
        REPO_URL = 'https://github.com/CloudCraftLabs/Sum-it-Up-Python.git'  // GitHub repository
        PYTHON_VERSION = 'python3.9' //Python version
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'master', url: "${REPO_URL}"
            }
        }

        stage('Set Up Python 3.11') {
            steps {
                script {
                    sh 'sudo apt update && sudo apt install -y python3.9 python3.9-venv'
                }
            }
        }

        stage('Create Virtual Environment') {
            steps {
                script {
                    sh '${PYTHON_VERSION} -m venv ${VENV_DIR}'
                    sh 'source ${VENV_DIR}/bin/activate'
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh 'source ${VENV_DIR}/bin/activate && pip install -r requirements.txt'
                }
            }
        }

        stage('Package Lambda Function') {
            steps {
                script {
                    sh 'cd ${WORKSPACE} && zip -r function.zip *'
                }
            }
        }

        stage('Deploy to AWS Lambda') {
            steps {
                withAWS(credentials: 'aws-credentials-id', region: "${AWS_REGION}") {
                    sh '''
                    aws lambda update-function-code --function-name ${FUNCTION_NAME} --zip-file fileb://function.zip --region ${AWS_REGION}
                    '''
                }
            }
        }

    }

    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
