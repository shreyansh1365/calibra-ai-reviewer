"""
Calibra Hindsight memory layer.

Each reviewer has a separate Hindsight memory bank.
Every Hindsight operation gets a fresh client and fresh async event loop
so Flask requests never reuse a closed aiohttp session/event loop.
"""

import os
import asyncio
from hindsight_client import Hindsight


def bank_id_for(reviewer_slug: str) -> str:
    return f"reviewer-{reviewer_slug}"


def _make_client():
    return Hindsight(
        base_url=os.environ["HINDSIGHT_BASE_URL"],
        api_key=os.environ["HINDSIGHT_API_KEY"],
    )


# ---------------------------------------------------------
# BANK CREATION
# ---------------------------------------------------------

def ensure_bank(reviewer_slug: str, display_name: str):
    async def _run():
        client = _make_client()

        try:
            bank_id = bank_id_for(reviewer_slug)

            try:
                await client.acreate_bank(
                    bank_id=bank_id,
                    name=display_name
                )
            except Exception:
                # Bank may already exist.
                pass

            return bank_id

        finally:
            await client.aclose()

    return asyncio.run(_run())


# ---------------------------------------------------------
# RETAIN REVIEW
# ---------------------------------------------------------

def retain_review(reviewer_slug: str, content: str):
    async def _run():
        client = _make_client()

        try:
            bank_id = bank_id_for(reviewer_slug)

            return await client.aretain(
                bank_id=bank_id,
                content=content
            )

        finally:
            await client.aclose()

    return asyncio.run(_run())


# ---------------------------------------------------------
# RECALL MEMORY
# ---------------------------------------------------------

def recall_relevant(
    reviewer_slug: str,
    query: str,
    limit: int = 6
):
    """
    Recall reviewer-specific memories from Hindsight.
    This is the main memory operation used during prediction.
    """

    async def _run():
        client = _make_client()

        try:
            bank_id = bank_id_for(reviewer_slug)

            result = await client.arecall(
                bank_id=bank_id,
                query=query
            )

            return [
                m.text for m in result.results
            ][:limit]

        finally:
            await client.aclose()

    return asyncio.run(_run())


# ---------------------------------------------------------
# RECORD ACTUAL HUMAN OUTCOME
# ---------------------------------------------------------

def retain_outcome(
    reviewer_slug: str,
    submission_excerpt: str,
    actual_score: float,
    note: str = ""
):
    """
    Store the actual human review outcome back into Hindsight.
    This creates the learning loop for future predictions.
    """

    async def _run():
        client = _make_client()

        try:
            bank_id = bank_id_for(reviewer_slug)

            content = (
                f'Actual outcome recorded: for a submission opening '
                f'"{submission_excerpt[:160]}...", '
                f'this reviewer scored it {actual_score}/10.'
            )

            if note:
                content += (
                    f" Reviewer's stated reason: {note}"
                )

            return await client.aretain(
                bank_id=bank_id,
                content=content
            )

        finally:
            await client.aclose()

    return asyncio.run(_run())


# ---------------------------------------------------------
# REVIEWER FINGERPRINT
# ---------------------------------------------------------

def reflect_on(
    reviewer_slug: str,
    query: str
):
    """
    Synthesize the reviewer's evaluation fingerprint using Hindsight.
    """

    async def _run():
        client = _make_client()

        try:
            bank_id = bank_id_for(reviewer_slug)

            result = await client.areflect(
                bank_id=bank_id,
                query=query
            )

            return getattr(
                result,
                "text",
                str(result)
            )

        finally:
            await client.aclose()

    return asyncio.run(_run())