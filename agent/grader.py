from dataclasses import dataclass
from typing import List
from env.models import StepResult

@dataclass
class GradeReport:
    total_reward: float
    efficiency_score: float       # 0-1: reward per step normalized
    crowd_control_score: float    # 0-1: steps with crowd < 30
    communication_score: float    # 0-1: steps with non-empty notifications
    overall_score: float          # 0-1 weighted average

    def __str__(self):
        return (
            f"Overall Score   : {self.overall_score:.3f}\n"
            f"Efficiency      : {self.efficiency_score:.3f}\n"
            f"Crowd Control   : {self.crowd_control_score:.3f}\n"
            f"Communication   : {self.communication_score:.3f}\n"
            f"Total Reward    : {self.total_reward:.2f}"
        )


class AgentGrader:
    """Evaluates agent performance on a 0.0–1.0 scale."""

    MAX_REWARD_PER_STEP = 10.0   # normalization constant

    def grade(self, history: List[StepResult]) -> GradeReport:
        if not history:
            return GradeReport(0, 0, 0, 0, 0)

        n = len(history)
        total_reward = sum(r.reward for r in history)

        # Efficiency: normalize cumulative reward
        max_possible = self.MAX_REWARD_PER_STEP * n
        efficiency = max(0.0, min(1.0, (total_reward + max_possible) / (2 * max_possible)))

        # Crowd control: fraction of steps where crowd < 30
        crowd_ok = sum(1 for r in history if r.state.crowd_size < 30)
        crowd_control = crowd_ok / n

        # Communication: fraction of steps with a notification
        notified = sum(1 for r in history if r.info.get("notification", ""))
        communication = notified / n

        overall = round(0.4 * efficiency + 0.4 * crowd_control + 0.2 * communication, 4)

        return GradeReport(
            total_reward=round(total_reward, 2),
            efficiency_score=round(efficiency, 4),
            crowd_control_score=round(crowd_control, 4),
            communication_score=round(communication, 4),
            overall_score=overall,
        )
