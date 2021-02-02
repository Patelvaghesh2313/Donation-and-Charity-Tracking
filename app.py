from flask import render_template, request, redirect, url_for, flash, g, session, current_app
from passlib.hash import sha256_crypt
from datetime import datetime, date
from models import *
from sqlalchemy import text
from web3 import Web3
import os
import json
import secrets
import smtplib
from email.message import EmailMessage
#------------EMAIL CONFIGURATION-----------------#
EMAIL_ADDRESS = 'kingpatel8122@gmail.com'
EMAIL_PASSWORD = '347676747926vir'

msg = EmailMessage()
#--------------END EMAIL CONFIGURATION------------#

app = Flask(__name__)
app.secret_key = 'charitySystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2313@localhost/CharitySystem'
profileFolder = os.path.join('static', 'profileImages')
app.config['UPLOAD_PROFILE_IMAGE_FOLDER'] = profileFolder
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

abi = json.loads('[{"constant":true,"inputs":[],"name":"getBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"amt","type":"int256"}],"name":"sendEther","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[],"name":"getOwner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"functionCalled","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]')
contract_address = web3.toChecksumAddress("0x60e121864013430b1526f65bC20417DD2ECb53F0")


contract = web3.eth.contract(address=contract_address, abi=abi)
db.init_app(app)

now = datetime.now()


######################## HERE WE MAKE THE ROUTE OF ALL URLS#############
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", user=session['user'])


############################  LOGIN MODULE   #########################


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        session.pop('user', None)
        return render_template("login.html")
    else:
        session.pop('user', None)
        username = request.form.get("username")
        password = request.form.get("password")
        myUser = User.query.filter_by(email=username).first()
        if username == 'admin' and password == 'admin@123':
            session['user'] = 'admin'
            return redirect(url_for('admin'))
        elif myUser == None:
            flash("User Does Not Exist ",'danger')
            return redirect(url_for('login'))
        else:
            if sha256_crypt.verify(password, myUser.password):
                session['user'] = username
                all_user = User.query.all()
                return redirect(url_for('dashboard', users=all_user))
            else:
                flash("Incorrect Username And Password !",'danger')
                return redirect(url_for('login'))
    return render_template("error.html")
############################  END OF LOGIN MODULE  #########################

############################  SIGN-UP MODULE  #########################


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == "GET":
        session.pop('user', None)
        return render_template("sign_in.html")
    else:
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        country = request.form.get("country")
        occupation = request.form.get("occupation")
        birthday = request.form.get("birthday")
        email = request.form.get("email")
        phone = request.form.get("phone")
        image = save_images(request.files.get('image'))
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        secure_password = sha256_crypt.encrypt(str(password))
        register_user = User.query.filter_by(email=email).first()
        if register_user:
            if register_user.email == email:
                return redirect(url_for('sign_in'))
        else:
            if password == confirm_password:
                user = User(firstname=firstname, lastname=lastname, country=country, occupation=occupation, birthday=birthday,
                            email=email, phone=phone, image=image, password=secure_password)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                flash("Password does not match", 'danger')
                return redirect(url_for('sign_in'))

############################  END OF SIGN-UP MODULE #########################


@app.route('/charity_Details')
def charity_Details():
    if g.user:
        data = Charity.query.all()
        return render_template("charity_details.html",charities = data)
    return render_template("error.html")


@app.route('/charity_Details/<int:id>')
def specific_charity(id):
    if g.user:
        specific_charity = Charity.query.filter_by(id=id).first()
        return render_template("specific_charity_detail.html",data=specific_charity)


@app.route('/past_transactions')
def past_transactions():
    if g.user:
        donation = Donation.query.filter_by(donor_email=g.user).all()
        return render_template("past_transactions.html", data=donation)
    return render_template("error.html")


@app.route('/past_transactions/donate',methods=['POST'])
def donate():
    if g.user:
        account_1 = contract.functions.getOwner().call()
        account_2 = request.form.get("to")
        privatekey = request.form.get("privatekey")
        amount = request.form.get("amount")
        transaction_time = now.strftime("%H:%M:%S")
        today = date.today()
        nance = web3.eth.getTransactionCount(account_1)
        tx = {
            'nonce': nance,
            'to': account_2,
            'value': web3.toWei(amount, 'ether'),
            'gas': 2000000,
            'gasPrice': web3.toWei('50', 'gwei')
        }

        signed_tx = web3.eth.account.signTransaction(tx, privatekey)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        has = web3.toHex(tx_hash)

        donation = Donation( sender=account_1, reciever=account_2, donor_email=g.user, transaction_id=has, transaction_amount=amount,
                            transaction_time=transaction_time, transaction_date=today)
        db.session.add(donation)
        db.session.commit()



        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()

            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            subject = 'Your Transaction Details'
            body = 'Hello ' + g.user + '\n\nTransaction Id: ' + has + '\nReciever Id: ' + account_2 + '\nAmount :' + amount +'\n\nThank You.'
            msg = f'Subject: {subject}\n\n{body}'
            smtp.sendmail(EMAIL_ADDRESS, g.user, msg)
        return redirect(url_for('charity_Details'))
    render_template("error.html")


@app.route('/contact_us')
def contact_us():
    if g.user:
        return render_template("contact_us.html")
    return render_template("error.html")


@app.route('/contact_us/send', methods=['POST'])
def send_msg():
    if g.user:
        username = session['user']
        myUser = User.query.filter_by(email=username).first()
        subject = request.form.get("subject")
        message = request.form.get("message")
        send_date = date.today()
        send_time = now.strftime("%H:%M:%S")
        image = myUser.image
        suggestion = Suggestion(email=g.user, image=image, subject=subject, message=message, time=send_time,
                                date=send_date)
        db.session.add(suggestion)
        db.session.commit()
        return redirect(url_for('contact_us'))
    return render_template("error.html")


