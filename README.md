# 🤖 WhatsApp Stream Assistant

A robust, context-aware bot designed for WhatsApp communication using the Meta API. Built with secure, scalable technologies like **Kafka**, **Redis**, and **Google BigQuery**, the assistant is capable of handling dynamic user conversations, maintaining state, performing intelligent fallback mechanisms, and routing human support when needed.

---

## 🛠️ Tech Stack

- **Meta WhatsApp Business API**
- **Kafka** – message streaming and architecture backbone
- **Redis** – temporary context and conversation storage
- **Google BigQuery (GBQ)** – persistent storage and analytics
- **HMAC** – secure webhook validation
- **Docker Compose** – service orchestration

---

## 🔄 Architecture Overview

### 🎯 Stage 1 – Smart Reply System
- The bot processes incoming messages while maintaining **chat context** using Redis.
- A system prompt (JSON file) guides its behavior.
- The bot uses a **fallback-based model switch mechanism**:
  1. `Deepsek R1` (primary)
  2. `Deepsek V3` (fallback)
  3. `GPT-4` (last resort)

If all models fail, a fail-safe message is sent, and a human takeover is triggered.

---

### 🧹 Stage 2 – Response Cleanup
- Ensures the reply is clear, relevant, and **free from hallucinations or redundant content**.

---

### 🔍 Stage 3 – Conversation State Evaluation
- Detects the **status of the conversation**:
  - `Open`
  - `Closed`
  - `Aggressive`
  - `Frustrated`
  
- If **open**, the assistant keeps the channel active.
- If **closed**, the assistant:
  - Notifies the customer that a human representative will take over.
  - Sends an **email** to the assigned human with the full chat history.
  - The human replies using a **different phone number**.

---

## 💾 Data Flow

- **Redis** is used for real-time data:
  - User context
  - Active conversations
  - Usage cost
  - Deal status

- On schedule:
  - Data is exported to **Google BigQuery**
  - Redis is cleaned to free up memory

---

## 🔐 Security

- All webhook calls from Meta are verified using **HMAC signatures** to prevent unauthorized access.

---

## 🚨 Fail-Safe System

- If message processing fails at any stage:
  - The bot informs the user that the system is down.
  - A human will reach out shortly.
  - The system alerts the **owner** via a dedicated channel.

---

## 📦 Deployment

We use **Docker Compose** to manage services:

```bash
docker-compose up -d


```
Services include:

API connector for Meta Webhooks

Kafka broker and consumer

Redis store

GPT/LLM orchestration layer

Scheduled exporter for GBQ

📈 Monitoring & Logging
Usage and system events are logged and exported to BigQuery for analysis.

Errors and alerts are also routed to internal channels or emails.

📬 Contact
For questions or contributions, please open an issue or reach out to the maintainer.

🧠 Future Roadmap
✅ Multi-language support

⏳ Dynamic model selection based on cost/latency

⏳ Real-time dashboard for active conversations

⏳ Integration with CRMs
