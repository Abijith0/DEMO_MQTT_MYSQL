# 🏭 Enterprise Edge IIoT Gateway: PLC to Cloud & SQL

## 📌 Executive Summary
This project demonstrates a production-grade Industrial IoT (IIoT) data pipeline. It bridges the Operational Technology (OT) and Information Technology (IT) divide by deploying a Python-based Edge Gateway. The system acquires real-time telemetry from a simulated manufacturing process, routes it to a local Enterprise SQL Historian for SCADA visualization, and simultaneously pushes it to a cloud MQTT broker for bidirectional mobile control.

---

## 🏗️ System Architecture (Logical Flow)

The system operates on a decoupled, multi-threaded architecture to ensure that data logging, cloud publishing, and UI rendering never block each other.

1. **OT Data Acquisition:** A simulated CODESYS PLC generates process variables (`CV`, `PV`, `Motor Status`). PTC Kepware Server exposes these tags via **OPC UA**.
2. **Edge Gateway (`DATA_LOGGER.PY`):** A custom Python service that continuously polls the OPC UA server. It acts as the central router:
   * **Route A (Local Historian):** Ingests telemetry into a **MySQL** relational database using parameterized queries to prevent injection and ensure data integrity.
   * **Route B (Cloud Telemetry):** Packages data into JSON payloads and publishes them to an **MQTT** broker.
3. **Enterprise Visualization (`DASHBOARD.PY`):** A **Streamlit** SCADA application that queries the MySQL historian to render live production trends and metrics.
4. **Remote Control:** An Android application subscribes to the MQTT broker, allowing remote operators to monitor the machine and safely write setpoints or trigger momentary Start/Stop logic back to the PLC.

---

## 🌐 Network Architecture & Topology

This architecture respects standard industrial network segmentation, separating raw machine control from enterprise viewing and remote cloud access.

* **[Level 1] Control Network:** CODESYS SoftPLC running cyclic logic.
* **[Level 2] Supervisory Network:** * PTC Kepware Server (OPC UA Aggregator).
  * Python Edge Gateway (Protocol Translator).
  * Local MySQL Server (Process Historian).
* **[Level 3] Plant/IT Network:** Streamlit Web Dashboard (Local Host/Intranet accessible).
* **[Level 4/5] Cloud/External:** HiveMQ Cloud Broker communicating over secure port 8883 (TLS/SSL) to the remote Android operator device.

---

## ⚙️ Core Technologies & Stack
* **Languages:** Python 3 (Pandas, PyMySQL, OPCUA, Paho-MQTT)
* **Industrial Protocols:** OPC UA, MQTT
* **Database:** MySQL Server (InnoDB)
* **Visualization:** Streamlit
* **Automation Software:** CODESYS V3, PTC Kepware Server EX

---

## 🛡️ Key Engineering Features
* **Fault Tolerance:** The Edge Gateway features automatic database reconnection logic to survive network drops without crashing.
* **Repeatable Read Handling:** The dashboard connection logic actively commits transactions before querying to bypass MySQL snapshot isolation, ensuring a true real-time feed.
* **Momentary Safety Logic:** Cloud control buttons implement "Press" and "Release" MQTT payloads, allowing the gateway to write boolean true/false states safely to the PLC.
