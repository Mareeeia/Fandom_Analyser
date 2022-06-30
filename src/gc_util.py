# Imports the Google Cloud client library
from google.cloud import storage

# Instantiates a client
from src.params.folder_params import BUCKET_NAME


def init_storage():
    storage_client = storage.Client()

    bucket = storage_client.get_bucket(BUCKET_NAME)  # bucket names need to be globally unique
    return bucket


def upload_file(filename: str, cloud_file, bucket):
    if bucket is not None:
        blob = bucket.blob(cloud_file)
        blob.upload_from_filename(filename)
