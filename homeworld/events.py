"""THE FROZEN EVENT TYPES (NEW_TESTAMENT 3.4, version 1).

Frozen kind list (add = minor bump; rename/remove = forbidden):

RANK_CHANGED    {old, new}
SHIP_BUILT      {ship_id, klass, rank_increased}
SHIP_CAPTURED   {ship_id, rank_increased}
SHIELD_DOWN     {target_id}
SHIELD_PARTIAL  {target_id, residual_norm, error_vector}
ORDER_REJECTED  {order, reason, residual}
ALARM_LEVEL     {level, per_station}
GATE_VOLUME     {volume, ok}
DRILL_STEP      {squad, step_index, subtracted_component}
ROWOP_APPLIED   {matrix_after}
PIVOT_ZERO      {row}
SOLVED          {context_id}
RESOURCE_TICK   {amount, cos_theta}
DOCK_PROGRESS   {deviation_angle}
SHIP_LOST       {ship_id, cause}
MISSION_FLAG    {name, value}
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Event:
    kind: str
    data: dict = field(default_factory=dict)
