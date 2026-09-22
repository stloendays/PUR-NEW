"""Named decision conditions for the Agent V5 comparison.

A *condition* is the scientific scenario a comparison runs inside: the decision
question, the registered hypotheses, the declared measurement plans and the VOI
weights. An *arm* is whether the chemistry-domain applicability audit is enforced
inside that scenario.

Both arms of a comparison always run under one condition, so the arm contrast stays
exactly the enforcement flag. Conditions are never compared arm-to-arm across the
boundary: that would confound the scenario with the enforcement.

Condition ``A_drift`` is the frozen original and resolves to the unmodified
``BASE_WEIGHTS``, the drift registry and the drift catalog, so it reproduces the
existing ``results/agent_v5/comparison_n10`` series exactly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "configs"

CONDITIONS_FILE = CONFIG_DIR / "decision_conditions.json"


def load_conditions(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or CONDITIONS_FILE).read_text(encoding="utf-8"))


def default_condition_id(path: Path | None = None) -> str:
    return str(load_conditions(path)["default_condition"])


def condition_ids(path: Path | None = None) -> list[str]:
    return sorted(load_conditions(path)["conditions"])


def load_condition(condition_id: str | None = None, *, path: Path | None = None) -> dict[str, Any]:
    """Resolve one condition into its registry, catalog, weights and declared metadata.

    ``voi_weights`` of ``null`` means the unmodified ``BASE_WEIGHTS`` of ``voi.py``.
    The resolved weights are returned as ``None`` in that case so the caller keeps the
    original default object rather than a copy that could drift from it.
    """
    from .voi import BASE_WEIGHTS  # imported here to avoid an import cycle at module load

    config = load_conditions(path)
    resolved_id = condition_id or config["default_condition"]
    if resolved_id not in config["conditions"]:
        raise KeyError(
            f"unknown decision condition {resolved_id!r}; declared conditions are "
            f"{sorted(config['conditions'])}"
        )
    declared = config["conditions"][resolved_id]

    registry_path = ROOT / declared["hypothesis_registry"]
    catalog_path = ROOT / declared["measurement_catalog"]
    weights = declared.get("voi_weights")

    if weights is not None:
        missing = set(BASE_WEIGHTS) - set(weights)
        if missing:
            raise ValueError(
                f"condition {resolved_id!r} declares VOI weights but omits base terms {sorted(missing)}"
            )

    return {
        "condition_id": resolved_id,
        "title": declared["title"],
        "decision_question": declared["decision_question"],
        "status": declared.get("status"),
        "protocol": declared.get("protocol"),
        "hypothesis_registry_path": str(registry_path),
        "measurement_catalog_path": str(catalog_path),
        "registry": json.loads(registry_path.read_text(encoding="utf-8")),
        "catalog": json.loads(catalog_path.read_text(encoding="utf-8")),
        "weights": dict(weights) if weights is not None else None,
        "weights_are_base_defaults": weights is None,
        "declared": declared,
    }
