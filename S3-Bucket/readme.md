# S3 BUCKET WITH PYTHON BOTO3

## S3 BUCKET

### What is Amazon S3?
    Amazon Simple Storage Service (Amazon S3) is an object storage service that offers industry-leading scalability, data availability, security, and performance. Customers of all sizes and industries can use Amazon S3 to store and protect any amount of data for a range of use cases, such as data lakes, websites, mobile applications, backup and restore, archive, enterprise applications, IoT devices, and big data analytics. Amazon S3 provides management features so that you can optimize, organize, and configure access to your data to meet your specific business, organizational, and compliance requirements.

### What is bucket in S3?
    A bucket is a container for objects stored in Amazon S3. You can store any number of objects in a bucket and can have up to 100 buckets in your account.

# Installation of Boto3

    Use the package manager [pip](https://pypi.org/project/boto3/) to install Boto3.

```bash
$ pip install boto3
```

# Import boto3 and json

    import boto3
    import json

# Connection and Authentication of S3 with python boto3

    boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Upload data in S3 

    s3_client.put_object(Body=json.dumps(payload),Bucket=bucket_name,Key="file_name.json")

# Get data from S3

    object = s3_client.get_object(Bucket=bucket_name, Key="file_name.json")
	content = object['Body']
	body = json.loads(content.read())

# Delete data from S3

    s3_client.delete_object(Bucket=bucket_name, Key="file_name.json")

# Documentation

    For the complete study of amazon S3 bucket with python boto3 [S3 python](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)