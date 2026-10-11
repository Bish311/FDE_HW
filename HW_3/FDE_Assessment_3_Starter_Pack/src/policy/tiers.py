from __future__ import annotations

TIER_1_CEILING = 1000.00
TIER_2_CEILING = 10000.00
TIER_3_CEILING = 25000.00


def compute_approval_tiers(annual_cost_usd: float | None) -> list[str]:
    if annual_cost_usd is None or annual_cost_usd <= 0.0:
        return ["Manager"]

    if annual_cost_usd <= TIER_1_CEILING:
        return ["Manager"]

    if annual_cost_usd <= TIER_2_CEILING:
        return ["Department Head", "Procurement"]

    if annual_cost_usd <= TIER_3_CEILING:
        return ["Department Head", "Finance", "Procurement"]

    return ["Department Head", "Finance", "CFO", "Procurement"]
