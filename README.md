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

### Prerequisites
- Docker and Docker Compose installed on your machine.

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/vr-lrs-monitor.git](https://github.com/YOUR_USERNAME/vr-lrs-monitor.git)
   cd vr-lrs-monitor