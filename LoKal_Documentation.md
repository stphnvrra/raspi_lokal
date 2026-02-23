# LoKal: Offline AI Education Assistant

**Group Members:**
1. Navarra, Stephen Ceasar
2. Mabugay, Jesrell
3. Chiquito, Jenny
4. Dagoc, Herzian Jean
5. Teopis, Gretchen

---

## I. Introduction

**LoKal** (Localized Knowledge and Learning) is a fully offline, localized AI educational system designed to provide high-quality learning support to students in remote and underserved areas. Powered by a **Raspberry Pi 4**, it integrates a speaker, microphone, and a local Large Language Model (LLM) to function entirely without internet connectivity.

### The Problem: The Digital Divide
In many remote locations, specifically in **Geographically Isolated and Disadvantaged Areas (GIDAS)**, limited access to smartphones, computers, and steady internet creates a significant "digital divide." This gap prevents students from accessing modern educational resources, further widening the inequality in quality education. LoKal addresses this by acting as a shared, communal educational device that can explain complex subjects like **Math, Science, and English** in clear, simple language.

### Our Mission: Quality Education for All
Our project aligns with the United Nations' **Sustainable Development Goal 4 (SDG 4)**, which aims to "ensure inclusive and equitable quality education and promote lifelong learning opportunities for all." By bringing advanced AI technology to areas with zero connectivity, we ensure that students are not left behind by the rapid pace of technological advancement.

### Technical Paradigm: From Cloud to Edge
Traditional AI assistants rely heavily on cloud computing, which requires high-speed internet and raises concerns about data privacy. LoKal utilizes **Edge Computing**—processing data directly on the local hardware (Raspberry Pi). This approach offers several critical advantages:
- **Total Independence:** Functions perfectly in "dead zones" with no cellular or Wi-Fi signal.
- **Data Sovereignty:** Student interactions are never uploaded to the cloud, ensuring 100% privacy and security.
- **Zero Latency:** Immediate responses without waiting for data to travel to a distant server.

By leveraging optimized, modern AI, LoKal turns a low-cost, durable device into a powerful tutor, ensuring that education remains accessible, private, and reliable, regardless of geographical or infrastructure limitations.

## II. Project Concept

LoKal offers an interactive and accessible learning experience through voice and text-based interaction.

**Functions of the System:**
- **Offline Questioning:** Allows students to ask homework questions anytime via voice (microphone) or text (keyboard) input.
- **Multilingual Support:** AI explains core subjects in simple language tailored for the learner.
- **Auditory Learning:** Provides spoken answers and explanations via a connected speaker, aiding students with different learning styles.
- **Privacy & Speed:** Because it is fully offline, student data stays local, and there is no latency associated with cloud server communication.

**Why It Helps:**
- **Reliability:** Functions consistently in locations with zero internet connectivity.
- **Engagement:** Encourages interactive speaking, typing, and listening.
- **Accessibility:** Improves support for younger learners or those with limited typing skills through voice interaction.
- **Cost-Efficiency:** Utilizes low-cost, durable hardware (Raspberry Pi 4) suitable for community deployment.

## III. Visualization of Your Project

### A. Prototype Visualization (Raspberry Pi 4-Based)

The project prototype is built using a **Raspberry Pi 4** as the main controller of the **LoKal** system.

**Main Components:**
- **Raspberry Pi 4 (4GB/8GB):** The core processor running the local AI environment.
- **USB Microphone:** For capturing voice-based questions from the student.
- **Connected Speaker:** For text-to-speech (TTS) output, enabling auditory learning.
- **Monitor/Display:** For visual feedback and text-based educational content.
- **Physical Keyboard:** Providing an alternative standard text input method.
- **USB Mouse:** For navigating the graphical user interface.

**How the Prototype Works:**
- The student initiates an interaction by selecting their preferred input method (voice or text).
- If voice is chosen, the **USB Microphone** captures the audio, which is converted to text using the **Vosk** offline engine.
- The **Raspberry Pi 4** processes the text question locally using an optimized AI model via **Ollama**.
- Once the answer is generated, it is displayed clearly on the **Monitor/Display**.
- If enabled, the **Piper TTS** engine converts the answer to speech, playing it back through the **Connected Speaker**.

### B. Web / Mobile Application Visualization

The **Raspberry Pi 4** runs a **local web application** internally, which serves as the main interface for the system. The application is hosted and accessed directly on the Raspberry Pi.

**The application allows users to:**
- **Access AI Learning:** Students can ask questions via text or voice and receive instant explanations.
- **Track Recent Chats:** The sidebar provides a history of previous educational interactions.
- **Account Management:** Users can login and register their account to save their chats.

This visualization demonstrates how the Raspberry Pi 4 enables **accessible, localized AI learning**, making the system suitable for school environments and remote community centers.

## IV. References

1. **Gerganov, G. (2024).** *Llama.cpp: Port of Facebook's LLaMA model in C/C++.* [GitHub Repository](https://github.com/ggerganov/llama.cpp) — Core engine for running LLMs on edge devices like Raspberry Pi.
2. **Ollama Project. (2024).** *Ollama: Get up and running with large language models locally.* [ollama.com](https://ollama.com) — Providing optimized models for ARM64 architectures.
3. **Vosk Speech Recognition Toolkit.** *Offline Speech-to-Text for Raspberry Pi.* [alphacephei.com/vosk](https://alphacephei.com/vosk) — Efficient, multi-language offline STT.
4. **Piper TTS.** *A fast, local neural text-to-speech system.* [GitHub Repository](https://github.com/rhasspy/piper) — Optimized for Raspberry Pi 4 for natural-sounding auditory learning.
5. **Raspberry Pi Foundation.** *Raspberry Pi 4 Model B Product Specifications.* [raspberrypi.com](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) — Hardware foundation for low-cost educational platforms.
6. **UNESCO (2023).** *Bridging the digital divide in remote education.* — Contextualizing the need for offline educational tools in underserved regions.
