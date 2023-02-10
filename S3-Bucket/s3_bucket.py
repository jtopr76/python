import boto3
import json
import datetime
 
class S3Auth:
	''' 
			create Authentication for access the s3 bucket 
	'''
	def __init__(self, obj=None):
		self.aws_access_key_id = 'AWS_ACCESS_KEY_ID'
		self.aws_secret_access_key = 'AWS_SECRET_ACCESS_KEY'
		self.bucket_name = 'BUCKET_NAME'
		self.s3_client = boto3.client(
			's3', aws_access_key_id=self.aws_access_key_id, 
			aws_secret_access_key=self.aws_secret_access_key)

class UpdateS3JsonFile(S3Auth):
	def __init__(self,payload, key):
		S3Auth.__init__ (self)
		self.s3_client.put_object(
				Body=json.dumps(payload),
				Bucket=self.bucket_name,
				Key=key)


class GetS3JsonFile(S3Auth):


	def __init__(self):
		'''
  		Inherit the S3Auth class for used the authentication access_key,access_id
		first call the get_object function inside  __init__ method.
    	'''
		S3Auth.__init__ (self)


	def get_object(self, key):
		key1 = self.get_key(key)
		try:
			object = self.s3_client.get_object(Bucket=self.bucket_name, Key=key1)
			content = object['Body']
			body = json.loads(content.read())
		except Exception as e:
			body = None
		return body

	
	def get_key(self,mobile_number):
		return "{}.json".format(mobile_number)


	def move_data_to_s3(self,data):
		key = data['mobile_number']
		body = self.get_object(key)
		if body:
			body['payload'].extend(data.get('payload'))
			UpdateS3JsonFile(body,
				self.get_key(data.get("mobile_number"))
            )
		else:
			UpdateS3JsonFile(data,
				self.get_key(data.get("mobile_number"))
            )


	def remove_file_from_s3(self,number):
		key = self.get_key(number)	
		self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)


class GetS3data(S3Auth):
	def __init__(self, key):
		S3Auth.__init__ (self)
		data = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
		print(data['Body'].read())
    
	def s3_client(self,key):
		data = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
   