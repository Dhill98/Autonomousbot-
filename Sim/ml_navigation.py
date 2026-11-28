"""Train a distance classifier and optionally observe the rover's live readings."""

import argparse
import math
import time
from urllib.request import urlopen

from sklearn.tree import DecisionTreeClassifier


# Synthetic training examples define STOP through 20 cm and CAUTION through 40 cm.
TRAINING_EXAMPLES = [
    (5, "STOP"),
    (10, "STOP"),
    (15, "STOP"),
    (18, "STOP"),
    (20, "STOP"),
    (20.1, "CAUTION"),
    (25, "CAUTION"),
    (30, "CAUTION"),
    (40, "CAUTION"),
    (40.1, "PASS"),
    (45, "PASS"),
    (60, "PASS"),
    (80, "PASS"),
]

# Hold out the original evaluation cases plus readings around both boundaries.
EVALUATION_EXAMPLES = [
    (8, "STOP"),
    (17, "STOP"),
    (19.9, "STOP"),
    (20.2, "CAUTION"),
    (38, "CAUTION"),
    (39.9, "CAUTION"),
    (40.2, "PASS"),
    (50, "PASS"),
    (75, "PASS"),
]


def train_model():
    model = DecisionTreeClassifier(random_state=42)
    model.fit(
        [[distance] for distance, _ in TRAINING_EXAMPLES],
        [label for _, label in TRAINING_EXAMPLES],
    )
    return model


def evaluate_model(model):
    predictions = model.predict([[distance] for distance, _ in EVALUATION_EXAMPLES])
    correct = 0
    for (distance, expected), prediction in zip(EVALUATION_EXAMPLES, predictions):
        correct += prediction == expected
        print(f"{distance:5.1f} cm | predicted {prediction:7} | expected {expected}")

    total = len(EVALUATION_EXAMPLES)
    print(f"Evaluation: {correct}/{total} correct ({correct / total:.0%}, synthetic examples)")


def watch_rover(model, rover_url):
    status_url = f"{rover_url.rstrip('/')}/status"
    print(f"Reading {status_url}. Press Ctrl+C to quit.", flush=True)
    while True:
        try:
            with urlopen(status_url, timeout=3) as response:
                fields = dict(
                    line.split("=", 1)
                    for line in response.read().decode("utf-8").splitlines()
                    if "=" in line
                )
            distance = float(fields["distance_cm"])
            if not math.isfinite(distance) or distance < 0:
                raise ValueError("Invalid distance")
            if distance == 0:
                print("No distance reading yet or no echo", flush=True)
            else:
                prediction = model.predict([[distance]])[0]
                sensor = fields.get("sensor", "unknown")
                print(f"{distance:5.1f} cm | model: {prediction} | rover sensor: {sensor}", flush=True)
        except (OSError, KeyError, ValueError) as error:
            print(f"Could not read rover status: {error}", flush=True)
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", metavar="ROVER_URL", help="ESP32 base URL for a live, read-only demo")
    args = parser.parse_args()

    model = train_model()
    if args.live:
        try:
            watch_rover(model, args.live)
        except KeyboardInterrupt:
            print("\nLive demo ended.")
    else:
        evaluate_model(model)


if __name__ == "__main__":
    main()
