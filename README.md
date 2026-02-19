# 🏭 Enterprise Industrial IoT Gateway  
### PLC → Edge → SQL → Cloud → Analytics

![system](PLC_KW_1.jpeg)

---

# 📌 Executive Summary
This project demonstrates a **production-grade Industry 4.0 architecture** that bridges OT (factory floor) and IT (cloud & analytics).

A Python-based edge gateway collects real-time machine data from a PLC via OPC UA, logs it into an enterprise SQL historian, and publishes it to the cloud via MQTT for mobile monitoring and remote control.

The system mirrors real smart-factory infrastructure used in modern manufacturing environments.

---

# 🎯 Key Capabilities
- Real-time PLC data acquisition (OPC UA)
- Edge gateway architecture (Python)
- SQL historian logging (MySQL)
- Cloud telemetry (MQTT TLS)
- Mobile monitoring & control
- SCADA-style analytics dashboard
- AI/ML-ready production dataset

---

# 🖼️ System Preview

## PLC + Kepware Layer
![plc](PLC_KW_2.jpeg)

## Mobile MQTT Monitoring
![mobile](IOT_MQTT_1.jpeg)

## MySQL Historian
![mysql](mysql_DB_1.png)

## Live Analytics Dashboard
![dash](mysql_DB_2.png)

---

# 🏗️ Full System Architecture

```mermaid
flowchart LR
    PLC[PLC Machine] --> Kepware[Kepware OPC Server]
    Kepware --> Edge[Python Edge Gateway]
    Edge --> MySQL[(MySQL Historian)]
    Edge --> MQTT[Cloud MQTT Broker]
    MQTT --> Mobile[Mobile App]
    MySQL --> Dashboard[Streamlit SCADA Dashboard]
    MySQL --> AI[Future AI/ML Engine]
