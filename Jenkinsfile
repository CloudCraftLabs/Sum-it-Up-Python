pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'  // Set your AWS region
        FUNCTION_NAME = 'sum-it-up'  // AWS Lambda function name
        REPO_URL = 'https://github.com/CloudCraftLabs/Sum-it-Up-Python.git'  // GitHub repository
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'master', url: "${REPO_URL}"
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r dependencies.py -t .'
            }
        }

        stage('Package Code') {
            steps {
                sh 'zip -r function.zip . -x "*.git*"'
            }
        }

        stage('Deploy to AWS Lambda') {
            steps {
                withAWS(credentials: 'aws-credentials-id', region: "${AWS_REGION}") {
                    sh '''
                    aws lambda update-function-code --function-name $FUNCTION_NAME --zip-file fileb://function.zip --region $AWS_REGION
                    '''
                }
            }
        }

        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
    }

    post {
        success {
            echo "Deployment to AWS Lambda was successful!"
        }
        failure {
            echo "Deployment failed. Check logs for details."
        }
    }
}
