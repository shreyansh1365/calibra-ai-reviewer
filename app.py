import logging

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template

from memory_bank import recall_relevant, retain_outcome, reflect_on
from groq_client import predict_review, explain_disagreement
from seed_data import REVIEWERS, DEMO_SUBMISSIONS

app = Flask(__name__)
log = logging.getLogger("calibra")
logging.basicConfig(level=logging.INFO)

DISAGREEMENT_THRESHOLD = 2.0  # points apart, out of 10
FINGERPRINT_QUERY = (
    "Summarize this reviewer's evaluation style: what do they weigh most heavily, "
    "what do they consistently let slide, and how has that shifted with any recent outcomes?"
)

# Simple in-process counter so the UI can visibly show each bank growing
# (seeded from the history length in seed_data.py). This is purely a
# display convenience - the actual memory lives in Hindsight, not here.
memory_counts = {r["slug"]: len(r["history"]) for r in REVIEWERS}

REVIEWER_NAMES = {r["slug"]: r["name"] for r in REVIEWERS}


def safe_call(fn, *args, fallback=None, label="operation", **kwargs):
    """Every external call (Hindsight, Groq) goes through this. A live
    demo should never die on stage because of a flaky network call or a
    missing API key - it should degrade visibly and keep going. Errors
    are logged in full server-side; the caller only ever sees a short,
    honest, non-technical message."""
    try:
        return fn(*args, **kwargs), None
    except Exception as e:
        log.exception("%s failed", label)
        return fallback, f"{label} is temporarily unavailable ({e.__class__.__name__})."


@app.route("/")
def index():
    return render_template(
        "index.html",
        reviewers=REVIEWERS,
        demo_submissions=DEMO_SUBMISSIONS,
        memory_counts=memory_counts,
    )


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    submission_text = data.get("submission_text", "").strip()
    if not submission_text:
        return jsonify({"error": "submission_text is required"}), 400

    predictions = []
    for reviewer in REVIEWERS:
        slug, name = reviewer["slug"], reviewer["name"]

        recalled, recall_err = safe_call(
            recall_relevant, slug, submission_text, fallback=[], label="memory recall"
        )
        if recall_err:
            predictions.append({
                "reviewer_name": name,
                "predicted_score": None,
                "confidence": "low",
                "feedback": recall_err,
                "grounded_in": [],
                "recalled_memories": [],
            })
            continue

        prediction, predict_err = safe_call(
            predict_review, name, submission_text, recalled,
            fallback=None, label="score prediction",
        )
        if predict_err:
            predictions.append({
                "reviewer_name": name,
                "predicted_score": None,
                "confidence": "low",
                "feedback": predict_err,
                "grounded_in": [],
                "recalled_memories": recalled,
            })
            continue

        prediction["recalled_memories"] = recalled
        predictions.append(prediction)

    disagreement = None
    scores = [p.get("predicted_score") for p in predictions if p.get("predicted_score") is not None]
    if len(scores) == 2 and abs(scores[0] - scores[1]) >= DISAGREEMENT_THRESHOLD:
        explanation, explain_err = safe_call(
            explain_disagreement, predictions[0], predictions[1],
            fallback="(explanation unavailable right now)", label="disagreement explanation",
        )
        disagreement = {"gap": round(abs(scores[0] - scores[1]), 1), "explanation": explanation}

    return jsonify({"predictions": predictions, "disagreement": disagreement})


@app.route("/api/record-outcome", methods=["POST"])
def record_outcome():
    """Close the loop: a human tells Calibra what a reviewer actually
    scored a submission. We retain that as a new memory in the
    reviewer's bank, so the NEXT prediction for a similar submission is
    grounded in this real outcome, not just the seed history. This is
    what makes the demo show learning, not just lookup."""
    data = request.get_json(force=True)
    slug = data.get("reviewer_slug")
    submission_text = data.get("submission_text", "").strip()
    actual_score = data.get("actual_score")
    note = data.get("note", "").strip()

    if slug not in memory_counts:
        return jsonify({"error": "unknown reviewer_slug"}), 400
    if not submission_text or actual_score is None:
        return jsonify({"error": "submission_text and actual_score are required"}), 400

    _, err = safe_call(
        retain_outcome, slug, submission_text, actual_score, note,
        label="writing outcome to memory",
    )
    if err:
        return jsonify({"error": err}), 502

    memory_counts[slug] += 1
    return jsonify({"ok": True, "reviewer_slug": slug, "memory_count": memory_counts[slug]})


@app.route("/api/fingerprint", methods=["POST"])
def fingerprint():
    """Reviewer fingerprint: asks Hindsight to SYNTHESIZE (reflect(), not
    just recall()) everything a reviewer's bank knows into one paragraph.
    Run this before and after recording an outcome to show the synthesis
    itself shift - not just a retrieved memory, but the reviewer's
    overall evaluated 'taste' changing."""
    data = request.get_json(force=True)
    slug = data.get("reviewer_slug")
    if slug not in memory_counts:
        return jsonify({"error": "unknown reviewer_slug"}), 400

    summary, err = safe_call(
        reflect_on, slug, FINGERPRINT_QUERY, label="reviewer fingerprint"
    )
    if err:
        return jsonify({"error": err}), 502

    return jsonify({
        "reviewer_slug": slug,
        "reviewer_name": REVIEWER_NAMES[slug],
        "fingerprint": summary,
        "memory_count": memory_counts[slug],
    })


if __name__ == "__main__":
    app.run(debug=True, port=5050)
