from flask import Flask,request
from s3_bucket import GetS3JsonFile

app = Flask(__name__)


@app.route("/get_data_from_s3_bucket")
def get_data():
    number = request.args.get('mobile_number')
    data = GetS3JsonFile()
    respons = data.get_object(number)
    return {"data":respons}

@app.route("/data_uploade",methods=['POST'])
def post_data():
    data = request.get_json()
    uploade_function = GetS3JsonFile()
    uploade_function.move_data_to_s3(data["data"])
    return {"Message":"uploaded successfully"}

@app.route("/data_remove",methods=['DELETE'])
def delete_data():
    number = request.args.get('mobile_number')
    uploade_function = GetS3JsonFile()
    uploade_function.remove_file_from_s3(number)
    return {"Message":"Deleted successfully"}