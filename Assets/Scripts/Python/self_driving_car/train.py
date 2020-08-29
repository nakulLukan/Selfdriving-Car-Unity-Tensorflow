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

REPLAY_MEMORY_SIZE = 10000
MIN_OBSERVATIONS = 500
BATCH_SIZE = 64
EPISODES = 100
UPDATE_TARGET_EVERY = 5

LEARNING_RATE = 0.01
DSICOUNT = 0.9

ACTION_SPACE_SIZE = 3
OBSERVATION_SPACE_SIZE = 3

class DQAgent():

    def __init__(self):
        self.replay = deque(maxlen= REPLAY_MEMORY_SIZE)
        self.model = self.create_model()

        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())
        self.update_target_step = 0

    def update_replay(self, observation):
        self.replay.append(observation)

    def create_model(self):
        model = Sequential()

        model.add(Input(OBSERVATION_SPACE_SIZE,))
        model.add(Dense(16, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(ACTION_SPACE_SIZE, activation='linear'))

        model.compile(loss='mse', optimizer=Adam(LEARNING_RATE), metrics=['accuracy'])
        return model
    
    def save_model(self, path):
        self.model.save(path)

    def train(self, terminal_step):
        if(len(self.replay) < MIN_OBSERVATIONS):
            return
        
        minibatch = random.sample(self.replay, BATCH_SIZE)
        current_states = np.array([transition[0] for transition in minibatch], dtype=np.float32).reshape(-1,OBSERVATION_SPACE_SIZE)
        current_q = self.model.predict(current_states)
        
        new_states = np.array([transition[3] for transition in minibatch], dtype=np.float32).reshape(-1,OBSERVATION_SPACE_SIZE)
        future_q = self.target_model.predict(new_states)
        X = []
        y = []
        for index, (current_state, action, reward, new_stat, done) in enumerate(minibatch):
            if not done:
                max_future_q = np.max(future_q[index])
                new_q = reward + DSICOUNT * max_future_q
            else:
                new_q = reward
            
            current_qs = current_q[index]
            current_qs[action] = new_q

            X.append(current_state)
            y.append(current_qs)

        
        self.model.fit(np.array(X).reshape(-1,OBSERVATION_SPACE_SIZE),np.array(y), batch_size=BATCH_SIZE, verbose=0, shuffle=False)
        if terminal_step:
            self.update_target_step +=1

        if self.update_target_step >= UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.update_target_step = 0

    def get_action(self, state):
        return self.model.predict(np.array(state))[0]

print("Press play' button in your editor")

# This is a non-blocking call that only loads the environment.
env = UnityEnvironment(file_name=None, seed=1, side_channels=[], no_graphics=False)
agent_name = "CarAgent?team=0"

def step(env, behavior_name):
    decision_step, terminal_step = env.get_steps(behavior_name=agent_name)
    done = len(terminal_step.interrupted) > 0
    if done:
        new_state = terminal_step.obs[0]
    else:
        new_state = decision_step.obs[0]
    reward = 0
    if done:
        reward = terminal_step.reward[0]
    else:
        reward = decision_step.reward[0]
    return (new_state, reward, done)

dqn = DQAgent()
statistics =[]

for episode in tqdm(range(0,EPISODES), ascii=True, unit='episode'):
    env.reset()
    current_state, reward, done = step(env, agent_name)
    done = False
    episode_rewards = []
    while not done:
        if random.randint(1,100) > 98:
            action = random.randint(0,ACTION_SPACE_SIZE-1)
        else:
            action = np.argmax(dqn.get_action(current_state))
        env.set_actions(behavior_name=agent_name, action=np.array(action).reshape(-1,1))
        env.step()
        new_state, reward, done = step(env, agent_name)
        dqn.update_replay((current_state, action, reward, new_state, done))
        dqn.train(done)
        current_state = new_state
        episode_rewards.append(reward)


    episode_stats = {"ep": episode, "avg": sum(episode_rewards)/len(episode_rewards), "min":min(episode_rewards), "max": max(episode_rewards)}
    statistics.append(episode_stats)
    if not episode % 10 and episode != 0:
        dqn.save_model("models/SelfDrivingCar/AdamMse4x8x4.ckpt")
        pickle_out = open('models/SelfDrivingCar/Statistics.lr', 'wb')
        pickle.dump(statistics, pickle_out)
        pickle_out.close()
        print(f"episode: {episode_stats['ep']} avg: {episode_stats['avg']} min: {episode_stats['min']} max: {episode_stats['max']} ")
