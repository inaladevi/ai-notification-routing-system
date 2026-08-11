from typing import Dict, Any, List


class ContextBuilder:
    """
    Builds a personalized context package for a single incoming message.

    This class only retrieves and organizes information.
    It does NOT perform any routing or LLM reasoning.
    """

    def __init__(self, repository):
        self.repo = repository

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def build_context(self, message: Dict[str, Any]) -> Dict[str, Any]:

        context = {
            "message": message,
            "user": self._get_user(message),
            "conversation": None,
            "history": self._get_history(message),
            "media": self._get_media(message),
        }

        conversation_type = message["conversation_type"]

        if conversation_type == "group":
            context["conversation"] = self._get_group_context(message)

        elif conversation_type == "business":
            context["conversation"] = self._get_business_context(message)

        else:
            context["conversation"] = self._get_personal_context(message)

        return context

    # ---------------------------------------------------------
    # User
    # ---------------------------------------------------------

    def _get_user(self, message):

        summary = self.repo.get_notification_summary(message["user_id"])

        return {
            "profile": self.repo.get_user(message["user_id"]),
            "notification_summary": summary[-3:],
        }

    # ---------------------------------------------------------
    # Group
    # ---------------------------------------------------------

    def _get_group_context(self, message):

        group = self.repo.get_group(message["group_id"])

        member = self.repo.get_group_member(
            message["group_id"],
            message["user_id"],
        )

        return {
            "type": "group",
            "group": group,
            "membership": member,
        }

    # ---------------------------------------------------------
    # Business
    # ---------------------------------------------------------

    def _get_business_context(self, message):

        business = self.repo.get_business(
            message["business_id"]
        )

        relationship = self.repo.get_user_business(
            message["user_id"],
            message["business_id"],
        )

        return {
            "type": "business",
            "business": business,
            "relationship": relationship,
        }

    # ---------------------------------------------------------
    # Personal
    # ---------------------------------------------------------

    def _get_personal_context(self, message):

        return {
            "type": "personal",
            "sender_user_id": message["sender_user_id"],
        }

    # ---------------------------------------------------------
    # History
    # ---------------------------------------------------------

    def _get_history(self, message):

        history = []

        conversation_type = message["conversation_type"]

        if conversation_type == "group":

            history = self.repo.get_history_for_group(
                message["group_id"]
            )

        elif conversation_type == "business":

            history = self.repo.get_history_for_business(
                message["business_id"]
            )

        else:

            history = self.repo.get_history_for_sender(
                message["sender_user_id"]
            )

        enriched = []

        for item in history:
            event = self.repo.get_message_event(item["message_id"])
            enriched.append({
                "message_id": item.get("message_id"),
                "message_text": item.get("message_text"),
                "sender_user_id": item.get("sender_user_id"),
                "opened": event.get("message_opened") if event else None,
                "replied": event.get("message_replied") if event else None,
                "dismissed": event.get("notification_dismissed") if event else None,
                "reported": event.get("message_reported") if event else None,
            })

        return enriched[-2:]

    # ---------------------------------------------------------
    # Media
    # ---------------------------------------------------------

    def _get_media(self, message):

        if not isinstance(message["media_type"], str):
            return None

        return None