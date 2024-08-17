import json
import os
import hvac

vault_url = os.environ["VAULT_URL"]
vault_namespace = os.environ["VAULT_NAMESPACE"]
vault_path = os.environ["VAULT_PATH"]
vault_token = os.environ["VAULT_TOKEN"]

client = hvac.Client(url=vault_url, token=vault_token, namespace=vault_namespace)

response = client.secrets.kv.read_secret_version(path=vault_path)

credentials = json.loads(response['data']['data']['echofind_config'])
private_key = json.loads(response['data']['data']['private_key'])

# S3 Connection
aws_access_key_id = credentials["aws_access_key_id"]
aws_secret_access_key = credentials["aws_secret_access_key"]
aws_bucket_name = credentials["aws_bucket_name"]

# ES Connection
es_hosts = credentials["es_hosts"]
es_api_key = credentials["es_api_key"]


firebase_api_key = credentials["firebase_api_key"]
firebase_auth_domain = credentials["firebase_auth_domain"]
firebase_project_id = credentials["firebase_project_id"]
firebase_storage_bucket = credentials["firebase_storage_bucket"]
firebase_messaging_sender_id = credentials["firebase_messaging_sender_id"]
firebase_app_id = credentials["firebase_app_id"]
