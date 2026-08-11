from copy import deepcopy


class Validator:
    ALLOWED_ACTIONS = {
        "notify",
        "digest",
        "mute",
    }

    ALLOWED_MESSAGE_TYPES = {
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
    }

    def validate(self, message_id, prediction):
        prediction = deepcopy(prediction)

        action = prediction.get("action", "digest")
        if action not in self.ALLOWED_ACTIONS:
            action = "digest"

        message_type = prediction.get("message_type", "unknown")
        if message_type not in self.ALLOWED_MESSAGE_TYPES:
            message_type = "unknown"

        reason = str(prediction.get("reason", ""))

        confidence = prediction.get("confidence", 0.0)
        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.0

        confidence = max(0.0, min(confidence, 1.0))

        evidence = prediction.get("evidence_message_ids", [])

        if isinstance(evidence, list):
            evidence = [str(x) for x in evidence if str(x) != message_id]
            evidence = ";".join(evidence) if evidence else "none"
        elif not evidence:
            evidence = "none"
        elif str(evidence) == str(message_id):
            evidence = "none"
        else:
            evidence = str(evidence)

        return {
            "message_id": message_id,
            "action": action,
            "message_type": message_type,
            "reason": reason,
            "confidence": confidence,
            "evidence_message_ids": evidence,
        }

    def fallback_prediction(self, message_id):
        return {
            "message_id": message_id,
            "action": "digest",
            "message_type": "unknown",
            "reason": "Fallback prediction due to processing error.",
            "confidence": 0.0,
            "evidence_message_ids": "none",
        }