import gymnasium as gym

from typing import Dict, Callable, Any
from enum import Enum
from environments.EnvironmentBase import EnvironmentBase

class Move(Enum):
    LEFT = 0
    DOWN = 1
    RIGHT = 2
    UP = 3
    
class FrozenLake(EnvironmentBase):
    def __init__(self, env = gym.make("FrozenLake-v1",
                      render_mode="ansi", 
                      desc=None,
                      map_name="4x4",
                      is_slippery=True,
                      success_rate=1.0/3.0,
                      reward_schedule=(1, 0, 0))):
        super().__init__(env)
        
    @property
    def ACTION_MAP(self) -> Dict[str, Callable]:
        return {
            "move_left": self.move_left,
            "move_right": self.move_right,
            "move_up": self.move_up,
            "move_down": self.move_down
        }

    def get_state_description(self, player_pos: int | None = None) -> str:
        """
        Alternative implementation that rebuilds the grid from desc.
        This is used too depict the current player position in the FrozenLake environment for an LLM.

        Args:
            env: The FrozenLake gymnasium environment

        Returns:
            str: Modified environment description with player position marked
        """
        if player_pos is None:
            player_pos = self.env.unwrapped.s
        desc = self.env.unwrapped.desc
        nrow, ncol = desc.shape

        row = player_pos // ncol
        col = player_pos % ncol

        result = []
        for r in range(nrow):
            line = ""
            for c in range(ncol):
                cell = desc[r][c].decode('utf-8') if isinstance(desc[r][c], bytes) else desc[r][c]
                if r == row and c == col:
                    line += f"[{cell}]"
                else:
                    line += f" {cell} "
            result.append(line)

        return '\n'.join(result)
    
    def move_left(self):
        return self.execute_action(Move.LEFT)
    def move_right(self):
        return self.execute_action(Move.RIGHT)
    def move_up(self):
        return self.execute_action(Move.UP)
    def move_down(self):
        return self.execute_action(Move.DOWN)
    
    def execute_action(self, action: Move) -> Dict[str, Any]:
        observation, reward, isTerminated, truncated, info = self.env.step(action.value)
        state = self.get_state_description(player_pos=observation)
        answer = {
            "state": state,
            "reward": reward,
            "isTerminated": isTerminated
        }
        return answer


assert issubclass(FrozenLake, EnvironmentBase)