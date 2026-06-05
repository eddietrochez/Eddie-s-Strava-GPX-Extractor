# Strava to Garmin GPX Downloader

A lightweight web application that interfaces with the Strava API to extract activity data streams and convert them into optimized GPX telemetry files ready for Garmin devices.

## 🛠️ Tech Stack
* **Language:** Python
* **Framework:** Flask
* **Deployment:** Render
* **Version Control:** Git & GitHub

## 🚀 Key Features
* **Strava OAuth:** Secure user authentication with the Strava API.
* **Stream Processing:** Extracts and processes raw telemetry data streams.
* **Garmin Compatible:** Generates standard, clean `.gpx` files.

## 💻 Local Setup

1. **Clone the repository:**
```bash
git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)
cd YOUR-REPO-NAME

Install dependencies:
pip install -r requirements.txt

Configure Environment Variables:
Create a .env file in the root folder and add your credentials:
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
FLASK_SECRET_KEY=your_secret_key

Run the app:
python app.py
