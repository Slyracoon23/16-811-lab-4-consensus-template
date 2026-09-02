"""A real fleet, when you are ready for one.

Deliberately fetches nothing. Everything here should first be proved on `synthetic.py`, where
lambda_2 is known in closed form — so the first run needs no simulator at all.

ROS 2 Jazzy:   https://docs.ros.org/en/jazzy/index.html
Gazebo:        https://gazebosim.org/
ROS2swarm:     https://github.com/ROS2swarm/ROS2swarm   (TurtleBot3 and Jackal swarm behaviours)

None of them is in the image on purpose. A ROS 2 desktop image is several gigabytes and the
mathematics you are writing needs none of it — the graph is a matrix. Move to ROS 2 at step 6,
when the question becomes whether the rate survives real transport delay.
"""

from __future__ import annotations

if __name__ == "__main__":
    print(__doc__)
