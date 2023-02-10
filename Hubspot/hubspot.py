from flask import Blueprint, request, render_template
import requests
import os
import utils

hubspot_api = Blueprint('hubspot_api', __name__)

client_id=os.environ['client_id']
client_secret=os.environ['client_secret']
redirect_uri=os.environ['redirect_uri']

@hubspot_api.route('/authorization')
def authorization():

  formData = {
    "grant_type": 'authorization_code',
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": redirect_uri,
    "code": request.args.get("code")
  }

  try:
    res = requests.post("https://api.hubapi.com/oauth/v1/token", data=formData)
    refresh_token = res.json()['refresh_token']

    utils.save_refresh_token(refresh_token)

    return render_template('success.html')
  except Exception as e:
    print(e)
    return "Error"

def get_access_token():
  formData = {
    "grant_type": 'authorization_code',
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": redirect_uri,
    "refresh_token": utils.get_refresh_token()
  }

  try:
    res = requests.post("https://api.hubapi.com/oauth/v1/token", data=formData)
    return res.json()['access_token']
  except Exception as e:
    print(e)
    return "Error"

@hubspot_api.route('/ticket', methods=("POST", ))
def ticket():

  access_token = get_access_token()

  try:
    ticketId = request.json[0]['objectId'] if len(request.json) else ""

    headers = {
      "authorization": "Bearer "+access_token
    }
    res = requests.get("https://api.hubapi.com/crm/v3/objects/tickets/"+str(ticketId), headers=headers)
    
    utils.save_update_ticket(res.json())

  except Exception as e:
    print(e)
    return "Error"

  return {}