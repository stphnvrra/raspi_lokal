# Smart Street Lighting Project

**Group Members:**
- Acxel Sososco
- Airon Bonite
- Harvey Perater
- Gian Paolo De Gracia
- Jenel Eric Fernandez

---

## I. Introduction

**Smart Street Lighting** is an automated lighting system designed to enhance public safety by using motion sensors and smart control logic. In traditional systems, lights remain turned on for long hours even when no pedestrians or vehicles are present, leading to unnecessary energy consumption and higher electricity costs.

The main problem this project aims to solve is **energy waste caused by continuous streetlight operation**. By integrating motion detection and automated timing, streetlights will only activate when needed. This project was created to explore how simple IoT-based automation can contribute to smarter cities, cost savings, and sustainable energy use.

Our motivation for developing this project is to apply automation concepts and sensor technology in a real-world scenario that benefits communities and supports environmental responsibility.

## II. Project Concept

The Smart Street Lighting system automatically controls streetlights based on environmental conditions and movement.

**Functions of the System:**
- Automatically turns streetlights **ON** and **OFF**
- Detects **motion** from pedestrians and vehicles
- Uses a **time delay sequence** to keep lights ON after motion is detected
- Detects **day and night conditions** using ambient light sensing
- Reduces power consumption when no movement is present

## III. Visualization of Your Project

### A. Prototype Visualization (Raspberry Pi 4-Based)

The project prototype is built using a **Raspberry Pi 4** as the main controller of the Smart Street Lighting system.

**Main Components:**
- Raspberry Pi 4
- PIR Motion Sensor
- Ambient Light Sensor (LDR)
- LED Streetlight Module
- Relay Module (for switching lights)

**How the Prototype Works:**
- During **daytime**, the ambient light sensor detects sufficient light, keeping the streetlights OFF.
- At **night**, the system becomes active.
- When **motion is detected** by the PIR sensor, the Raspberry Pi 4 processes the signal and turns the streetlight ON.
- After a **predefined delay** with no detected movement, the Raspberry Pi automatically turns the streetlight OFF to conserve energy.

### B. Web / Mobile Application Visualization

The Raspberry Pi 4 is connected to a **web-based or mobile-accessible dashboard**.

**The application allows users to:**
- Monitor real-time streetlight status (ON/OFF)
- View motion detection logs
- Observe system activity remotely
- Analyze basic lighting usage behavior

This visualization demonstrates how the Raspberry Pi 4 enables **remote monitoring and smart control**, making the system suitable for smart city applications.

## IV. References

1. Internet of Things (IoT) concepts and applications
2. Smart City Infrastructure studies
3. Sensor-based automation systems
4. Energy-efficient lighting technologies
