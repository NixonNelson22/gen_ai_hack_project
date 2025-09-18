
# Autonomous Cement Plant Control System MVP

This project is a minimal, demo-ready MVP for an autonomous cement plant control system using Google Cloud services.

## Architecture

The system consists of three main components:

- **Leaf Agent**: A Python script that simulates sensor data for a plant department, preprocesses it, and sends it to a Pub/Sub topic.
- **Main Agent**: A Python script that subscribes to the leaf agent's data, applies simple rule-based logic, and stores the state and decisions in Firestore.
- **Operator Dashboard**: A Streamlit application that displays the plant's real-time status, alerts, and recommended control decisions from Firestore.

## Google Cloud Setup

1.  **Create a Google Cloud Project**:
    - If you don't have one already, create a new project in the [Google Cloud Console](https://console.cloud.google.com/).

2.  **Enable APIs**:
    - In your project, enable the following APIs:
        - Pub/Sub API
        - Cloud Firestore API

3.  **Create Pub/Sub Topics**:
    - Create two Pub/Sub topics:
        - `leaf-agent-data`
        - `main-agent-decisions`

4.  **Create a Pub/Sub Subscription**:
    - Create a subscription to the `leaf-agent-data` topic named `main-agent-subscription`.

5.  **Create a Firestore Database**:
    - In the Google Cloud Console, create a Firestore database in Native mode.

6.  **Create a Service Account**:
    - Create a service account with the following roles:
        - `Pub/Sub Editor`
        - `Cloud Datastore User` (for Firestore)
    - Download the service account key as a JSON file.

7.  **Set Environment Variables**:
    - Set the following environment variables in your terminal:
      ```bash
      export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
      export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
      ```

## Local Setup and Execution

1.  **Clone the Repository**:
    - Clone this repository to your local machine.

2.  **Install Dependencies**:
    - Navigate to the `cement_plant_control_system` directory and install the required Python packages:
      ```bash
      pip install -r requirements.txt
      ```

3.  **Run the Components**:
    - Open three separate terminals and run each component:

      - **Terminal 1: Main Agent**
        ```bash
        cd cement_plant_control_system/main_agent
        python main_agent.py
        ```

      - **Terminal 2: Leaf Agent**
        ```bash
        cd cement_plant_control_system/leaf_agent
        python leaf_agent.py
        ```

      - **Terminal 3: Operator Dashboard**
        ```bash
        cd cement_plant_control_system/operator_dashboard
        streamlit run dashboard.py
        ```

4.  **View the Dashboard**:
    - Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).
