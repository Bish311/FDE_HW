from __future__ import annotations

import json

from src.llm.client import call_openrouter

MODEL_LUNA = "openai/gpt-6-luna"


def synthesize_recommendation_and_next_step(
    request_data: dict[str, object],
    policy_summary: dict[str, object],
    evidence_findings: list[str],
) -> dict[str, str]:
    evidence_text = "\n".join(evidence_findings)
    flags_text = ", ".join(policy_summary.get("risk_flags", []))
    approvals_text = ", ".join(policy_summary.get("required_approvals", []))

    prompt = (
        f"Purchase Request: {request_data.get('product_name')} by {request_data.get('requester_id')}\n"
        f"Cost: ${request_data.get('annual_cost_usd')}\n"
        f"Risk Flags: {flags_text}\n"
        f"Required Approvals: {approvals_text}\n"
        f"Evidence Findings:\n{evidence_text}\n\n"
        "Generate a JSON object with two fields:\n"
        "1. 'recommendation': Concise 1-2 sentence recommendation grounded in evidence.\n"
        "2. 'next_step': Concise 1-2 sentence clear next action for the requester or reviewer."
    )
    messages = [
        {"role": "system", "content": "You are a professional procurement copilot. Ground all statements strictly in the provided evidence. Output JSON only."},
        {"role": "user", "content": prompt},
    ]

    raw = call_openrouter(MODEL_LUNA, messages, reasoning_effort="medium", json_mode=True)
    if raw is not None:
        choices = raw.get("choices")
        if isinstance(choices, list) and len(choices) > 0:
            content = choices[0].get("message", {}).get("content", "")
            try:
                parsed = json.loads(content)
                rec = str(parsed.get("recommendation") or "").strip()
                step = str(parsed.get("next_step") or "").strip()
                if rec and step:
                    return {"recommendation": rec, "next_step": step}
            except (json.JSONDecodeError, ValueError):
                pass

    route = str(policy_summary.get("recommended_route") or "manual_review")
    return _fallback_copy(route, request_data, policy_summary)


def _fallback_copy(
    route: str,
    req: dict[str, object],
    policy: dict[str, object],
) -> dict[str, str]:
    prod = str(req.get("product_name") or "the requested tool")
    if route == "request_clarification":
        return {
            "recommendation": f"Return request for {prod} to requester for clarification.",
            "next_step": "Provide the missing cost, license count, or data-access details to proceed with policy review.",
        }
    if route == "escalate_security_review":
        return {
            "recommendation": f"Escalate {prod} immediately to Security due to untrusted prompt instructions.",
            "next_step": "Security team must inspect the request payload before any review can resume.",
        }
    if route == "escalate_manual_review":
        return {
            "recommendation": f"Route {prod} to manual procurement review due to vendor data discrepancies or service outage.",
            "next_step": "Procurement officer must verify vendor security compliance directly.",
        }
    if route == "finance_budget_exception":
        return {
            "recommendation": f"Hold {prod} pending Finance review due to insufficient departmental software budget.",
            "next_step": "Department Head must submit a formal budget exception request to Finance.",
        }
    if route == "specialist_review":
        return {
            "recommendation": f"Route {prod} for specialist approvals based on data sensitivity and vendor risk.",
            "next_step": "Complete Security, Privacy, and Legal reviews before committing spend.",
        }
    if route == "evaluate_existing_alternatives":
        return {
            "recommendation": f"Review existing catalog tools for {prod} before authorizing duplicate software.",
            "next_step": "Validate whether existing tooling satisfies the stated business justification.",
        }
    return {
        "recommendation": f"Recommend routing {prod} for standard management approvals.",
        "next_step": "Obtain required signatures through standard procurement workflow.",
    }
