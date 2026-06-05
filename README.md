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

```bash
# 1. Clone the repository
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Environment Variables (.env)
# Create a .env file in the root folder and add your credentials:
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
FLASK_SECRET_KEY=your_secret_key

# 4. Run the application
python app.py
