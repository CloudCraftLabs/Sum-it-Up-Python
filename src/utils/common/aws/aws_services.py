import boto3
import json
from src.config.data.params import params
from botocore.exceptions import ClientError
import base64
from src.utils.common.logger import logger


def initS3(awsRegion = ""):
    if awsRegion == "":
        awsRegion = params["AWSRegion"]
    s3client = boto3.client(
        's3',
        region_name=awsRegion
    )
    return s3client


def initSecretManager():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=params["AWSRegion"],
    )
    return client


def getDBSecretValue(dbtype):
    secret = ''
    secret_name = params['project-env']+'/db/'+dbtype
    print(secret_name)
    client = initSecretManager()
    
    try:
        get_secret_value_response = client.get_secret_value(
                        SecretId=secret_name
                    )
        logger.info(f"secret_name : {secret_name} get_secret_value_response : {get_secret_value_response}")
    except ClientError as e:
        print(e)
        if e.response['Error']['Code'] == 'AccessDeniedException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    return secret


def get_aws_s3_presigned_url_post(bucket_name, object_name, expiration=3600):
    response = {}
    try:
        s3_client = initS3(awsRegion=params.get('AWSRegion'))
        response = s3_client.generate_presigned_post(bucket_name, object_name, ExpiresIn=expiration)
    except Exception as e:
        raise e
    return response


def get_aws_s3_presigned_url_get(bucket_name, object_name, expiration=3600):
    response = {}
    try:
        s3_client = initS3(awsRegion=params.get('AWSRegion'))
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name, 'Key': object_name},
                                                ExpiresIn=expiration)
    except Exception as e:
        raise e
    return response
