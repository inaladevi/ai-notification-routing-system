import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _write(directory, name, columns, rows):
    pd.DataFrame(rows, columns=columns).to_csv(directory / name, index=False)


@pytest.fixture
def dataset_dir(tmp_path):
    """A tiny dataset with the same columns as the real one (no API key or real data needed)."""
    _write(tmp_path, "users.csv",
           ["user_id", "do_not_disturb_window", "messages_opened_30d", "messages_replied_30d",
            "notifications_dismissed_30d", "messages_reported_30d"],
           [["u_1", "22:00-07:00", 45, 8, 14, 2]])
    _write(tmp_path, "groups.csv",
           ["group_id", "group_name", "group_type", "member_count", "admin_count", "created_at", "messages_30d"],
           [["g_1", "Family", "family", 5, 1, "2023-01-01", 90]])
    _write(tmp_path, "group_members.csv",
           ["group_id", "user_id", "role", "joined_at", "messages_sent_30d", "messages_read_30d",
            "replies_sent_30d", "notifications_dismissed_30d", "group_muted_by_user"],
           [["g_1", "u_1", "member", "2023-02-01", 2, 2, 0, 4, 1]])
    _write(tmp_path, "business_accounts.csv",
           ["business_id", "display_name", "brand_name", "category", "verified", "official_domain",
            "domain_used_by_sender", "account_age_days", "messages_sent_30d", "user_reports_30d",
            "domain_used_by_sender_age_days"],
           [["b_1", "Shop", "Shop", "ecommerce", 1, "shop.in", "shop.in", 900, 100, 1, 700]])
    _write(tmp_path, "user_business_history.csv",
           ["user_id", "business_id", "why_user_knows_account", "last_activity_at", "allows_promotions",
            "promotions_opted_out_at", "activity_count_180d", "messages_opened_30d",
            "messages_dismissed_30d", "messages_replied_30d", "last_reply_at"],
           [["u_1", "b_1", "order", "2026-07-01 10:00", 0, "", 3, 5, 1, 0, ""]])

    message_columns = ["message_id", "user_id", "conversation_type", "group_id", "business_id",
                       "sender_user_id", "created_at", "message_text", "media_type", "media_id",
                       "forwarded_count"]
    _write(tmp_path, "messages.csv", message_columns, [
        ["m_text", "u_1", "group", "g_1", "", "u_9", "2026-07-31 10:00", "hello group", "", "", 0],
        ["m_image", "u_1", "group", "g_1", "", "u_9", "2026-07-31 11:00", "", "image", "img_1", 0],
        ["m_voice", "u_1", "group", "g_1", "", "u_9", "2026-07-31 12:00", "", "voice", "vn_1", 0],
    ])

    _write(tmp_path, "message_history.csv", message_columns, [
        ["h_new", "u_1", "group", "g_1", "", "u_9", "2026-07-10 09:00", "newest", "", "", 0],
        ["h_old", "u_1", "group", "g_1", "", "u_9", "2026-05-01 09:00", "oldest", "", "", 0],
        ["h_mid", "u_1", "group", "g_1", "", "u_9", "2026-06-01 09:00", "middle", "", "", 0],
    ])
    _write(tmp_path, "message_events.csv",
           ["user_id", "message_id", "message_opened", "message_replied", "reaction_time_minutes",
            "notification_dismissed", "muted_after_message", "message_reported"],
           [["u_1", "h_new", 1, 0, 3, 0, 0, 0],
            ["u_1", "h_old", 0, 0, 0, 1, 0, 0],
            ["u_1", "h_mid", 1, 1, 2, 0, 0, 0]])
    _write(tmp_path, "daily_notification_summary.csv",
           ["user_id", "date", "notifications_sent", "notifications_dismissed"],
           [["u_1", "2026-07-04", 2, 1]])
    _write(tmp_path, "images.csv", ["image_id", "file_path"], [["img_1", "media/images/img_1.jpg"]])
    _write(tmp_path, "voice_notes.csv", ["voice_note_id", "file_path"], [["vn_1", "media/audio/vn_1.mp3"]])
    return tmp_path