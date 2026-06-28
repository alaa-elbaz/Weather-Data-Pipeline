# 🌦️ Real-Time Weather Data Pipeline

An end-to-end Data Engineering project that automates the process of extracting, transforming, and loading (ETL) weather data into a containerized database, with a live interactive dashboard for visualization.

## 📌 Project Overview
This project demonstrates a complete ETL pipeline. It fetches real-time weather metrics (Temperature, Humidity, Wind Speed) for Cairo from the Open-Meteo API, processes the data using Python, and stores it in a PostgreSQL database managed by Docker. Finally, it visualizes the insights through a web-based dashboard.

## 🛠️ Tech Stack
*   **Language:** Python 3.x
*   **Data Processing:** Pandas, SQLAlchemy
*   **Database:** PostgreSQL 15
*   **Infrastructure:** Docker & Docker Compose
*   **Visualization:** Streamlit
*   **API:** Open-Meteo API

## 🏗️ Architecture
1.  **Extraction:** Python script calls the Open-Meteo API to get live weather data.
2.  **Transformation:** Data is cleaned, timestamps are formatted, and new features are added using Pandas.
3.  **Loading:** The cleaned data is inserted into a PostgreSQL database running inside a Docker container.
4.  **Visualization:** Streamlit connects to PostgreSQL to fetch the latest records and display interactive charts.

## 🚀 How to Run
To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd weather_pipeline# 🌦️ Real-Time Weather Data Pipeline

An end-to-end Data Engineering project that automates the process of extracting, transforming, and loading (ETL) weather data into a containerized database, with a live interactive dashboard for visualization.

## 📌 Project Overview
This project demonstrates a complete ETL pipeline. It fetches real-time weather metrics (Temperature, Humidity, Wind Speed) for Cairo from the Open-Meteo API, processes the data using Python, and stores it in a PostgreSQL database managed by Docker. Finally, it visualizes the insights through a web-based dashboard.

## 🛠️ Tech Stack
*   **Language:** Python 3.x
*   **Data Processing:** Pandas, SQLAlchemy
*   **Database:** PostgreSQL 15
*   **Infrastructure:** Docker & Docker Compose
*   **Visualization:** Streamlit
*   **API:** Open-Meteo API

## 🏗️ Architecture
1.  **Extraction:** Python script calls the Open-Meteo API to get live weather data.
2.  **Transformation:** Data is cleaned, timestamps are formatted, and new features are added using Pandas.
3.  **Loading:** The cleaned data is inserted into a PostgreSQL database running inside a Docker container.
4.  **Visualization:** Streamlit connects to PostgreSQL to fetch the latest records and display interactive charts.

## 🚀 How to Run
To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd weather_pipeline


    📌 To-Do & Future Roadmap

 - [x] **Unit Testing (pytest):** نكتب Unit Tests باستخدام pytest للتأكد من أن الدوال شغال صح.
[ ] Production Orchestration: Migrate from the basic schedule library to an enterprise orchestrator like Apache Airflow or n8n for failure monitoring and automated retries.

[ ] Full Containerization: Dockerize the ETL script (main.py) and the web application (app.py) inside docker-compose.yml to achieve environment independence.

[ ] Data Security: Strict decouple of production secrets, reading credentials fully via dynamic os.getenv without local fallbacks.

[ ] Alerting Integration: Add Webhook alerts (Slack/Telegram) to instantly notify on pipeline failures or API timeouts.