# Smart Bus Stop Crowd Manager

A reinforcement learning environment (OpenEnv spec) for managing crowd dynamics at an urban bus stop, with a real-time web dashboard inspired by the Namma BMTC app.

---

## Environment Overview

The agent observes a bus stop and decides each step whether to:
- **send_bus** — dispatch an extra bus immediately
- **delay_bus** — hold the next scheduled bus
- **no_action** — monitor and wait

The goal is to minimize overcrowding and waiting times while managing dispatch costs and keeping passengers informed.

---

## State Space

| Field | Type | Description |
|---|---|---|
| crowd_size | int | Passengers currently waiting |
| avg_waiting_time | float | Average wait in minutes |
| bus_arrival_eta | float | Minutes until next bus |
| passenger_inflow_rate | float | New passengers per minute |
| last_notification | str | Latest passenger message |

## Action Space

`send_bus` · `delay_bus` · `no_action`

## Reward Design

- +0.5 per passenger boarded (send_bus)
- −dispatch_cost for sending extra bus
- −3.0 for delaying a bus
- −(crowd−40)×0.3 overcrowding penalty
- −(wait−10)×0.5 long wait penalty
- +2.0 good state bonus (crowd<20, wait<5)
- +0.5 notification reward

## Difficulty Levels

| Level | Steps | Inflow | Traffic Delay | Bus Capacity |
|---|---|---|---|---|
| Easy | 50 | 1–3/min | 0% | 40 |
| Medium | 75 | 1–6/min | 10% | 35 |
| Hard | 100 | 2–10/min | 25% | 30 |

---

## Setup

```bash
pip install -r requirements.txt

# Run web app
python web/app.py
# Open http://localhost:5000

# Run evaluation benchmark
python evaluate.py --difficulty medium --episodes 10
```

## Docker

```bash
docker build -t smart-bus-stop .
docker run -p 7860:7860 smart-bus-stop
```

## OpenEnv API

```python
from env import BusStopEnv

env = BusStopEnv(difficulty="medium")
state = env.reset()

done = False
while not done:
    action = "send_bus"  # or your agent's choice
    result = env.step(action)
    state, reward, done = result.state, result.reward, result.done
```

## Grading

```python
from agent import AgentGrader
grader = AgentGrader()
report = grader.grade(env.history)
print(report)  # Overall Score: 0.742
```

Score is 0.0–1.0 weighted: 40% efficiency + 40% crowd control + 20% communication.

---

## Assumptions

- One bus stop, single route
- Bus capacity is fixed per difficulty
- Passenger inflow follows a random walk
- Notifications are always generated (communication score = 1.0 for active agents)
- Episode ends after max_steps regardless of state
