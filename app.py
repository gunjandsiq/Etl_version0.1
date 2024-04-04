import boto3
from models import database
import sentry_sdk
from sentry_sdk import capture_exception
class S3_helper:
    def __init__(self):
        self.client_s3 = boto3.client('s3')

    # Returns a list of all buckets 
    def bucket_list_names(self):
        try:
            bucket_list = []
            response = self.client_s3.list_buckets()
            for bucket in response['Buckets']:
                bucket_list.append(bucket['Name'])
            database.add_record('s3','bucket_list_names',bucket_list)
            return bucket_list
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
    
    def create_s3_bucket(self, bucket_name):
        try:
            response = self.client_s3.create_bucket(
                Bucket = bucket_name,
            )
            print(response)
            database.add_record('s3','create_s3_bucket',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # retrieves metadata from an object without returning the object itself    
    def get_storage_class(self,bucket_name, file_key):
        try:
            response = self.client_s3.head_object(Bucket=bucket_name, Key=file_key)
            storage_class = response.get('StorageClass')
            database.add_record('s3','get_storage_class',storage_class)
            return storage_class
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Delete the object
    def delete_file_from_s3(self,bucket_name, file_key):
        try:
            response = self.client_s3.delete_object(Bucket=bucket_name, Key=file_key)
            database.add_record('s3','delete_file_from_s3',response)
            print(f"File '{file_key}' deleted successfully.")
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # def filter_bucket(self,bucket_name, min_date=None, max_date=None,report_type=None):
    #     try:
    #         response = self.client_s3.list_objects_v2(Bucket=bucket_name)
    #         file_names = []
    #         for obj in response['Contents']:
    #             if obj['Key'].startswith("BelSkai"):
    #                 date = obj['Key'].split('_')[1].split('.')[0]
    #                 origanal_report_type=obj['Key'].split('_')[0].replace("BelSkai","")
    #                 # Check if date is within the specified range
    #             if (min_date is None or date >= min_date) and (max_date is None or date <= max_date) and (report_type is None or origanal_report_type == report_type):
    #                 file_names.append(obj['Key'])
    #                 # print(obj['Key'])
    #         database.add_record('s3','filter_bucket',file_names)       
    #         return file_names
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #         capture_exception(e)
    #         return str(e)

    # Creates a copy of an object that is already stored in s3   
    def change_storage_class(self,bucket_name, file_key, new_storage_class):
        try:
            copy_source = {
                'Bucket': bucket_name,
                'Key': file_key
            }
            self.client_s3.copy_object(
                Bucket=bucket_name,
                CopySource=copy_source,
                Key=file_key,
                StorageClass=new_storage_class
            )
            print(
                f"Storage class of {file_key} changed to {new_storage_class}")
        except self.client_s3.exceptions.InvalidObjectState as e:
            print(f"An error occurred: {e}. \n The object may be in a state like GLACIER or Deep Archive so that does not allow direct modification.")
        except Exception as e:  
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
    
    # Returns all objects in a bucket   
    def objects_list(self,bucket_name): 
        try:
            response = self.client_s3.list_objects(
                Bucket = bucket_name
            )
            database.add_record('s3','objects_list',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)
        
    # Retrieves an object from s3    
    def get_object(self,bucket_name,file_key):
        try:
            response = self.client_s3.get_object(
                Bucket = bucket_name,
                Key = file_key 
            )
            database.add_record('s3','get_object',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Adds an object to a bucket    
    def put_object_in_s3(self,bucket_name,file_key):
        try:
            response = self.client_s3.put_object(
                Bucket = bucket_name,
                Key = file_key 
            )
            database.add_record('s3','put_object_in_s3',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Upload a file to an S3 object
    def upload_file_to_object(self,file_path,bucket_name,file_key):
        try:
            response = self.client_s3.upload_file(
                Filename = file_path,                                                 # The path to the file to upload
                Bucket = bucket_name,                                                 # The name of the bucket 
                Key = file_key                                                        # The name of the key
            )
            database.add_record('s3','upload_file_to_object',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)

    # Download an S3 object to a file    
    def download_object_to_file(self,bucket_name,file_key,file_path):
        try:
            response = self.client_s3.download_file(
                Bucket = bucket_name,                                                  # The name of the bucket to download from
                Key = file_key,                                                        # The name of the key
                Filename = file_path                                                   # The path to the file
            )
            database.add_record('s3','download_object_to_file',response)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            capture_exception(e)
            return str(e)