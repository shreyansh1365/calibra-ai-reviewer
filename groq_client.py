"""
Wrapper around Groq for generating a reviewer's predicted evaluation.

The LLM never invents a reviewer's taste from scratch - it is always
grounded in the specific memories Hindsight recalled for that reviewer,
which are passed in as `recalled_memories`. That grounding is what we
show judges as "why the agent said this."
"""

import os
import json
from groq import Groq

_client = None


def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


PREDICT_SYSTEM_PROMPT = """You are simulating how a specific legal-submission \
reviewer would evaluate a new piece of writing, based ONLY on memories of \
that reviewer's past evaluations. Do not invent preferences that are not \
supported by the memories. If the memories are sparse, say the prediction \
is low-confidence rather than guessing.

Respond ONLY with JSON, no markdown fences, no preamble, matching exactly:
{
  "reviewer_name": string,
  "predicted_score": number,        // 1-10
  "confidence": "low" | "medium" | "high",
  "feedback": string,               // 2-4 sentences, in this reviewer's voice
  "grounded_in": [string]           // which recalled memories drove this, verbatim or near-verbatim
}
"""


def predict_review(reviewer_name: str, submission_text: str, recalled_memories: list[str]) -> dict:
    client = get_client()
    memories_block = "\n".join(f"- {m}" for m in recalled_memories) or "(no relevant memories recalled)"

    user_prompt = f"""Reviewer: {reviewer_name}

Memories recalled about this reviewer's past evaluations:
{memories_block}

New submission to evaluate:
\"\"\"
{submission_text}
\"\"\"

Predict how {reviewer_name} would score and comment on this submission."""

    resp = client.chat.completions.create(
        model=os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
        messages=[
            {"role": "system", "content": PREDICT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )
    raw = resp.choices[0].message.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "reviewer_name": reviewer_name,
            "predicted_score": None,
            "confidence": "low",
            "feedback": raw,
            "grounded_in": [],
        }


DISAGREEMENT_SYSTEM_PROMPT = """You explain, in 2-3 sentences, WHY two legal \
reviewers predicted different scores for the same submission, using only the \
grounding evidence given. Be specific about which evaluation criterion each \
reviewer weighs differently. Plain text only, no JSON."""


def explain_disagreement(reviewer_a: dict, reviewer_b: dict) -> str:
    client = get_client()
    user_prompt = f"""Reviewer A ({reviewer_a['reviewer_name']}): score {reviewer_a.get('predicted_score')}, \
grounded in: {reviewer_a.get('grounded_in')}

Reviewer B ({reviewer_b['reviewer_name']}): score {reviewer_b.get('predicted_score')}, \
grounded in: {reviewer_b.get('grounded_in')}

Why would they disagree?"""
    resp = client.chat.completions.create(
        model=os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
        messages=[
            {"role": "system", "content": DISAGREEMENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )
    return resp.choices[0].message.content.strip()