@app.route('/profile')
def profile():
    if g.user:
        username = session['user']
        session['today'] = date.today()
        myUser = User.query.filter_by(email=username).first()
        return render_template("profile.html", user=myUser)
    return render_template("error.html")


@app.route('/profile/<int:id>', methods=['POST'])
def update_profile(id):
    if g.user:
        if request.method == 'POST':
            my_data = User.query.get(request.form.get('id'))
            my_data.firstname = request.form['firstname']
            my_data.lastname = request.form['lastname']
            my_data.country = request.form['country']
            my_data.occupation = request.form['occupation']
            my_data.birthday = request.form['birthday']
            my_data.email = request.form['email']
            my_data.phone = request.form['phone']
            my_data.image = my_data.image
            my_data.password = my_data.password
            db.session.commit()
            flash("Profile Updated Successfully", 'success')
            return redirect(url_for('profile'))
    return render_template("error.html")


@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template("index.html")


############################ ADMIN-PART #############################


@app.route('/admin')
def admin():
    if session['user'] == 'admin':
        total_users = User.query.count()
        total_posts = Charity.query.count()
        total_donation = Donation.query.count()
        total_suggestion = Suggestion.query.count()
        return render_template("admin_dashboard.html", user=session['user'],total_users=total_users,total_posts=total_posts, total_donation=total_donation, total_suggestion=total_suggestion)
    return render_template("error.html")

############################ USER DETAILS PART #############################


@app.route('/user_details')
def user_details():
    if session['user'] == 'admin':
        all_user = User.query.all()
        return render_template("admin_user_details.html", users=all_user)
    return render_template("error.html")


@app.route('/user_details/add_user', methods=['POST'])
def add_user():
    if session['user'] == 'admin':
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        country = request.form.get("country")
        occupation = request.form.get("occupation")
        birthday = request.form.get("birthday")
        email = request.form.get("email")
        phone = request.form.get("phone")
        image = save_images(request.files.get('image'))
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        secure_password = sha256_crypt.encrypt(str(password))
        register_user = User.query.filter_by(email=email).first()
        if register_user:
            if register_user.email == email:
                flash("User Already Exist", 'danger')
                return redirect(url_for('user_details'))
        else:
            if password == confirm_password:
                user = User(firstname=firstname,lastname=lastname,country=country,occupation=occupation,birthday=birthday,email=email
                            ,phone=phone,image=image,password=secure_password)
                db.session.add(user)
                db.session.commit()
                flash("User Inserted Successfully",'success')
                return redirect(url_for('user_details'))
            else:
                flash("Password Does Not Match", 'danger')
                return redirect(url_for('user_details'))
    else:
        return render_template("error.html")


@app.route('/user_details/update_user', methods=['POST'])
def update_user():
    if session['user'] == 'admin':
        if request.method == 'POST':
            my_data = User.query.get(request.form.get('id'))
            my_data.firstname = request.form['firstname']
            my_data.lastname = request.form['lastname']
            my_data.country = request.form['country']
            my_data.occupation = request.form['occupation']
            my_data.birthday = request.form['birthday']
            my_data.email = request.form['email']
            my_data.phone = request.form['phone']
            my_data.image = my_data.image
            my_data.password = my_data.password
            db.session.commit()
            flash("User Updated Successfully",'success')
            return redirect(url_for('user_details'))
    else:
        return render_template("error.html")


@app.route('/delete_user/<id>', methods=['GET', 'POST'])
def delete_user(id):
    my_data = User.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("User Deleted Successfully",'danger')
    return redirect(url_for('user_details'))
############################ END OF USER DETAILS PART #############################

#############SAVE THE IMAGE HERE WE MAKE ONE FUNCTION###################


def save_images(image):
    hash_photo = secrets.token_urlsafe(10)
    _, file_extension = os.path.splitext(image.filename)
    photo_name = hash_photo + file_extension
    file_path = os.path.join(current_app.root_path, 'static/pics', photo_name)
    image.save(file_path)
    return photo_name


########################END OF SAVE IMAGE FUNCTION######################

############################ CHARITY DETAILS PART #############################

@app.route('/charity_details')
def charity_details():
    if session['user'] == 'admin':
        all_charity = Charity.query.all()
        return render_template("admin_charity_details.html",charities = all_charity)
    return render_template("error.html")


@app.route('/charity_details/add_charity', methods=['POST'])
def add_charity():
    if session['user'] == 'admin':
        title = request.form.get('title')
        content = request.form.get('content')
        image = save_images(request.files.get('image'))
        pub_date = request.form.get('pub_date')

        addCharity = Charity(title=title,content=content,image=image,pub_time=pub_date)
        db.session.add(addCharity)
        db.session.commit()
        flash("Charity Added Successfully",'success')
        return redirect(url_for('charity_details'))
    return render_template("error.html")


@app.route('/delete_charity/<id>', methods=['GET', 'POST'])
def delete_charity(id):
    my_data = Charity.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Charity Deleted Successfully",'success')
    return redirect(url_for('charity_details'))


@app.route('/transaction_details')
def transaction_details():
    if session['user'] == 'admin':
        all_transaction = Donation.query.all()
        return render_template("admin_transaction_details.html",donations = all_transaction)
    return render_template("error.html")

@app.route('/user_suggestions')
def admin_inbox():
    if session['user'] == 'admin':
        all_suggestion = Suggestion.query.all()
        return render_template("admin_inbox.html",suggestion = all_suggestion)
    return render_template("error.html")


############################ END OF CHARITY DETAILS PART #############################


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

#################### END OF ADMIN PART ########################


if __name__ == '__main__':
    app.run()
