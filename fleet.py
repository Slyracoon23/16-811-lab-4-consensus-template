"""The protocol as actual ROS 2 nodes, one per robot, talking over real topics.

`evaluate.py` integrates xdot = -Lx in NumPy, and that is the right place to first check that your
Laplacian is correct — it is deterministic and it is fast. But it also quietly assumes every robot
reads every neighbour instantly and exactly, which is the assumption a real fleet breaks.

Here each robot is an `rclpy` node. It publishes its own value and subscribes to its neighbours',
and the update runs on a timer against whatever has actually arrived. Nothing is shared in memory;
the graph is realised as topics. The convergence rate should still be lambda_2 — and where it is
not, the reason is in the transport rather than in the algebra, which is the interesting half.

Run it:
    python run_fleet.py --graph ring --robots 8

Watch it, with Foxglove Studio connected through the bridge:
    ros2 run foxglove_bridge foxglove_bridge      # then open ws://localhost:8765
"""

from __future__ import annotations

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class Robot(Node):
    """One agent. Publishes its value; averages in whatever its neighbours last said."""

    def __init__(self, index: int, neighbours: list[int], value: float, *, gain: float, period: float):
        super().__init__(f"robot_{index}")
        self.index, self.value, self.gain = index, float(value), gain
        self.heard: dict[int, float] = {}
        self.history: list[float] = []

        self.publisher = self.create_publisher(Float64, f"/robot_{index}/value", 10)
        for other in neighbours:
            self.create_subscription(Float64, f"/robot_{other}/value", self._make_listener(other), 10)
        self.create_timer(period, self.step)

    def _make_listener(self, other: int):
        def listen(message: Float64) -> None:
            self.heard[other] = message.data

        return listen

    def step(self) -> None:
        """One Euler step of xdot = -Lx, using only what has arrived.

        The sum is over neighbours we have actually heard from. A robot that has heard from nobody
        does not move — which is the honest behaviour, and is why the first few steps of a real
        fleet do not match the prediction.
        """
        disagreement = sum(self.value - other for other in self.heard.values())
        self.value -= self.gain * disagreement
        self.history.append(self.value)
        self.publisher.publish(Float64(data=self.value))


def run(adjacency: np.ndarray, *, steps: int = 400, gain: float = 0.05, period: float = 0.01, seed: int = 0):
    """Spin a fleet on this graph and return the value history, shape (robots, steps)."""
    adjacency = np.asarray(adjacency)
    rng = np.random.default_rng(seed)
    start = rng.normal(size=len(adjacency))
    start -= start.mean()

    rclpy.init()
    executor = rclpy.executors.MultiThreadedExecutor()
    robots = []
    try:
        for index in range(len(adjacency)):
            neighbours = np.flatnonzero(adjacency[index] > 0).tolist()
            robot = Robot(index, neighbours, start[index], gain=gain, period=period)
            robots.append(robot)
            executor.add_node(robot)

        deadline = steps * period * 1.5
        elapsed = 0.0
        while elapsed < deadline and min(len(r.history) for r in robots) < steps:
            executor.spin_once(timeout_sec=period)
            elapsed += period

        length = min(len(r.history) for r in robots)
        return np.array([r.history[:length] for r in robots])
    finally:
        for robot in robots:
            robot.destroy_node()
        rclpy.shutdown()
