from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import BehaviorName
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Input, Flatten, Dense
import random
import numpy as np
from collections import deque
from tqdm import tqdm
import pickle

print("Press play' button in your editor")

# This is a non-blocking call that only loads the environment.
env = UnityEnvironment(file_name=None, seed=1, side_channels=[], no_graphics=False)
agent_name = "BallAgent?team=0"

model = tf.keras.models.load_model('models/RollerBall/AdamMse4x8x4.ckpt')
def get_action(state):
        return model.predict(np.array(state))[0] 

def step(env, behavior_name):
    decision_step, terminal_step = env.get_steps(behavior_name=agent_name)
    reward = 0
    done = len(terminal_step.interrupted) > 0
    if done:
        new_state = terminal_step.obs[0]
        reward = terminal_step.reward[0]

    else:
        new_state = decision_step.obs[0]
        reward = decision_step.reward[0]

    return (new_state, reward, done)


env.reset()
while True:
    env.reset()
    current_state, reward, done = step(env, agent_name)
    done = False
    while not done:
        action = np.argmax(get_action(current_state))
        env.set_actions(behavior_name=agent_name, action=np.array(action).reshape(-1,1))
        env.step()
        new_state, reward, done = step(env, agent_name)
        current_state = new_state

        