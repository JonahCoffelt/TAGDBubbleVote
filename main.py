import pygame as pg
import glm
import random
import time
import subprocess
import requests
import os
import sys
import signal

HOST = "http://127.0.0.1:5000"
REFRESH_SECONDS = 1.0

class Bubble:
    def __init__(self, app, position: glm.vec2, velocity: glm.vec2=glm.vec2(0, 0)) -> None:
        self.app = app
        self.position = position
        self.velocity = velocity
        self.acceleration = glm.vec2(0)
        self.mass = 10
        self.vote = False

    def update(self):
        center_range = 15
        self.center = glm.vec2(center_range - center_range * 2 * self.vote, 0)
        dist2 = glm.distance2(self.center, self.position)
        if dist2 == 0: dist2 = 0.001

        F = self.mass * 50000 / dist2
        direction = glm.normalize(self.center - self.position)
        self.acceleration = direction * F / self.mass
        self.acceleration = glm.clamp(self.acceleration, -20, 20)
        
        self.velocity += self.acceleration * self.app.dt
        self.velocity = glm.clamp(self.velocity, -15.0, 15.0)

        self.position += self.velocity * app.dt

    def render(self):
        pg.draw.circle(self.app.win, (0, 0, 255), self.app.center + self.position * app.unit, app.unit)

class App:
    def __init__(self):
        self.win = pg.display.set_mode((800, 800), pg.RESIZABLE)
        
        self.clock = pg.time.Clock()
        self.dt = 0
        self.timer = 0

        self.unit = 25
        self.win_size = glm.vec2(800, 800)
        self.center = self.win_size / 2
        self.bubbles = {"1.1.1.1" : Bubble(self, glm.vec2(1, 0), glm.vec2(1, 10))}
        self.votes = {}

    def update(self):
        self.dt = self.clock.tick(60) / 1000
        self.timer += self.dt

        if self.timer > 1:
            self.update_votes()
            self.timer = 0

        for bubble in self.bubbles.values():
            bubble.update()

        self.events = pg.event.get()
        for event in self.events:
            if event.type == pg.QUIT:
                self.running = False
                pg.quit()
            elif event.type == pg.VIDEORESIZE:
                width, height = event.size
                self.win_size.x = width
                self.win_size.y = height
                self.center = self.win_size / 2

    def render(self):
        self.win.fill((0, 0, 0, 255))

        for bubble in self.bubbles.values():
            bubble.render()

        pg.display.flip()

    def update_votes(self):
        response = requests.get(f"{HOST}/votes", timeout=1)
        votes = response.json()

        print("Current Votes\n" + "-" * 20)
        print(votes)

        for (ip, vote) in votes.items():
            if ip not in self.bubbles:
                bubble = Bubble(self, glm.vec2(random.randrange(-5, 5), random.randrange(-5, 5)), glm.vec2(1, 0))
                self.bubbles[ip] = bubble
            self.bubbles[ip].vote = vote

    def start(self):
        self.running = True
        while self.running:
            self.render()
            self.update()

python_exec = sys.executable
server = subprocess.Popen([python_exec, "host.py"])

app = App()
app.start()

server.terminate()
server.wait()