import json


SYSTEM_PROMPT = """You are a notification routing assistant.

Decide whether an incoming message should be routed as:
- notify
- digest
- mute

Use the provided context only.

Priority order:
1. Safety/suspicion
2. Urgency
3. Personal relevance
4. Historical user behavior
5. Disruption cost

Verified business interactions (orders, bookings, payments, appointments) should usually be prioritized over unrelated promotions. Treat unverified businesses or suspicious domains cautiously.

Return ONLY valid JSON with this schema:
{
  "action": "notify|digest|mute",
  "message_type": "personal|urgent|event|payment|business_update|promotion|greeting|forward|spam|scam|unknown",
  "reason": "one concise sentence",
  "confidence": 0.0,
  "evidence_message_ids": ["..."]
}

Use the least disruptive action that is still supported by the evidence.
Do not infer urgency unless the message or context supports it.
Only include evidence_message_ids that directly support your decision."""


def build_user_prompt(context):
    """
    Constructs the structured user prompt payload injection for the LLM runner.
    """
    message = context["message"]
    user = context["user"]
    conversation = context["conversation"]
    history = context["history"]
    media = context["media"]

    return f"""Incoming Message

{json.dumps(message)}

User Context

{json.dumps(user)}

Conversation Context

{json.dumps(conversation)}

Relevant Historical Messages

{json.dumps(history)}

Media Context

{json.dumps(media)}

Using ONLY the information above, determine the most appropriate routing decision.

Return valid JSON only."""

ROUTING_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "action": {
            "type": "STRING",
            "enum": [
                "notify",
                "digest",
                "mute",
            ],
        },
        "message_type": {
            "type": "STRING",
            "enum": [
                "personal",
                "urgent",
                "event",
                "payment",
                "business_update",
                "promotion",
                "greeting",
                "forward",
                "spam",
                "scam",
                "unknown",
            ],
        },
        "reason": {
            "type": "STRING",
        },
        "confidence": {
            "type": "NUMBER",
        },
        "evidence_message_ids": {
            "type": "ARRAY",
            "items": {
                "type": "STRING",
            },
        },
    },
    "required": [
        "action",
        "message_type",
        "reason",
        "confidence",
        "evidence_message_ids",
    ],
}