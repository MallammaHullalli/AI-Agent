---
title: Smart Bus Stop Crowd Manager
emoji: 🚌
colorFrom: green
colorTo: yellow
sdk: docker
pinned: false
---

# Smart Bus Stop Crowd Manager

A reinforcement learning environment (OpenEnv spec) for managing crowd dynamics at an urban bus stop, with a real-time web dashboard inspired by the Namma BMTC app.

## Environment Overview

The agent observes a bus stop and decides each step whether to:
- **send_bus** — dispatch an extra bus immediately
- **delay_bus** — hold the next scheduled bus
- **no_action** — monitor and wait

## Setup

```bash
pip install -r requirements.txt
python web/app.py
# Open http://localhost:7860
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
    result = env.step("send_bus")
    state, reward, done = result.state, result.reward, result.done
```
