import random
from typing import Tuple, Dict, Any
from .models import BusStopState, StepResult, ActionType

ACTIONS = ["send_bus", "delay_bus", "no_action"]

NOTIFICATION_TEMPLATES = {
    "send_bus": [
        "Extra bus dispatched! Estimated arrival in 3 minutes.",
        "Good news: An additional bus is on its way to reduce wait times.",
        "Extra service activated due to high demand. Bus arriving shortly.",
    ],
    "delay_bus": [
        "Service update: Next bus delayed by 5 minutes due to traffic.",
        "Bus delay notice: Please expect a short wait. We apologize for the inconvenience.",
        "Scheduled bus delayed. Next arrival updated.",
    ],
    "no_action": [
        "All services running on schedule.",
        "Current wait time is within normal range.",
        "No service changes at this time.",
    ],
    "overcrowded": [
        "Stop is currently crowded. Please maintain distance and wait for the next bus.",
        "High passenger volume detected. Extra services may be deployed.",
    ],
    "low_crowd": [
        "Stop is clear. Comfortable boarding expected.",
    ],
}


class BusStopEnv:
    """
    OpenEnv-compatible Smart Bus Stop Crowd Management Environment.
    Difficulty levels: 'easy', 'medium', 'hard'
    """

    DIFFICULTY_CONFIG = {
        "easy": {
            "max_steps": 50,
            "inflow_range": (1.0, 3.0),
            "traffic_delay_prob": 0.0,
            "crowd_variance": 0,
            "bus_capacity": 40,
            "dispatch_cost": 5.0,
        },
        "medium": {
            "max_steps": 75,
            "inflow_range": (1.0, 6.0),
            "traffic_delay_prob": 0.1,
            "crowd_variance": 5,
            "bus_capacity": 35,
            "dispatch_cost": 8.0,
        },
        "hard": {
            "max_steps": 100,
            "inflow_range": (2.0, 10.0),
            "traffic_delay_prob": 0.25,
            "crowd_variance": 10,
            "bus_capacity": 30,
            "dispatch_cost": 12.0,
        },
    }

    def __init__(self, difficulty: str = "medium"):
        assert difficulty in self.DIFFICULTY_CONFIG, f"Unknown difficulty: {difficulty}"
        self.difficulty = difficulty
        self.cfg = self.DIFFICULTY_CONFIG[difficulty]
        self._step_count = 0
        self._state: BusStopState = None
        self.history: list = []

    # ------------------------------------------------------------------
    # OpenEnv API
    # ------------------------------------------------------------------

    def reset(self) -> BusStopState:
        """Initialize environment and return starting state."""
        self._step_count = 0
        self.history = []
        inflow = round(random.uniform(*self.cfg["inflow_range"]), 2)
        self._state = BusStopState(
            crowd_size=random.randint(5, 20),
            avg_waiting_time=round(random.uniform(1.0, 5.0), 2),
            bus_arrival_eta=round(random.uniform(2.0, 10.0), 2),
            passenger_inflow_rate=inflow,
            last_notification="Welcome to Smart Bus Stop. Services are running normally.",
        )
        return self._state

    def state(self) -> BusStopState:
        """Return current observation."""
        return self._state

    def step(self, action: ActionType) -> StepResult:
        """Process action, advance simulation, return StepResult."""
        assert action in ACTIONS, f"Invalid action: {action}"
        assert self._state is not None, "Call reset() before step()"

        self._step_count += 1
        s = self._state
        cfg = self.cfg

        # --- Apply action effects ---
        crowd_after = s.crowd_size
        eta_after = s.bus_arrival_eta
        reward = 0.0

        if action == "send_bus":
            boarded = min(crowd_after, cfg["bus_capacity"])
            crowd_after = max(0, crowd_after - boarded)
            reward += boarded * 0.5          # reward for clearing crowd
            reward -= cfg["dispatch_cost"]   # cost of dispatch
            eta_after = round(random.uniform(5.0, 12.0), 2)  # next bus reset

        elif action == "delay_bus":
            eta_after = s.bus_arrival_eta + 5.0
            reward -= 3.0                    # penalty for delay

        else:  # no_action
            # Natural bus arrival if ETA hits 0
            if s.bus_arrival_eta <= 1.0:
                boarded = min(crowd_after, cfg["bus_capacity"])
                crowd_after = max(0, crowd_after - boarded)
                reward += boarded * 0.3
                eta_after = round(random.uniform(5.0, 12.0), 2)

        # --- Simulate passenger inflow ---
        inflow_variance = random.randint(-cfg["crowd_variance"], cfg["crowd_variance"])
        new_inflow = max(0, s.passenger_inflow_rate + inflow_variance * 0.1)
        crowd_after += int(new_inflow)

        # --- Traffic delay (hard mode) ---
        if random.random() < cfg["traffic_delay_prob"]:
            eta_after += round(random.uniform(1.0, 4.0), 2)

        # --- Update waiting time ---
        new_wait = s.avg_waiting_time + (0.5 if crowd_after > 30 else -0.2)
        new_wait = max(0.0, round(new_wait, 2))

        # --- Reward shaping ---
        if crowd_after > 40:
            reward -= (crowd_after - 40) * 0.3   # overcrowding penalty
        if new_wait > 10:
            reward -= (new_wait - 10) * 0.5      # long wait penalty
        if crowd_after < 20 and new_wait < 5:
            reward += 2.0                         # good state bonus

        # --- Generate notification ---
        notification = self._generate_notification(action, crowd_after, new_wait)
        if notification:
            reward += 0.5  # reward for informative notification

        # --- Update inflow rate (random walk) ---
        new_inflow_rate = round(
            max(0.5, s.passenger_inflow_rate + random.uniform(-0.5, 0.5)), 2
        )

        # --- Build next state ---
        next_state = BusStopState(
            crowd_size=crowd_after,
            avg_waiting_time=new_wait,
            bus_arrival_eta=max(0.0, round(eta_after - 1.0, 2)),
            passenger_inflow_rate=new_inflow_rate,
            last_notification=notification,
        )
        self._state = next_state

        done = self._step_count >= cfg["max_steps"]

        result = StepResult(
            state=next_state,
            reward=round(reward, 3),
            done=done,
            info={
                "step": self._step_count,
                "action": action,
                "notification": notification,
                "crowd_cleared": s.crowd_size - crowd_after + int(new_inflow),
            },
        )
        self.history.append(result)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate_notification(self, action: ActionType, crowd: int, wait: float) -> str:
        msgs = list(NOTIFICATION_TEMPLATES[action])
        if crowd > 40:
            msgs += NOTIFICATION_TEMPLATES["overcrowded"]
        elif crowd < 15:
            msgs += NOTIFICATION_TEMPLATES["low_crowd"]
        return random.choice(msgs)

    @property
    def action_space(self):
        return ACTIONS

    @property
    def observation_space(self):
        return {
            "crowd_size": {"type": "int", "min": 0, "max": 200},
            "avg_waiting_time": {"type": "float", "min": 0.0, "max": 60.0},
            "bus_arrival_eta": {"type": "float", "min": 0.0, "max": 30.0},
            "passenger_inflow_rate": {"type": "float", "min": 0.0, "max": 20.0},
            "last_notification": {"type": "str"},
        }
