# 2048-python-gym

## About
Based on the popular game [2048](https://github.com/gabrielecirulli/2048) by Gabriele Cirulli, here is Python version wrapped by [OpenAI gym](https://github.com/openai/gym).

## Dependencies
- gym
- numpy
- pillow

## Example
```
import puzzle

env = puzzle.Env("your/image/save/dir")
env.reset()
env.render()
```
## If you want to override
```
import puzzle

class Your2048Env(puzzle.Env):
    def get_reward(self, moved):
        ...
```

### available class attribute
- episode_num
- pre_step_max_tile
- step_num
- pre_step_moved
- matrix

### available method
- get_max_tile()

default reward are below
```
-0.01 if not self.pre_step_moved and not moved else ((self.get_max_tile() - self.pre_step_max_tile) + 10)
```

## Contributors:
- [yangshun](https://github.com/yangshun)
- [Tay Yang Shun](http://github.com/yangshun)
- [Emmanuel Goh](http://github.com/emman27)
- [google](https://github.com/google)