import os
import sys
from pathlib import Path
from typing import Dict, List

# Ensure the local src directory is importable when this script runs directly.
SCRIPT_DIR = Path(__file__).resolve().parent
SRC_ROOT = SCRIPT_DIR.parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import pandas as pd

from repository import NotificationRepository
from context_builder import ContextBuilder
from router import Router
from validator import Validator


SAMPLE_MESSAGES_FILE = "sample_messages.csv"
EVALUATION_REPORT_FILE = "evaluation_report.md"


def load_sample_messages(dataset_dir: Path) -> List[Dict[str, str]]:
    sample_path = dataset_dir / SAMPLE_MESSAGES_FILE
    sample_df = pd.read_csv(sample_path, dtype=str).fillna("")
    return sample_df.to_dict("records")


def initialize_pipeline(dataset_dir: Path):
    repo = NotificationRepository(str(dataset_dir)).load()
    context_builder = ContextBuilder(repo)
    validator = Validator()

    router = None
    model_name = os.getenv("EVALUATION_MODEL_NAME", "gemini-3.1-flash-lite")

    try:
        router = Router(model_name=model_name)
    except Exception as exc:
        if isinstance(exc, ValueError) and "GEMINI_API_KEY" in str(exc):
            print("WARNING: GEMINI_API_KEY is missing. Router is disabled.")
        else:
            print("WARNING: Router initialization failed.")
        print("         Falling back to validator-only predictions.")
        print(f"         {type(exc).__name__}: {exc}")

    return repo, context_builder, router, validator


def predict_message(
    message: Dict[str, str],
    context_builder: ContextBuilder,
    router: Router,
    validator: Validator,
) -> Dict[str, object]:
    message_id = message["message_id"]

    try:
        context = context_builder.build_context(message)

        if router is None:
            raise RuntimeError("Router is unavailable")

        prediction = router.route(context)
    except Exception as exc:
        print(f"WARNING: prediction failed for {message_id}: {exc}")
        prediction = validator.fallback_prediction(message_id)

    return validator.validate(message_id, prediction)


def compute_metrics(
    predictions: List[Dict[str, object]],
    sample_messages: List[Dict[str, str]],
) -> Dict[str, object]:
    total = len(sample_messages)
    if total == 0:
        return {
            "total_messages": 0,
            "action_accuracy": 0.0,
            "message_type_accuracy": 0.0,
            "average_confidence": 0.0,
            "correct_action_count": 0,
            "correct_message_type_count": 0,
        }

    correct_action = 0
    correct_message_type = 0
    total_confidence = 0.0

    for prediction, sample in zip(predictions, sample_messages):
        expected_action = sample.get("action", "").strip()
        expected_type = sample.get("message_type", "").strip()

        if prediction["action"] == expected_action:
            correct_action += 1

        if prediction["message_type"] == expected_type:
            correct_message_type += 1

        total_confidence += float(prediction.get("confidence", 0.0))

    return {
        "total_messages": total,
        "correct_action_count": correct_action,
        "correct_message_type_count": correct_message_type,
        "action_accuracy": correct_action / total,
        "message_type_accuracy": correct_message_type / total,
        "average_confidence": total_confidence / total,
    }


def format_percentage(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_report(report_path: Path, metrics: Dict[str, object], used_fallback: bool, model_name: str):
    router_status = "Enabled" if not used_fallback else "Disabled"

    lines = [
        "# Evaluation Report",
        "",
        "This report summarizes the sample routing evaluation on `dataset/sample_messages.csv`.",
        "The evaluation compares model predictions against the labeled sample messages provided with the dataset.",
        "",
        f"- Model: `{model_name}`",
        f"- LLM Router: {router_status}",
        "",
        "## Metrics",
        "",
        f"- Total evaluated messages: **{metrics['total_messages']}**",
        f"- Action accuracy: **{metrics['correct_action_count']}/{metrics['total_messages']} ({format_percentage(metrics['action_accuracy'])})**",
        f"- Message type accuracy: **{metrics['correct_message_type_count']}/{metrics['total_messages']} ({format_percentage(metrics['message_type_accuracy'])})**",
        f"- Average confidence: **{metrics['average_confidence']:.3f}**",
        "",
    ]

    if used_fallback:
        lines.extend([
            "## Notes",
            "",
            "- The routing model was unavailable during this evaluation.",
            "- Predictions were generated using the validator fallback behavior, which defaults to `digest` and `unknown`.",
            "- Set `GEMINI_API_KEY` and rerun the pipeline for model-driven evaluation.",
            "",
        ])

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    root_dir = Path(__file__).resolve().parents[2]
    dataset_dir = root_dir / "dataset"
    report_path = Path(__file__).resolve().parent / EVALUATION_REPORT_FILE

    sample_messages = load_sample_messages(dataset_dir)
    repo, context_builder, router, validator = initialize_pipeline(dataset_dir)

    predictions = []
    for sample in sample_messages:
        prediction = predict_message(sample, context_builder, router, validator)
        predictions.append(prediction)

    metrics = compute_metrics(predictions, sample_messages)
    write_report(report_path, metrics, used_fallback=(router is None), model_name=os.getenv("EVALUATION_MODEL_NAME", "gemini-3.1-flash-lite"))

    print("Evaluation results")
    print("------------------")
    print(f"Total evaluated messages: {metrics['total_messages']}")
    print(f"Action accuracy: {format_percentage(metrics['action_accuracy'])}")
    print(f"Message type accuracy: {format_percentage(metrics['message_type_accuracy'])}")
    print(f"Average confidence: {metrics['average_confidence']:.3f}")
    print(f"Report written to: {report_path}")


if __name__ == "__main__":
    main()
