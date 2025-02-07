# from flask import Flask, jsonify
import os
import sendgrid

def get_sendgrid():
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    return sg
# app = Flask(__name__)

# class SendGridHelper:

#     @staticmethod
#     def get_sendgrid():
#         sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
#         return sg
# @app.route('/')
# def index():
#     # Example usage of SendGridHelper
#     sendgrid_helper = SendGridHelper()
#     sendgrid_instance = sendgrid_helper.get_sendgrid()

#     # Your further logic using sendgrid_instance can be added here
#     # ...

#     return jsonify({'message': 'SendGridHelper example'})

# if __name__ == '__main__':
#     app.run(debug=True)
