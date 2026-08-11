from pathlib import Path
from collections import defaultdict
import pandas as pd


class NotificationRepository:
    """
    Loads all competition datasets once and provides
    convenient lookup methods for the rest of the pipeline.
    """

    def __init__(self, dataset_dir: str = "dataset"):
        self.dataset_dir = Path(dataset_dir)

        # Raw DataFrames
        self.users = None
        self.groups = None
        self.group_members = None
        self.business_accounts = None
        self.user_business_history = None
        self.messages = None
        self.message_history = None
        self.message_events = None
        self.daily_notification_summary = None

        # Lookup dictionaries
        self.users_by_id = {}
        self.groups_by_id = {}
        self.businesses_by_id = {}

        self.group_members_by_key = {}
        self.user_business_by_key = {}

        self.events_by_message = {}
        self.notification_summary_by_user = defaultdict(list)

        self.history_by_user = defaultdict(list)
        self.history_by_group = defaultdict(list)
        self.history_by_business = defaultdict(list)
        self.history_by_sender = defaultdict(list)

    # -------------------------------------------------------
    # Public API
    # -------------------------------------------------------

    def load(self):
        """Load every dataset and build lookup indexes."""

        self.users = self._read_csv("users.csv")
        self.groups = self._read_csv("groups.csv")
        self.group_members = self._read_csv("group_members.csv")
        self.business_accounts = self._read_csv("business_accounts.csv")
        self.user_business_history = self._read_csv("user_business_history.csv")

        self.messages = self._read_csv("messages.csv")

        self.message_history = self._read_csv("message_history.csv")
        self.message_events = self._read_csv("message_events.csv")

        self.daily_notification_summary = self._read_csv(
            "daily_notification_summary.csv"
        )

        self._build_indexes()

        return self

    # -------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------

    def _read_csv(self, filename):
        return pd.read_csv(self.dataset_dir / filename).fillna("")

    def _build_indexes(self):

        # ---------- Groups ----------
        self.groups_by_id = (
            self.groups.set_index("group_id")
            .to_dict("index")
        )

        # ---------- Businesses ----------
        self.businesses_by_id = (
            self.business_accounts
            .set_index("business_id")
            .to_dict("index")
        )

        # ---------- Group Members ----------
        for row in self.group_members.to_dict("records"):
            key = (row["group_id"], row["user_id"])
            self.group_members_by_key[key] = row

        # ---------- User Business ----------
        for row in self.user_business_history.to_dict("records"):
            key = (row["user_id"], row["business_id"])
            self.user_business_by_key[key] = row

        # ---------- Events ----------
        for row in self.message_events.to_dict("records"):
            self.events_by_message[row["message_id"]] = row

        # ---------- Notification Summary ----------
        for row in self.daily_notification_summary.to_dict("records"):
            self.notification_summary_by_user[row["user_id"]].append(row)

        # ---------- Message History ----------
        for row in self.message_history.to_dict("records"):

            self.history_by_user[row["user_id"]].append(row)

            if row["group_id"]:
                self.history_by_group[row["group_id"]].append(row)

            if row["business_id"]:
                self.history_by_business[row["business_id"]].append(row)

            if row["sender_user_id"]:
                self.history_by_sender[row["sender_user_id"]].append(row)

    # -------------------------------------------------------
    # Lookup Methods
    # -------------------------------------------------------

    def get_user(self, user_id):
        return self.users_by_id.get(user_id)

    def get_group(self, group_id):
        return self.groups_by_id.get(group_id)

    def get_group_member(self, group_id, user_id):
        return self.group_members_by_key.get((group_id, user_id))

    def get_business(self, business_id):
        return self.businesses_by_id.get(business_id)

    def get_user_business(self, user_id, business_id):
        return self.user_business_by_key.get((user_id, business_id))

    def get_history_for_user(self, user_id):
        return self.history_by_user.get(user_id, [])

    def get_history_for_group(self, group_id):
        return self.history_by_group.get(group_id, [])

    def get_history_for_business(self, business_id):
        return self.history_by_business.get(business_id, [])

    def get_history_for_sender(self, sender_user_id):
        return self.history_by_sender.get(sender_user_id, [])

    def get_message_event(self, message_id):
        return self.events_by_message.get(message_id)

    def get_notification_summary(self, user_id):
        return self.notification_summary_by_user.get(user_id, [])

    def get_messages(self):
        return self.messages.to_dict("records")
