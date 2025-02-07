from flask import Flask, url_for, render_template, request, jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
# app = Flask(__name__)
from dotenv import load_dotenv
load_dotenv()
# Replace 'YOUR_SENDGRID_API_KEY' with your actual SendGrid API key
# app.config['SENDGRID_API_KEY'] = 'YOUR_SENDGRID_API_KEY'
# sg = SendGridAPIClient(app.config['SENDGRID_API_KEY'])

class ForgotPasswordEmail:
    @staticmethod
    def send_forgot_password_email_letter(to, subject, objUser):
        print("to")
        print("to")
        print(to)
        print("subject")
        print("subject")
        print(subject)
        print("objUser")
        print("objUser")
        print(objUser)
        print("objUser.email")
        print("objUser.email")
        print(objUser.email)
        _reset_url = url_for('auth.password_reset', _external=True)
        print("_reset_url")
        print("_reset_url")
        print(_reset_url)
        reset_url = f"{_reset_url}?id={objUser.id}&password_reset_token={objUser.password_reset_token}"
        # reset_url = f"{_reset_url}?email={objUser.email}&password_reset_token={objUser.password_reset_token}"

        # reset_url = url_for('auth.verify_email', email=objUser.email, password_reset_token=objUser.password_reset_token, _external=True)
        print("reset_url")
        print("reset_url")
        print(reset_url)
        html_content = render_template(
            'emails/Users/Account/ForgotPasswordEmailLetter.html',
            objUser=objUser,
            email=objUser.email,
            reset_url=reset_url,
            logo='http://fireecologyplants.net/images/logo.png'
        )
        # print("html_content")
        # print("html_content")
        # print(html_content)
        message = Mail(
            from_email=os.getenv('MAIL_FROM'),  # Replace with your email address
            # from_email='j.ferrer@fireecologyplants.net',  # Replace with your email address
            to_emails=to,
            subject=subject,
            html_content=html_content
        )
        # message = Mail(
        #     # from_email='j.ferrer@unsw.edu.au',fireecologyplants.net
        #     from_email='j.ferrer@fireecologyplants.net',
        #     to_emails='usamamashkoor@gmail.com',
        #     subject='This is test emailssssssssssss',
        #     html_content='<strong>Hi Usama</strong>'
        # )
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        try:
            responseEmail = sg.send(message)
            print("responseEmail")
            print("responseEmail")
            print(responseEmail)
            print("responseEmail.status_code")
            print("responseEmail.status_code")
            print(responseEmail.status_code)
            print("responseEmail.body")
            print("responseEmail.body")
            print(responseEmail.body)
            print("responseEmail.headers")
            print("responseEmail.headers")
            print(responseEmail.headers)
            return {"success": True, "message": "Email sent successfully"}
        except Exception as e:
            print("error in sending email")
            print("error in sending email")
            print(e)
            return {"success": False, "message": f"Error: {str(e)}"}