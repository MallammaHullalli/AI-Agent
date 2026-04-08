import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, jsonify, request
from env import BusStopEnv
from agent import BaselineAgent, AgentGrader

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), "templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "static"))

_env = None
_agent = BaselineAgent()
_grader = AgentGrader()


def get_env():
    global _env
    if _env is None:
        _env = BusStopEnv(difficulty="medium")
        _env.reset()
    return _env


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/reset", methods=["POST"])
def api_reset():
    global _env
    difficulty = request.json.get("difficulty", "medium")
    _env = BusStopEnv(difficulty=difficulty)
    state = _env.reset()
    return jsonify({"state": state.to_dict(), "step": 0, "done": False, "reward": 0})


@app.route("/api/state", methods=["GET"])
def api_state():
    return jsonify(get_env().state().to_dict())


@app.route("/api/step", methods=["POST"])
def api_step():
    env = get_env()
    action = request.json.get("action", "no_action")
    result = env.step(action)
    report = _grader.grade(env.history)
    return jsonify({
        "state": result.state.to_dict(),
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
        "score": report.overall_score,
        "step": result.info["step"],
    })


@app.route("/api/auto_step", methods=["POST"])
def api_auto_step():
    env = get_env()
    action = _agent.act(env.state())
    result = env.step(action)
    report = _grader.grade(env.history)
    return jsonify({
        "state": result.state.to_dict(),
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
        "score": report.overall_score,
        "step": result.info["step"],
        "action": action,
    })


@app.route("/api/grade", methods=["GET"])
def api_grade():
    env = get_env()
    report = _grader.grade(env.history)
    return jsonify({
        "overall_score": report.overall_score,
        "efficiency_score": report.efficiency_score,
        "crowd_control_score": report.crowd_control_score,
        "communication_score": report.communication_score,
        "total_reward": report.total_reward,
    })


if __name__ == "__main__":
    app.run(debug=False, port=5000)
