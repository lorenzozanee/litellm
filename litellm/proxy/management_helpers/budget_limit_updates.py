import json
from collections.abc import Mapping, Sequence
from typing import Final

from fastapi import HTTPException

from litellm.proxy.common_utils.timezone_utils import get_budget_reset_time


def synchronize_matching_budget_limit_window(
    *,
    existing_windows: Sequence[Mapping[str, object]],
    current_max_budget: float | None,
    current_budget_duration: str | None,
    updated_max_budget: float | None,
    updated_budget_duration: str | None,
) -> str | None:
    if current_max_budget is None or current_budget_duration is None:
        return None

    matches: Final = tuple(
        index
        for index, window in enumerate(existing_windows)
        if window.get("max_budget") == current_max_budget and window.get("budget_duration") == current_budget_duration
    )
    if not matches:
        return None
    if len(matches) > 1:
        raise HTTPException(
            status_code=400,
            detail="Multiple budget windows match the existing scalar budget; include budget_limits in the update.",
        )

    matched_index: Final = next(iter(matches))
    if updated_max_budget is None or updated_budget_duration is None:
        remaining_windows: Final = tuple(
            dict(window) for index, window in enumerate(existing_windows) if index != matched_index
        )
        return json.dumps(remaining_windows or None, default=str)

    updated_window: Final = {
        **dict(existing_windows[matched_index]),
        "max_budget": updated_max_budget,
        "budget_duration": updated_budget_duration,
        **(
            {"reset_at": get_budget_reset_time(budget_duration=updated_budget_duration).isoformat()}
            if updated_budget_duration != current_budget_duration
            else {}
        ),
    }

    synchronized_windows: Final = tuple(
        updated_window if index == matched_index else dict(window) for index, window in enumerate(existing_windows)
    )
    return json.dumps(synchronized_windows, default=str)
