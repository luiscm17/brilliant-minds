"""Adaptation Agent (AAM) — main orchestrator for the DocSimplify pipeline.

Flow:
  1. Receives user message + profile + RAG context chunks
  2. Builds the text to simplify (from message or RAG context)
  3. Calls SimplifierAgent
  4. Calls CalmEvaluatorAgent (up to 2 iterations if not approved)
  5. Calls ExplainerAgent
  6. Calls ValidatorAgent
  7. Returns SimplifiedResponse
"""

from src.agents.simplifier_agent import simplifier_agent
from src.agents.explainer_agent import explainer_agent
from src.agents.calm_evaluator import calm_evaluator_agent
from src.agents.validator_agent import validate
from src.models.schemas import SimplifiedResponse, UserProfile


async def run_adaptation_pipeline(
    message: str,
    profile: UserProfile,
    rag_chunks: list[str],
) -> SimplifiedResponse:
    """Execute the full multi-agent adaptation pipeline."""

    # Build source text: prefer RAG context if documents were referenced
    source_text = "\n\n".join(rag_chunks) if rag_chunks else message

    # Step 1: Simplify
    simplifier = await simplifier_agent()
    simplified = await simplifier.run(
        text=source_text,
        reading_level=profile.reading_level,
        preset=profile.preset,
        avoid_words=profile.avoid_words,
    )

    # Step 2: Calm evaluation (max 2 iterations)
    calm = await calm_evaluator_agent()
    for _ in range(2):
        calm_result = await calm.run(simplified)
        if calm_result.approved:
            break
        simplified = calm_result.corrected_text

    # Step 3: Generate explanation
    explainer = await explainer_agent()
    explanation = await explainer.run(original=source_text, simplified=simplified)

    # Step 4: Validate
    wcag_report = validate(
        text=simplified,
        reading_level=profile.reading_level,
        avoid_words=profile.avoid_words,
    )

    return SimplifiedResponse(
        original_message=message,
        simplified_text=simplified,
        explanation=explanation,
        wcag_report=wcag_report,
        preset_used=profile.preset,
        reading_level_used=profile.reading_level,
    )
