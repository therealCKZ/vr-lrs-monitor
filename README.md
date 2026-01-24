# VR LRS Real-time Monitoring System

A containerized three-tier data monitoring pipeline designed for VR (Virtual Reality) learning environments. This system fetches xAPI statements from a Learning Record Store (LRS), processes them through a Python middleware, and visualizes the activity in real-time using Grafana.



## Architecture
1. **Data Layer (LRS)**: Stores VR activity statements via xAPI protocol.
2. **Middleware Layer (Python Flask)**: 
   - Handles secure authentication and SSL bypass for internal servers.
   - Filters data using a custom `START_TIME` window.
   - Simplifies complex xAPI JSON into a lightweight metrics format.
3. **Visualization Layer (Grafana)**: 
   - Uses the **Infinity Plugin** to consume the API.
   - Provides real-time dashboards for VR engagement monitoring.

## Getting Started

Follow these instructions to get the system up and running on your local machine for development and testing purposes.

### Prerequisites
Ensure you have the following installed:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
* [Git](https://git-scm.com/)

---

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/vr-lrs-monitor.git](https://github.com/YOUR_USERNAME/vr-lrs-monitor.git)
   cd vr-lrs-monitor

2. **Launch the Sevice**
   ```bash
   docker-compose up --build -d

3. **Verify the API Status**
Check if the Middleware is successfully communicating with the LRS:
* Open: http://localhost:8000/metrics
* You should see a JSON response with record_count

---

### Accessing the Dashboard
1. **Login to Grafana**
    * URL: http://lrs-api:8000/metrics
    * Username: admin
    * Password: admin
2. **Configuration**
Ensure the **Infinity Data Source** in Grafana is pointed to the internal Docker address: http://lre-api:8000/metrics

---

### Cusomizing the Obseration Window
To change the specific time from the system starts counting VR activities:
1. Open api/main.py.
2. Locate the START_TIME variable.
3. Edit the timestamp (ISO 8601 format with GMT+8):
   ```bash
   START_TIME = "2026-01-24T09:00:00+08:00"

4. Restart the container to apply changes:
   ```bash
   docker-compose up --build -d