import enum
import os

import gym
import gym.spaces
import numpy as np
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont



import logic

CELL_SIZE    = 50
GRID_PADDING = 10 
ELEMENT_SIZE = CELL_SIZE + 2 * GRID_PADDING

MATRIX_SIZE  = 4
IMAGE_SIZE   = ELEMENT_SIZE * MATRIX_SIZE 

FONT = PIL.ImageFont.truetype(os.path.join("font", "varta", "Varta-Bold.ttf"), 30)

BACKGROUND_COLOR_GAME = "#92877d"
BACKGROUND_COLOR_DICT = {
    0:"#9e948a",   2:"#eee4da",   4:"#ede0c8",    8:"#f2b179", 
    16:"#f59563",  32:"#f67c5f",  64:"#f65e3b",   128:"#edcf72",  
    256:"#edcc61", 512:"#edc850", 1024:"#edc53f", 2048:"#edc22e",
    "super": "#3c3a32"
}

CELL_COLOR_DICT = { 
    2:"#776e65",   4:"#776e65",    8:"#f9f6f2",    16:"#f9f6f2",
    32:"#f9f6f2",  64:"#f9f6f2",   128:"#f9f6f2",  256:"#f9f6f2",
    512:"#f9f6f2", 1024:"#f9f6f2", 2048:"#f9f6f2", "super": "#f9f6f2"
}

class Error(Exception):
    pass

class InvalidActionError(Error):
    def __init__(self, action):
        self.action = action

class Env(gym.core.Env):
    def __init__(self, image_save_dir=".images"):
        self.image_save_dir = image_save_dir

        self.episode_num        = 0
        self.step_num           = 0
        self.total_step_counter = 0

        self.actions = [
            logic.up,
            logic.down,
            logic.left,
            logic.right
        ]

        self.action_space      = gym.spaces.Discrete(len(self.actions))
        self.observation_space = gym.spaces.Discrete(MATRIX_SIZE * MATRIX_SIZE)

        self.metadata = {
            "render.modes": ["human"]
        }

    def _reset(self):
        self.step_num = 0
        self.max_tile = 0
        self.was_moveable = True

        self.episode_num += 1
        
        self.matrix = logic.new_game(MATRIX_SIZE)
        
        self.matrix = logic.add_new_tile(self.matrix)
        self.matrix = logic.add_new_tile(self.matrix)

        return np.array(self.matrix).flatten()
    
    def _step(self, action):
        is_terminate = False
        done         = False
        
        self.step_num += 1
        self.total_step_counter +=1

        if action <= self.action_space.n - 1:
            self.matrix, done = self.actions[action](self.matrix)
        else:
            raise InvalidActionError(action)

        if done:
            self.matrix = logic.add_new_tile(self.matrix)
            is_terminate = logic.game_state(self.matrix)

        now_max_tile = logic.max_tile(self.matrix)

        reward = -0.01 if self.was_moveable == False and done == False else ((now_max_tile - self.max_tile) + 10)


        self.was_moveable = done
        self.max_tile = now_max_tile

        info = {
            "max_tile": self.max_tile,
            "moveable": self.was_moveable
        }

        return np.array(self.matrix).flatten(), reward, is_terminate, info

    def _render(self, mode='human', close=False):
        image = PIL.Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE + 100), BACKGROUND_COLOR_GAME)

        draw = PIL.ImageDraw.Draw(image)

        for i in range(MATRIX_SIZE):
            for j in range(MATRIX_SIZE):
                x0 = i * ELEMENT_SIZE + GRID_PADDING
                y0 = j * ELEMENT_SIZE + GRID_PADDING
                x1 = (i + 1) * ELEMENT_SIZE - GRID_PADDING
                y1 = (j + 1) * ELEMENT_SIZE - GRID_PADDING
                draw.rectangle([(x0, y0),(x1, y1)], fill=BACKGROUND_COLOR_DICT[self.matrix[i][j] if self.matrix[i][j] <=2048 else "super"])
                if self.matrix[i][j] > 0:

                    width, height = draw_text_size = draw.textsize(str(self.matrix[i][j]), font=FONT)
                    draw.text(((x0+x1-width)/2,(y0+y1-height)/2), str(self.matrix[i][j]), fill=CELL_COLOR_DICT[self.matrix[i][j] if self.matrix[i][j] <=2048 else "super"], font=FONT)



        draw.text((10, IMAGE_SIZE + 10),  "step        = " + str(self.step_num),    fill="#eee4da", font=FONT) # to pretify view
        draw.text((10, IMAGE_SIZE + 30),  "episode = "     + str(self.episode_num), fill="#eee4da", font=FONT)
        del draw

        save_dir = os.path.join(self.image_save_dir)
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)

        image.save(os.path.join(self.image_save_dir, str(self.total_step_counter) + ".jpg"))
