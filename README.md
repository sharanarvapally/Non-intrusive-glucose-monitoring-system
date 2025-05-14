This project is a web-based dashboard for a non-invasive glucose monitoring system that uses simulated sensor data. It provides real-time glucose predictions, user login support, downloadable reports, and a history of readings.

## 🚀 Features

- 📈 Real-time glucose prediction using a trained XGBoost model
- 🧠 Machine Learning pipeline using `xgb_glucose_model.pkl` and `scaler.pkl`
- 🔐 User authentication via Flask-Login
- 🧾 Automatic PDF report generation and download
- 📬 Email alerts and report delivery via Gmail SMTP
- 📊 History view of previous reports and glucose values

## 🗂️ Project Structure

```

glucose\_dashboard/
├── app.py                  # Main Flask application
├── models.py               # Database models
├── scaler.pkl              # Scaler for preprocessing inputs
├── xgb\_glucose\_model.pkl   # Trained XGBoost model
├── simulated\_glucose\_monitoring\_data.csv  # Sample input data
├── instance/
│   └── glucose.db          # SQLite database
├── static/
│   └── reports/            # Generated PDF reports
├── templates/
│   ├── dashboard.html      # Dashboard UI
│   └── history.html        # History page UI

````

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sharanarvapally/Non-intrusive-glucose-monitoring-system.git
   cd Non-intrusive-glucose-monitoring-system/glucose_dashboard


2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**

   ```bash
   python app.py
   ```

5. **Access the dashboard**

   * Open your browser and go to `http://127.0.0.1:5000`

## 🧪 Tech Stack

* Python, Flask
* SQLite
* XGBoost
* HTML/CSS (Jinja templates)
* SMTP (Gmail) for email automation

## 📬 Email Setup

To enable email features, configure your Gmail credentials (or app password) securely using environment variables or a configuration file.

## 🧠 Future Improvements

* Real sensor integration (e.g., with Raspberry Pi or ESP32)
* User role management (admin/patient)
* Mobile-responsive dashboard UI
* Live charts with real-time updates



## 📄 License

This project is licensed under the MIT License.

```

---
