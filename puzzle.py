"""
2048 Python wrapped by OpenAI gym
"""
import os

import gym
import gym.spaces
import numpy as np
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

import logic

CELL_SIZE = 50
GRID_PADDING = 10
ELEMENT_SIZE = CELL_SIZE + 2 * GRID_PADDING

MATRIX_SIZE = 4
IMAGE_SIZE = ELEMENT_SIZE * MATRIX_SIZE

FONT = PIL.ImageFont.truetype(os.path.join("font", "varta", "Varta-Bold.ttf"), 30)

BACKGROUND_COLOR_GAME = "#92877d"
BACKGROUND_COLOR_DICT = {
    0: "#9e948a", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
    16: "#f59563", 32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72",
    256: "#edcc61", 512: "#edc850", 1024: "#edc53f", 2048: "#edc22e",
    "super": "#3c3a32"
}

CELL_COLOR_DICT = {
    2: "#776e65", 4: "#776e65", 8: "#f9f6f2", 16: "#f9f6f2",
    32: "#f9f6f2", 64: "#f9f6f2", 128: "#f9f6f2", 256: "#f9f6f2",
    512: "#f9f6f2", 1024: "#f9f6f2", 2048: "#f9f6f2", "super": "#f9f6f2"
}

class Error(Exception):
    """
    Error base class
    """
    pass

class InvalidActionError(Error):
    """
    this error is raised when invalid action are assigned
    """
    def __init__(self, action):
        super(InvalidActionError, self).__init__()
        self.action = action

class Env(gym.core.Env):
    """
    2048 gym env
    """
    def __init__(self, image_save_dir=".images"):
        self.image_save_dir = image_save_dir

        self.episode_num = 0
        self.pre_step_max_tile = 0
        self.step_num = 0
        self._total_step_counter = 0
        self.pre_step_moved = 0

        self.matrix = []

        self.actions = [
            logic.up,
            logic.down,
            logic.left,
            logic.right
        ]

        self.action_space = gym.spaces.Discrete(len(self.actions))
        self.observation_space = gym.spaces.Discrete(MATRIX_SIZE * MATRIX_SIZE)

        self.metadata = {
            "render.modes": ["human"]
        }

    def _reset(self):
        self.step_num = 0
        self.pre_step_max_tile = 0
        self.pre_step_moved = True

        self.episode_num += 1

        self.matrix = logic.new_game(MATRIX_SIZE)

        self.matrix = logic.add_new_tile(self.matrix)
        self.matrix = logic.add_new_tile(self.matrix)

        return np.array(self.matrix).flatten()

    def get_max_tile(self):
        return logic.max_tile(self.matrix)

    def get_reward(self, moved):
        return -0.01 if not self.pre_step_moved and not moved else ((self.get_max_tile() - self.pre_step_max_tile) + 10)

    def _step(self, action):
        is_terminate = False
        done = False

        self.step_num += 1
        self._total_step_counter += 1

        if action <= self.action_space.n - 1:
            self.matrix, moved = self.actions[action](self.matrix)
        else:
            raise InvalidActionError(action)

        if moved:
            self.matrix = logic.add_new_tile(self.matrix)
            is_terminate = logic.game_state(self.matrix)

        reward = self.get_reward(moved)

        self.pre_step_moved = moved
        self.pre_step_max_tile = self.get_max_tile()

        info = {
            "max_tile": self.pre_step_max_tile,
            "moved": self.pre_step_moved
        }

        return np.array(self.matrix).flatten(), reward, is_terminate, info

    def _render(self, mode='human', close=False):
        board_image = draw_board_image(self.matrix)

        draw_explanation(board_image, self.step_num, self.episode_num)

        save_dir = os.path.join(self.image_save_dir)
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)

        board_image.save(os.path.join(self.image_save_dir, str(self._total_step_counter) + ".jpg"))


def draw_board_image(matrix):
    image = PIL.Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE + 100), BACKGROUND_COLOR_GAME)

    draw = PIL.ImageDraw.Draw(image)
    for i in range(MATRIX_SIZE):
        for j in range(MATRIX_SIZE):
            left = i * ELEMENT_SIZE + GRID_PADDING
            top = j * ELEMENT_SIZE + GRID_PADDING
            right = (i + 1) * ELEMENT_SIZE - GRID_PADDING
            bottom = (j + 1) * ELEMENT_SIZE - GRID_PADDING
            draw.rectangle([(left, top), (right, bottom)], fill=BACKGROUND_COLOR_DICT[matrix[i][j] if matrix[i][j] <= 2048 else "super"])
            if matrix[i][j] > 0:
                width, height = draw.textsize(str(matrix[i][j]), font=FONT)
                draw.text(((left + right - width) / 2, (top + bottom - height) / 2), str(matrix[i][j]), fill=CELL_COLOR_DICT[matrix[i][j] if matrix[i][j] <= 2048 else "super"], font=FONT)
    del draw

    return image

def draw_explanation(board_image, step_num, episode_num):
    draw = PIL.ImageDraw.Draw(board_image)

    draw.text((10, IMAGE_SIZE + 10), "step        = " + str(step_num), fill="#eee4da", font=FONT) # to pretify view
    draw.text((10, IMAGE_SIZE + 30), "episode = "     + str(episode_num), fill="#eee4da", font=FONT)

    del draw
