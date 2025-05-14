from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import joblib
import numpy as np
import os
from reportlab.pdfgen import canvas

from models import db, User, Prediction

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///glucose.db'
db.init_app(app)

# Ensure reports directory exists
os.makedirs('static/reports', exist_ok=True)

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Mail setup
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sharanarvapally005@gmail.com'         # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_app_password_here'       # Replace with app password
mail = Mail(app)

# Load ML model and scaler
try:
    model = joblib.load('xgb_glucose_model.pkl')
    scaler = joblib.load('scaler.pkl')
except Exception as e:
    model, scaler = None, None
    print("Model loading error:", e)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email already registered.")
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if not model or not scaler:
            return "Model or Scaler not loaded properly. Please check server logs.", 500

        temp = float(request.form['temp'])
        sbp = float(request.form['sbp'])
        dbp = float(request.form['dbp'])
        hr = float(request.form['hr'])
        hrv = float(request.form['hrv'])

        input_features = np.array([[temp, sbp, dbp, hr, hrv]])
        input_scaled = scaler.transform(input_features)
        predicted_glucose = model.predict(input_scaled)[0]

        diagnosis = "Normal" if predicted_glucose < 100 else "Prediabetic" if predicted_glucose < 126 else "Diabetic"
        insulin_dose = max(0, (predicted_glucose - 100) / 50)

        prediction = Prediction(
            user_id=current_user.id,
            temperature=temp,
            sbp=sbp,
            dbp=dbp,
            heart_rate=hr,
            hrv=hrv,
            glucose=predicted_glucose,
            diagnosis=diagnosis,
            insulin_dose=insulin_dose,
            timestamp=datetime.now()
        )
        db.session.add(prediction)
        db.session.commit()

        # Generate PDF report
        filename = f"report_{prediction.id}.pdf"
        generate_pdf(prediction, filename)

        # Email PDF report
        try:
            msg = Message("Your Glucose Report", sender=app.config['MAIL_USERNAME'], recipients=[current_user.email])
            msg.body = "Attached is your recent glucose monitoring report."
            with app.open_resource(f"static/reports/{filename}") as fp:
                msg.attach(filename, "application/pdf", fp.read())
            mail.send(msg)
        except Exception as e:
            print("Email failed:", e)

        return render_template(
            'result.html',
            glucose=predicted_glucose,
            diagnosis=diagnosis,
            insulin=insulin_dose,
            prediction_id=prediction.id
        )

    return render_template('dashboard.html')

def generate_pdf(prediction, filename):
    pdf_path = os.path.join('static', 'reports', filename)
    c = canvas.Canvas(pdf_path)
    c.setFont("Helvetica", 14)
    c.drawString(100, 800, "Glucose Monitoring Report")
    c.drawString(100, 770, f"Date: {prediction.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(100, 740, f"Temperature: {prediction.temperature} °C")
    c.drawString(100, 720, f"Systolic BP: {prediction.sbp} mmHg")
    c.drawString(100, 700, f"Diastolic BP: {prediction.dbp} mmHg")
    c.drawString(100, 680, f"Heart Rate: {prediction.heart_rate} bpm")
    c.drawString(100, 660, f"HRV: {prediction.hrv} ms")
    c.drawString(100, 640, f"Predicted Glucose: {round(prediction.glucose, 2)} mg/dL")
    c.drawString(100, 620, f"Diagnosis: {prediction.diagnosis}")
    c.drawString(100, 600, f"Suggested Insulin Dose: {round(prediction.insulin_dose, 2)} units")
    c.save()

@app.route('/download/<int:report_id>')
@login_required
def download_report(report_id):
    filename = f"report_{report_id}.pdf"
    return redirect(url_for('static', filename=f'reports/{filename}'))

@app.route('/history')
@login_required
def history():
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.timestamp.desc()).all()
    return render_template('history.html', predictions=predictions)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
