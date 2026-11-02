# Evaluation Report

This report summarizes the sample routing evaluation on `dataset/sample_messages.csv`.
The evaluation compares model predictions against the labeled sample messages provided with the dataset.

- Model: `gemini-3.1-flash-lite`
- LLM Router: Enabled

## Metrics

- Total evaluated messages: **30**
- Action accuracy: **25/30 (83.3%)**
- Message type accuracy: **28/30 (93.3%)**
- Average confidence: **0.937**
- Fallback predictions (model did not answer): **0**
