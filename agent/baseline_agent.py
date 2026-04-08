from env.models import BusStopState, ActionType

class BaselineAgent:
    """
    Heuristic baseline agent for reproducibility.
    Rules:
      - send_bus  if crowd > 35 or (crowd > 20 and wait > 8)
      - delay_bus if crowd < 5 and eta < 3
      - no_action otherwise
    """

    def __init__(self, crowd_threshold: int = 35, wait_threshold: float = 8.0):
        self.crowd_threshold = crowd_threshold
        self.wait_threshold = wait_threshold

    def act(self, state: BusStopState) -> ActionType:
        if state.crowd_size > self.crowd_threshold:
            return "send_bus"
        if state.crowd_size > 20 and state.avg_waiting_time > self.wait_threshold:
            return "send_bus"
        if state.crowd_size < 5 and state.bus_arrival_eta < 3.0:
            return "delay_bus"
        return "no_action"
