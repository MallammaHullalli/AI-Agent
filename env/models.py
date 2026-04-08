from dataclasses import dataclass, field
from typing import Literal, Optional

ActionType = Literal["send_bus", "delay_bus", "no_action"]

@dataclass
class BusStopState:
    crowd_size: int                  # number of passengers waiting
    avg_waiting_time: float          # minutes
    bus_arrival_eta: float           # minutes until next bus
    passenger_inflow_rate: float     # passengers per minute
    last_notification: str = ""

    def to_dict(self) -> dict:
        return {
            "crowd_size": self.crowd_size,
            "avg_waiting_time": self.avg_waiting_time,
            "bus_arrival_eta": self.bus_arrival_eta,
            "passenger_inflow_rate": self.passenger_inflow_rate,
            "last_notification": self.last_notification,
        }

@dataclass
class StepResult:
    state: BusStopState
    reward: float
    done: bool
    info: dict = field(default_factory=dict)
