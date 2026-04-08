"""
Reproducible evaluation script for Smart Bus Stop environment.
Usage: python evaluate.py --difficulty easy|medium|hard --episodes 10
"""
import argparse
import random
from env import BusStopEnv
from agent import BaselineAgent, AgentGrader

def run_episode(env: BusStopEnv, agent: BaselineAgent) -> float:
    state = env.reset()
    done = False
    while not done:
        action = agent.act(state)
        result = env.step(action)
        state = result.state
        done = result.done
    grader = AgentGrader()
    report = grader.grade(env.history)
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--difficulty", default="medium", choices=["easy", "medium", "hard"])
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    env = BusStopEnv(difficulty=args.difficulty)
    agent = BaselineAgent()
    grader = AgentGrader()

    scores = []
    for ep in range(1, args.episodes + 1):
        state = env.reset()
        done = False
        while not done:
            action = agent.act(state)
            result = env.step(action)
            state = result.state
            done = result.done
        report = grader.grade(env.history)
        scores.append(report.overall_score)
        print(f"Episode {ep:>3} | Score: {report.overall_score:.3f} | Reward: {report.total_reward:.1f}")

    avg = sum(scores) / len(scores)
    print(f"\n{'='*45}")
    print(f"Difficulty : {args.difficulty.upper()}")
    print(f"Episodes   : {args.episodes}")
    print(f"Avg Score  : {avg:.4f}")
    print(f"{'='*45}")

if __name__ == "__main__":
    main()
