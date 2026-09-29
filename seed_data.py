"""
Synthetic historical review data for two legal-editorial reviewers.
Realistic in texture (specific case names, specific corrections) rather
than generic "good job / needs work" filler - this is what the hackathon
brief calls out as the #1 thing that makes a demo look real.

Run: python seed_data.py
"""

REVIEWERS = [
    {
        "slug": "priya",
        "name": "Priya Menon",
        "history": [
            "Docked 2 points on Ashish Kumar's arbitration clause memo for citing Bharat Aluminium Co. v. Kaiser Aluminium without a pinpoint page reference - I always require pinpoint citations for Supreme Court judgments.",
            "Praised Asmita Verma's contract-interpretation note for using the IRAC structure cleanly, but noted the conclusion was buried in paragraph 4 instead of stated up front.",
            "Rejected a submission from Ashna Ahmad for citing a High Court judgment that was later overruled - flagged that citation currency checks are non-negotiable for me.",
            "Told Avantika Sirohi her footnote formatting was inconsistent (mixing Bluebook and OSCOLA styles in one memo) - I weigh citation consistency heavily, more than most reviewers on this team.",
            "Gave Ashmit Srivastav full marks on a data-privacy brief specifically because every statutory reference included the exact section and subsection number, not just the Act name.",
            "Noted that I consistently score submissions lower when the author paraphrases a judgment's holding instead of quoting the operative portion precisely - precision over prose style, every time.",
            "Flagged a submission for using 'ibid' incorrectly after a string citation - small errors like this compound in my scoring because they signal the author didn't proofread the citation trail.",
            "Complimented a submission for front-loading the strongest precedent first rather than chronologically - I reward argument sequencing that leads with the strongest authority.",
        ],
    },
    {
        "slug": "arjun",
        "name": "Arjun Rao",
        "history": [
            "Gave Ashish Kumar's arbitration memo high marks despite a missing pinpoint citation - the underlying analysis of severability was original and well-reasoned, which matters more to me than citation mechanics.",
            "Marked down Asmita Verma's contract note for restating textbook doctrine without adding original analysis - I actively penalize submissions that read like a summary rather than an argument.",
            "Praised Ashna Ahmad for raising a counter-argument the prompt didn't ask for and then rebutting it - I reward writers who anticipate the opposing side unprompted.",
            "Told Avantika Sirohi that footnote formatting inconsistencies don't move my score much as long as the substantive analysis is sound - I care much less about citation style than about the reasoning.",
            "Scored Ashmit Srivastav's data-privacy brief lower than expected because the analysis stayed purely descriptive of the statute instead of applying it to a hypothetical fact pattern.",
            "I consistently reward submissions that take a clear normative position ('this provision should be read narrowly because...') over ones that stay neutral and descriptive throughout.",
            "Noted that I rarely penalize minor citation formatting errors unless they make a source impossible to locate - the substance of the argument is what I'm grading.",
            "Gave a submission a lower score for being well-cited but derivative - it read like a case brief, not an original legal argument, and originality is the criterion I weigh most heavily.",
        ],
    },
]

# Submissions to run through the demo, in order - designed to show the
# system recognizing real disagreement patterns, not random noise.
DEMO_SUBMISSIONS = [
    {
        "title": "Memo on force majeure clauses post-pandemic",
        "text": (
            "This memo argues that force majeure clauses should be interpreted narrowly "
            "post-pandemic, restating the holding in Energy Watchdog v. CERC without a "
            "pinpoint citation. The analysis largely summarizes existing commentary and "
            "does not apply the doctrine to a new fact pattern or take a clear position "
            "on how courts should treat hybrid work disruptions."
        ),
    },
    {
        "title": "Note on arbitral seat vs venue distinction",
        "text": (
            "This note takes the position that Indian courts have conflated 'seat' and "
            "'venue' in arbitration clauses, and argues (with an original hypothetical) "
            "that this conflation undermines party autonomy. Citations are present but "
            "inconsistently formatted, mixing Bluebook and OSCOLA styles, and one "
            "Supreme Court citation is missing a pinpoint page reference."
        ),
    },
    {
        "title": "Follow-up: seat vs venue in maritime arbitration",
        "text": (
            "This follow-up note extends the seat-versus-venue argument to maritime "
            "arbitration clauses, again with an original hypothetical involving a "
            "shipping dispute. Citations mix Bluebook and OSCOLA styles as before, and "
            "one Supreme Court citation is again missing a pinpoint page reference."
        ),
    },
]
