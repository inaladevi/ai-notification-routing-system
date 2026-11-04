from context_builder import ContextBuilder
from repository import NotificationRepository
from validator import Validator


def build(dataset_dir):
    repo = NotificationRepository(str(dataset_dir)).load()
    return repo, ContextBuilder(repo)


def message(repo, message_id):
    return next(m for m in repo.get_messages() if m["message_id"] == message_id)


# ---------- repository / context builder ----------

def test_user_profile_reaches_the_context(dataset_dir):
    # Regression test: users_by_id used to be empty, so every prompt had "profile": null.
    repo, builder = build(dataset_dir)
    context = builder.build_context(message(repo, "m_text"))

    profile = context["user"]["profile"]
    assert profile is not None
    assert profile["messages_opened_30d"] == 45


def test_history_is_the_two_most_recent_messages_oldest_first(dataset_dir):
    repo, builder = build(dataset_dir)
    context = builder.build_context(message(repo, "m_text"))

    assert [item["message_id"] for item in context["history"]] == ["h_mid", "h_new"]


def test_history_keeps_event_signals(dataset_dir):
    repo, builder = build(dataset_dir)
    history = builder.build_context(message(repo, "m_text"))["history"]

    by_id = {item["message_id"]: item for item in history}
    assert by_id["h_mid"]["replied"] == 1
    assert by_id["h_new"]["opened"] == 1


def test_text_message_has_no_media(dataset_dir):
    repo, builder = build(dataset_dir)
    context = builder.build_context(message(repo, "m_text"))

    assert context["media"] is None
    assert context["media_file"] is None


def test_image_message_points_to_its_file(dataset_dir):
    repo, builder = build(dataset_dir)
    context = builder.build_context(message(repo, "m_image"))

    assert context["media"] == {"media_type": "image", "media_id": "img_1"}
    assert str(context["media_file"]).endswith("media/images/img_1.jpg")


def test_voice_message_points_to_its_file(dataset_dir):
    repo, builder = build(dataset_dir)
    context = builder.build_context(message(repo, "m_voice"))

    assert context["media"]["media_type"] == "voice"
    assert str(context["media_file"]).endswith("media/audio/vn_1.mp3")


def test_media_file_path_is_not_in_the_prompt_payload(dataset_dir):
    repo, builder = build(dataset_dir)
    context = builder.build_context(message(repo, "m_image"))

    assert "media/images" not in str(context["media"])


# ---------- validator ----------

def test_invalid_action_and_type_fall_back_to_safe_values():
    result = Validator().validate("m1", {"action": "shout", "message_type": "weird"})

    assert result["action"] == "digest"
    assert result["message_type"] == "unknown"


def test_confidence_is_clamped_between_zero_and_one():
    validator = Validator()

    assert validator.validate("m1", {"confidence": 7})["confidence"] == 1.0
    assert validator.validate("m1", {"confidence": -3})["confidence"] == 0.0
    assert validator.validate("m1", {"confidence": "not a number"})["confidence"] == 0.0


def test_evidence_ids_exclude_the_message_itself():
    result = Validator().validate("m1", {"evidence_message_ids": ["m1", "h1", "h2"]})

    assert result["evidence_message_ids"] == "h1;h2"


def test_empty_evidence_becomes_none():
    assert Validator().validate("m1", {"evidence_message_ids": []})["evidence_message_ids"] == "none"


def test_fallback_prediction_is_flagged_as_a_fallback():
    result = Validator().fallback_prediction("m1")

    assert result["action"] == "digest"
    assert result["confidence"] == 0.0
    assert "Fallback" in result["reason"]