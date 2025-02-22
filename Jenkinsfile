pipeline {
    agent any
    
    environment {
        AWS_REGION = 'ap-south-1'
        FUNCTION_NAME = 'sum-it-up'
        VENV_DIR = 'venv'
       PYTHON_BIN = '/opt/homebrew/bin/python3.11'  
    }

    stages {
        
        stage('Checkout Code') {
            steps {
                git branch: 'master', url: 'https://github.com/CloudCraftLabs/Sum-it-Up-Python.git'
            }
        }

        stage('Create Virtual Environment') {
            steps {
                script {
                    sh '${PYTHON_BIN} -m venv ${VENV_DIR}'
                }
            }
        }

        stage('Activate Virtual Environment & Install Dependencies') {
            steps {
                script {
                    sh '''
                    source ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r dependencies.py
                    '''
                }
            }
        }

        stage('Package Lambda Function') {
            steps {
                script {
                    sh '''
                    source ${VENV_DIR}/bin/activate
                    cd ${WORKSPACE} && zip -r function.zip *
                    '''
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
