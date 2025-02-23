pipeline {
    agent any
    
    environment {
        AWS_REGION = 'ap-south-1' //AWS Region
        FUNCTION_NAME = 'sum-it-up' //AWS Lambda Func name
        VENV_DIR = 'venv' //Virtual env name
       PYTHON_BIN = '/opt/homebrew/bin/python3.11'  //locall path for python 3.11
        AWS_CLI = '/opt/homebrew/bin/aws' //AWS CLI path
        TIMESTAMP = new Date().format("yyyyMMdd-HHmmss", TimeZone.getTimeZone("UTC")) //Timestamp
        LAYER_NAME = 'sum-it-up-layer' //AWS Lambda Layer name
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
                    pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Package Lambda Layer') {
            steps {
                script {
                    sh '''
                    mkdir -p python/lib/python3.11/site-packages
                    cp -r ${VENV_DIR}/lib/python3.11/site-packages/* python/lib/python3.11/site-packages/
                    zip -r layer.zip python
                    '''
                }
            }
        }

        stage('Upload Lambda Layer') {
            steps {
                script {
                    sh '''
                    LAYER_VERSION=$(${AWS_CLI} lambda publish-layer-version --layer-name ${LAYER_NAME} --zip-file fileb://layer.zip --compatible-runtimes python3.11 --query Version --output text)
                    echo "LAYER_VERSION=$LAYER_VERSION" > layer_version.txt
                    '''
                }
            }
        }

        stage('Package Lambda Function') {
            steps {
                script {
                    sh '''
                    source ${VENV_DIR}/bin/activate
                    zip -r function.zip *
                    '''
                }
            }
        }

        stage('Deploy Lambda Function') {
            steps {
                script {
                    sh '''
                    ${AWS_CLI} lambda update-function-code --function-name ${FUNCTION_NAME} --zip-file fileb://function.zip --region ${AWS_REGION}
                    '''
                }
            }
        }

        stage('Update Lambda Configuration') {
            steps {
                script {
                    sh '''
                    LAYER_VERSION=$(cat layer_version.txt)
                    ${AWS_CLI} lambda update-function-configuration --function-name ${FUNCTION_NAME} --layers arn:aws:lambda:${AWS_REGION}:123456789012:layer:${LAYER_NAME}:$LAYER_VERSION
                    '''
                }
            }
        }

        stage('Publish Lambda Version') {
            steps {
                script {
                    sh '''
                    VERSION=$(${AWS_CLI} lambda publish-version --function-name ${FUNCTION_NAME} --query Version --output text)
                    echo "VERSION=$VERSION" > lambda_version.txt
                    '''
                }
            }
        }

        stage('Update Alias') {
            steps {
                script {
                    sh '''
                    VERSION=$(cat lambda_version.txt)
                    ${AWS_CLI} lambda update-alias --function-name ${FUNCTION_NAME} --name latest --function-version $VERSION
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Deployment successful! Lambda and Layer versioning completed.'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
