# Install project
$ python3.9 -m virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt

# Run localy
$ uvicorn app:app --port 8001 --debug

# Prerequisites
// Install aws-cli and setup accessKey and secretKey
// Follow below url to install on local computer. Only need to refer "Install the AWS SAM CLI" section from below document.
// https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install-linux.html

# Deploy on lambda server 
$ sam build
$ sam deploy