# AI Notification Routing System

## Overview

An AI-powered notification routing system that classifies incoming messages into one of three actions:

- Notify
- Digest
- Mute

The system combines message content with user history, conversation context, group information, and notification history to make routing decisions using Google's Gemini API.

---

## Pipeline

```text
Incoming Message
        │
        ▼
Notification Repository
        │
        ▼
Context Builder
        │
        ▼
Gemini Router
        │
        ▼
Validator
        │
        ▼
output.csv
```

---

## Tech Stack

- Python
- Google Gemini API
- Pandas
- Prompt Engineering
- JSON Processing
- CSV Processing

---

## Project Structure

```
src/
dataset/
docs/

requirements.txt
README.md
```

---

## Dataset

The project expects the required datasets inside the `dataset/` directory.

Predictions are generated as:

```
dataset/output.csv
```

---

## Evaluation

Run the evaluation pipeline on the labeled sample dataset:

```bash
python3 src/evaluation_pipeline/main.py
```

This generates:

- evaluation_report.md

and reports:

- Action accuracy
- Message type accuracy
- Average confidence

---

## Installation

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```text
GEMINI_API_KEY=your_api_key_here
```

---

## Run

```bash
python3 src/main.py
```