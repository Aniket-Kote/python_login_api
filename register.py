from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import random
import mysql.connector
from flask_cors import CORS


from flask import Flask, request, jsonify, session
from flask_mail import Mail, Message
import random
import mysql.connector
import secrets



app = Flask(__name__)
CORS(app)

# Configure MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Default XAMPP username
    password="",  # Default XAMPP password is empty
    database="mydatabase"  # Replace with your database name
)
cursor = db.cursor()

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'askncapture0808@gmail.com'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'ebpj ktpi imcr iwtr'  # Replace with your Gmail password

app.secret_key = secrets.token_hex(16)  # Set a secret key for session management
mail = Mail(app)


# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    cnf_password = data.get('cnf_password')
    mobile_number = data.get('mobile_number')
    message=''
    if password==cnf_password:
        # Generate verification code
        verification_code = ''.join(random.choices('0123456789', k=6))

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()


        if existing_user:
            message="User already exist click on Login"
            statusCode=201
        else:
            # Insert user data into the database
            insert_query = "INSERT INTO users (first_name, last_name, email, password, mobile_number, verification_code) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (first_name, last_name, email, password, mobile_number, verification_code))
            db.commit()

            # Send verification email
            msg = Message('Email Verification', sender='askncapture0808@example.com', recipients=[email])
            msg.body = f'Your verification code is: {verification_code}'
            mail.send(msg)
            message='User registered successfully. Check your email for verification.'
            statusCode=200
    else:
        message="Password not matched Please recheck and submit"
        statusCode=400

    return jsonify({'message': message,'status':statusCode})

# Route for email verification
@app.route('/verify_email', methods=['POST'])
def verify_email():
    data = request.get_json()
    email = data.get('email')
    verification_code = data.get('verification_code')

    # Verify email and code against database
    select_query = "SELECT email FROM users WHERE email = %s AND verification_code = %s"
    cursor.execute(select_query, (email, verification_code))
    user = cursor.fetchone()

    if user:
        # Update user status to verified
        update_query = "UPDATE users SET verified = TRUE WHERE email = %s"
        cursor.execute(update_query, (email,))
        db.commit()
        return jsonify({'message': 'Email verified successfully.'}), 200
    else:
        return jsonify({'message': 'Invalid email or verification code.'}), 400





# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if user exists and password is correct
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()

    if user:
        # Create session for the user and generate a unique secret
        session['email'] = email
        session['secret'] = secrets.token_hex(16)  # Generate a 16-byte random token
        return jsonify({'message': 'Login successful.', 'secret': session['secret']}), 200
    else:
        return jsonify({'message': 'Invalid email or password.'}), 401

# Route for checking if user is logged in
@app.route('/check_login', methods=['GET'])
def check_login():
    if 'email' in session:
        return jsonify({'logged_in': True, 'email': session['email']}), 200
    else:
        return jsonify({'logged_in': False}), 401

# Route for user logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    session.pop('secret', None)
    return jsonify({'message': 'Logout successful.'}), 200





@app.route('/enterdata',methods=['POST'])
def enterdata():
    data=request.get_json()
    inputfield=data.get('inputfield')
    # message="You entered "+inputfield
    print(len(str(inputfield)))
    if len(str(inputfield))==0:
        message="Invalid data"
    elif len(str(inputfield))>0:
        message="Proceed"
    
    
    return jsonify({'message':message}),200 



if __name__ == '__main__':
    app.run(debug=True)




