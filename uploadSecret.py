
import sys
import json
import logging
import os
import boto3

AWS_REGION = os.environ.get("AWS_REGION", 'us-east-1')
PROJECTNAME = os.environ.get('PROJECT_NAME', 'myproject')
SERVICENAME = os.environ.get('SERVICE_NAME', 'test-svc')

# Create service client
SESSION = boto3.session.Session()
sts_client = SESSION.client("sts")
secretsmgr_client = SESSION.client("secretsmanager")

#Set logging preferences
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s: %(name)s-%(levelname)s: %(message)s'
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    account_env = str(sys.argv[1])
    with open(f'../iac/secrets.json', 'r') as config_l:
        _input = json.load(config_l)
    for input_db in _input["db_list"]:
        try:
            logger.info(f'Checking if secret exists for db - {input_db}')
            _db_exist = secretsmgr_client.describe_secret(
                SecretId = f'{input_db}-dbConfig'
            )
            logger.info(f'Secret exists for db - {input_db}. Response is - {_db_exist}')
        except secretsmgr_client.exceptions.ResourceNotFoundException:
            logger.info(f'Secret does not exist. Creating secret for db - {input_db}')
            _secret = secretsmgr_client.create_secret(
             Name = f'a{ASSETID}/deal-{_input["environment"]}/{input_db}.dbConfig',
             Description = 'Testing',
             SecretString = f'{{"db_type":"POSTGRES","username":"{input_db}","password":"{input_db}"}}',
            )			
            logger.info(f'Secret created successfully for db - {input_db}')
