import enum

import logic

MATRIX_SIZE = 4

class Action(enum.Enum):
    UP    = 0
    DOWN  = 1
    LEFT  = 2
    RIGHT = 3

class Error(Exception):
    pass

class InvalidActionError(Error):
    def __init__(self, action):
        self.action = action

class Env():
    def __init__(self):
        pass

    def reset(self):
        self.matrix = logic.new_game(MATRIX_SIZE)
        
        self.matrix = logic.add_new_tile(self.matrix)
        self.matrix = logic.add_new_tile(self.matrix)

        return self.matrix
    
    def step(self, action):
        is_terminate = False
        done         = False

        if action == Action.UP:
            self.matrix, done = logic.up(self.matrix)
        elif action == Action.DOWN:
            self.matrix, done = logic.down(self.matrix)
        elif action == Action.LEFT:
            self.matrix, done = logic.left(self.matrix)
        elif action == Action.RIGHT:
            self.matrix, done = logic.right(self.matrix)
        else:
            raise InvalidActionError(action)

        if done:
            self.matrix = logic.add_new_tile(self.matrix)
            is_terminate = logic.game_state(self.matrix)

        info = {
            "updateable": done 
        }
        return self.matrix, logic.max_title(self.matrix), is_terminate, info


def main():
    def pretty_print(matrix):
        for i in range(len(matrix)):
            print(matrix[i])

    env = Env()

    for i in range(1):
        pretty_print(env.reset())
        
        while True:
            key = input()
            if key == "a":
                action = Action.LEFT
            elif key == "w":
                action = Action.UP
            elif key == "d":
                action = Action.RIGHT
            elif key == "s":
                action = Action.DOWN

            observe, reward, done, info = env.step(action)
            print(info)
            pretty_print(observe)
            if done == True:
                print(reward)
                break

if __name__ == "__main__":
    main()