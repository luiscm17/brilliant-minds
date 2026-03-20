"""Validator Agent — programmatic WCAG/accessibility validation of simplified text."""

from src.models.schemas import WcagReport


def validate(text: str, reading_level: str, avoid_words: list[str]) -> WcagReport:
    """Validate the simplified text against accessibility rules. Returns a WcagReport."""
    issues = []
    score = 100

    sentences = [s.strip() for s in text.replace("\n", ". ").split(".") if s.strip()]
    if not sentences:
        return WcagReport(score=0, passed=False, issues=["Text is empty"])

    # Rule 1: Average sentence length
    level_limits = {"A1": 8, "A2": 12, "B1": 18, "B2": 22, "C1": 28}
    limit = level_limits.get(reading_level, 15)
    avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
    if avg_words > limit:
        penalty = min(30, int((avg_words - limit) * 3))
        score -= penalty
        issues.append(
            f"Average sentence length ({avg_words:.1f} words) exceeds limit for {reading_level} ({limit} words)"
        )

    # Rule 2: Forbidden words still present
    found_forbidden = [w for w in avoid_words if w.lower() in text.lower()]
    if found_forbidden:
        score -= len(found_forbidden) * 10
        issues.append(f"Forbidden words still present: {', '.join(found_forbidden)}")

    # Rule 3: Minimum content structure
    word_count = len(text.split())
    if word_count < 10:
        score -= 20
        issues.append("Text is too short to be meaningful")

    score = max(0, score)
    return WcagReport(score=score, passed=score >= 70, issues=issues)
