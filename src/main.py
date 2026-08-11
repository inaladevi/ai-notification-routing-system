import time

import pandas as pd

from repository import NotificationRepository
from context_builder import ContextBuilder
from router import Router
from validator import Validator


def main():
    # Load all datasets
    repo = NotificationRepository("dataset").load()

    # Initialize pipeline components
    context_builder = ContextBuilder(repo)
    router = Router(model_name="gemini-3.1-flash-lite")
    print(">>> MAIN ROUTER MODEL:", router.model_name)
    validator = Validator()

    predictions = []

    # Process every incoming message
    for message in repo.get_messages():

        message_id = message["message_id"]

        try:
            context = context_builder.build_context(message)

            prediction = router.route(context)
            prediction = validator.validate(
                message_id,
                prediction,
            )
            predictions.append(prediction)

            time.sleep(5)

        except Exception as e:
            print(f"\nFAILED: {message_id}")
            print(type(e).__name__)
            print(e)
            raise

    # Write submission file
    output = pd.DataFrame(predictions)

    output.to_csv(
        "dataset/output.csv",
        index=False,
    )

    print(f"Generated {len(output)} predictions.")


if __name__ == "__main__":
    main()