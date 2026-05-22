"""Deterministic KPI calculation helpers for the MVP application."""

from __future__ import annotations


def safe_percent_reduction(before: float, after: float) -> float:
    if before <= 0:
        return 0.0
    return ((before - after) / before) * 100


def calculate_time_saving(time_before: float, time_after: float) -> float:
    return safe_percent_reduction(time_before, time_after)


def calculate_quality_change(quality_before: float, quality_after: float) -> float:
    return quality_after - quality_before


def calculate_cost_saving(
    time_before: float,
    time_after: float,
    cost_per_hour: float,
) -> float:
    if cost_per_hour <= 0:
        return 0.0
    saved_hours = max(time_before - time_after, 0) / 60
    return saved_hours * cost_per_hour


def normalize_percent(value: float) -> float:
    return max(0.0, min(value / 100, 1.0))


def normalize_quality_change(change: float) -> float:
    return max(0.0, min(change / 10, 1.0))


def calculate_efficiency_index(
    time_saving_percent: float,
    quality_change: float,
    clarification_reduction_percent: float,
    risk_reduction_percent: float,
) -> float:
    return (
        0.35 * normalize_percent(time_saving_percent)
        + 0.30 * normalize_quality_change(quality_change)
        + 0.20 * normalize_percent(clarification_reduction_percent)
        + 0.15 * normalize_percent(risk_reduction_percent)
    )


def build_kpi_conclusion(
    time_saving: float,
    quality_change: float,
    clarification_reduction: float,
    risk_reduction: float,
) -> str:
    positive_factors = []

    if time_saving > 0:
        positive_factors.append("reducing execution time")
    if quality_change > 0:
        positive_factors.append("improving task quality")
    if clarification_reduction > 0:
        positive_factors.append("decreasing clarifications")
    if risk_reduction > 0:
        positive_factors.append("reducing defects or risks")

    if not positive_factors:
        return (
            "The entered KPI values do not show measurable process improvement. "
            "Review whether AI support changed time, quality, clarifications, or risk outcomes."
        )

    if len(positive_factors) == 1:
        focus = positive_factors[0]
    else:
        focus = ", ".join(positive_factors[:-1]) + f", and {positive_factors[-1]}"

    return (
        f"The use of AI improved the process mainly by {focus}. "
        "This indicates that the AI-supported workflow can be considered useful for this task type."
    )


def calculate_kpis(
    time_before_minutes: float,
    time_after_minutes: float,
    quality_before: float,
    quality_after: float,
    clarifications_before: float,
    clarifications_after: float,
    defects_before: float,
    defects_after: float,
    cost_per_hour: float = 0.0,
) -> dict[str, float]:
    """Calculate all KPI values required by the application."""

    time_saving_percent = calculate_time_saving(
        time_before_minutes,
        time_after_minutes,
    )
    quality_change = calculate_quality_change(quality_before, quality_after)
    clarification_reduction_percent = safe_percent_reduction(
        clarifications_before,
        clarifications_after,
    )
    defect_risk_change_percent = safe_percent_reduction(defects_before, defects_after)
    cost_saving = calculate_cost_saving(
        time_before_minutes,
        time_after_minutes,
        cost_per_hour,
    )
    efficiency_index = calculate_efficiency_index(
        time_saving_percent,
        quality_change,
        clarification_reduction_percent,
        defect_risk_change_percent,
    )

    return {
        "time_saving_percent": round(time_saving_percent, 2),
        "quality_change": round(quality_change, 2),
        "clarification_reduction_percent": round(
            clarification_reduction_percent, 2
        ),
        "defect_risk_change_percent": round(defect_risk_change_percent, 2),
        "cost_saving": round(cost_saving, 2),
        "efficiency_index": round(efficiency_index, 4),
    }


def build_conclusion(metrics: dict[str, float]) -> str:
    """Backward-compatible wrapper used by app.py."""

    return build_kpi_conclusion(
        metrics["time_saving_percent"],
        metrics["quality_change"],
        metrics["clarification_reduction_percent"],
        metrics["defect_risk_change_percent"],
    )
