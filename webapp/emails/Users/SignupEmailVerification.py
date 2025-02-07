from flask import Flask, url_for, render_template, request, jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv
load_dotenv()
# app = Flask(__name__)

# Replace 'YOUR_SENDGRID_API_KEY' with your actual SendGrid API key
# app.config['SENDGRID_API_KEY'] = 'YOUR_SENDGRID_API_KEY'
# sg = SendGridAPIClient(app.config['SENDGRID_API_KEY'])

class SignupEmailVerification:
    @staticmethod
    def send_signup_verify_email_letter(to, subject, objUser):
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
        print("objUser.email_verification_code")
        print("objUser.email_verification_code")
        print(objUser.email_verification_code)
        _verification_url = url_for('auth.verify_email', _external=True)
        print("_verification_url")
        print("_verification_url")
        print(_verification_url)
        verification_url = f"{_verification_url}?id={objUser.id}&verification_code={objUser.email_verification_code}"
        # verification_url = f"{_verification_url}?email={objUser.email}&verification_code={objUser.email_verification_code}"

        # verification_url = url_for('auth.verify_email', email=objUser.email, verification_code=objUser.email_verification_code, _external=True)
        print("verification_url")
        print("verification_url")
        print(verification_url)
        html_content = render_template(
            'emails/Users/Account/SignupVerifyEmailLetter.html',
            objUser=objUser,
            email=objUser.email,
            verification_url=verification_url,
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


# def send_email():
#     to = request.form['recipient']
#     subject = request.form['subject']
#     objUser = {
#         'full_name': 'John Doe',  # Replace with actual user data
#         'email': 'john@example.com',
#         'email_verification_code': '123456'  # Replace with actual verification code
#     }

#     result = SignupEmailVerification.send_signup_verify_email_letter(to, subject, objUser)
#     return result

