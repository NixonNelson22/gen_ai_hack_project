# Cement Plant Control System

This project is a demonstration of a cement plant control system using a multi-agent architecture. The system is designed to monitor and optimize the cement production process in real-time.

## Features

*   **Multi-Agent System:** The core of the project is a multi-agent system consisting of a main agent and multiple leaf agents.
*   **Real-time Monitoring:** The system simulates a real-time data stream from a cement plant.
*   **AI-Powered Optimization:** The agents use AI to analyze the data and provide control recommendations.
*   **Web-Based Dashboard:** An HTMX-based operator dashboard provides a real-time view of the plant's status, agent activities, and task results.
*   **Redis Communication:** The agents and the main control program (MCP) server communicate via Redis.

## Getting Started

### Prerequisites

*   Python 3.10+
*   Redis

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/NixonNelson22/gen_ai_hack_project.git
    ```
2.  Install the required Python packages:
    ```bash
    pip install -r cement_plant_control_system/requirements.txt
    ```

## Usage

1.  Start the application by running the `start.sh` script:
    ```bash
    ./start.sh
    ```
2.  This will start the following components:
    *   MCP Server (FastAPI)
    *   Main Agent
    *   Leaf Agent
    *   Data Stream Simulator
3.  Open your web browser and navigate to `http://localhost:8080/dashboard` to view the operator dashboard.

## Architecture

The system consists of the following main components:

*   **MCP Server:** A FastAPI server that acts as the central orchestrator. It manages agent registration, task distribution, and results collection.
*   **Main Agent:** A top-level agent that oversees the entire plant operation. It receives high-level goals and breaks them down into smaller tasks for the leaf agents.
*   **Leaf Agents:** Specialized agents that monitor and control specific parts of the cement plant. They receive tasks from the main agent and report back the results.
*   **Operator Dashboard:** An HTMX-based web interface that allows operators to monitor the system, view agent activities, and manually send tasks to agents.
*   **Redis:** A Redis server is used as the communication backbone for the entire system. It facilitates message passing between the agents and the MCP server.
*   **Data Stream Simulator:** A script that simulates a real-time data stream from the cement plant, providing realistic data for the agents to work with.