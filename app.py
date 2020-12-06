import os

from dotenv import load_dotenv, find_dotenv
from faker import Faker
from flask import Flask, jsonify, request
from flask_cors import CORS
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import SyncGrant

app = Flask(__name__)
CORS(app)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path, override=True)
fake = Faker()

@app.route('/token', methods=['GET'])
def randomToken():
    return generateToken(fake.user_name())


@app.route('/token', methods=['POST'])
def createToken():
    # Get the request json or form data
    content = request.get_json() or request.form
    # get the identity from the request, or make one up
    identity = content.get('identity', fake.user_name())
    return generateToken(identity)


@app.route('/token/<identity>', methods=['POST', 'GET'])
def token(identity):
    return generateToken(identity)


def generateToken(identity):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    api_key = os.environ['TWILIO_API_KEY']
    api_secret = os.environ['TWILIO_API_SECRET']
    sync_service_sid = os.environ['TWILIO_SYNC_SERVICE_SID']

    token = AccessToken(account_sid, api_key, api_secret)
    token.identity = identity

    sync_grant = SyncGrant(service_sid=sync_service_sid)
    token.add_grant(sync_grant)
    token = token.to_jwt().decode('utf-8')
    return jsonify(identity=identity, token=token)



def provision_sync_default_service():
    client = Client(os.environ['TWILIO_API_KEY'], os.environ['TWILIO_API_SECRET'], os.environ['TWILIO_ACCOUNT_SID'])
    client.sync.services('default').fetch()


if __name__ == '__main__':
    provision_sync_default_service()
    app.run(debug=True, host='0.0.0.0', port=5001)
