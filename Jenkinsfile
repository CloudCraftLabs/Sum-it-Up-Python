pipeline {
    agent any
    
    environment {
        AWS_REGION = 'ap-south-1' //AWS Region
        FUNCTION_NAME = 'sum-it-up' //AWS Lambda Func name
        VENV_DIR = 'venv' //Virtual env name
       PYTHON_BIN = '/opt/homebrew/bin/python3.11'  //locall path for python 3.11
        TIMESTAMP = new Date().format("yyyyMMdd-HHmmss", TimeZone.getTimeZone("UTC")) //Timestamp
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

        stage('Publish New Version') {
            steps {
                script {
                    sh '''
                    LAMBDA_VERSION=$(aws lambda publish-version --function-name ${FUNCTION_NAME} --region ${AWS_REGION} --query 'Version' --output text)
                    echo "New Lambda Version: $LAMBDA_VERSION"
                    echo "LAMBDA_VERSION=$LAMBDA_VERSION" >> $GITHUB_ENV
                    '''
                }
            }
        }

        stage('Update Alias to Latest Version') {
            steps {
                script {
                    sh '''
                    ALIAS_NAME="prod-${TIMESTAMP}"  # Create recognizable alias name
                    echo "Using alias: $ALIAS_NAME"

                    aws lambda update-alias --function-name ${FUNCTION_NAME} --name $ALIAS_NAME --function-version $LAMBDA_VERSION --region ${AWS_REGION} || \
                    aws lambda create-alias --function-name ${FUNCTION_NAME} --name $ALIAS_NAME --function-version $LAMBDA_VERSION --region ${AWS_REGION}
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
