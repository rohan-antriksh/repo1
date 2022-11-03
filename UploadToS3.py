import json
import logging
import os
import boto3
from botocore.exceptions import ClientError
import zipfile
from os.path import basename

AWS_REGION = os.environ.get("AWS_REGION", 'us-east-1')
PROJECTNAME = os.environ.get("PROJECTNAME",'myproject')
SERVICENAME = os.environ.get('SERVICE_NAME', 'test-svc')

# Create service client
s3_client = boto3.client("s3")
s3_resource = boto3.resource('s3')

TMP = '/tmp'

#Set logging preferences
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s: %(name)s-%(levelname)s: %(message)s'
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def not_exist(s3_bucket, file_key):
    try:
        print(f'check if file {file_key} exists....')
        file_details = s3_resource.Object(s3_bucket, file_key).get()
        print(file_details)
        return False
    except ClientError as e:
        if e.response['Error']['Code'] == "NoSuchKey":
            print(f'File - {file_key} does not exist.')
            return True
        return False

def handler(event, context):

    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    print(f"Received event - {sns_message}")

    # Process event to get source_id
    source_id_full = sns_message["SourceId"]    
    if source_id_full.startswith(f'{PROJECTNAME}-{SERVICENAME}') :
        print(f"Found source id {source_id}")

        if env == "uat" or env == "prod":
            s3_bucket = "prod-us-east-1-s3"
        else:
            s3_bucket = "preprod-us-east-1-s3"

        try:

                f = open(f"{TMP}/{source_id}.txt", "w+")
                f.write(source_id)
                f.close()

                #Check if zip file already exists in s3
                check_zip_not_exist = not_exist(s3_bucket, f'{env}/mytest-{source_id}.zip')
                if check_zip_not_exist is True:
                    print("Creating zip file..")
                    zipObj = zipfile.ZipFile(f"{TMP}/mytest-{source_id}.zip", "w")
                    zipObj.write(f"{TMP}/{source_id}.txt",f"{source_id}.txt")
                    zipObj.close()
                else:
                    print("Uploading file to existing zip file.")
                    s3_client.download_file(s3_bucket, f'{env}/mytest-{source_id}.zip', f'{TMP}/mytest-{source_id}.zip')
                    zipObj = zipfile.ZipFile(f"{TMP}/mytest-{source_id}.zip", "a")
					zipObj.write(f"{TMP}/{source_id}.txt", f"{source_id}.txt")
					zipObj.close()
                       
                s3_client.upload_file(f"{TMP}/mytest-{source_id}.zip", s3_bucket, f"{env}/mytest-{source_id}.zip", ExtraArgs={'ACL': 'bucket-owner-full-control'})
                print(f"File has been uploaded.")

        except ClientError as e:
            logging.error(e)
    else:
        print(f"SourceId does not start with expected string. Exiting.")
