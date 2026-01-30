import pygame as pg
import glm
import random
import time
import subprocess
import requests
import os
import sys
import signal

HOST = "http://127.0.0.1:5001"
REFRESH_SECONDS = 1.0

def calc_gravity(m: float, p1: glm.vec2, p2: glm.vec2) -> glm.vec2:
    dist2 = glm.distance2(p1, p2)
    if dist2 < 0.00001: return 0

    F = m / dist2
    direction = glm.normalize(p1 - p2)

    return F * direction

class Bubble:
    def __init__(self, app, position: glm.vec2, velocity: glm.vec2=None, color: glm.vec3=None) -> None:
        self.app = app
        self.position = position
        self.velocity = velocity or glm.vec2(0)
        self.acceleration = glm.vec2(0)
        self.vote = False
        self.color = color or glm.vec3(255)
        self.target_color = self.color

    def update(self):
        center_range = 15
        self.center = glm.vec2(center_range - center_range * 2 * self.vote, 0)

        self.acceleration += calc_gravity(50000, self.center, self.position)
        for other in app.bubbles.values():
            if other == self: continue
            self.acceleration -= calc_gravity(1000, glm.vec2(other.position), glm.vec2(self.position))
        self.acceleration = glm.clamp(self.acceleration, -20, 20)
        
        self.velocity += self.acceleration * self.app.dt
        self.velocity = glm.clamp(self.velocity, -15.0, 15.0)

        self.position += self.velocity * app.dt

        color_diff = self.target_color - self.color
        if color_diff: self.color += color_diff * app.dt

    def render(self):
        color = glm.clamp(self.color, 0, 255)
        color = (int(self.color.r), int(self.color.y), int(self.color.z))
        pg.draw.circle(self.app.win, color, self.app.center + self.position * app.unit, app.unit)
        pg.draw.circle(self.app.win, (240, 240, 240), self.app.center + self.position * app.unit, app.unit, 2)

class App:
    def __init__(self):
        self.win = pg.display.set_mode((800, 800), pg.RESIZABLE)
        
        self.clock = pg.time.Clock()
        self.dt = 0
        self.timer = 0

        self.unit = 25
        self.win_size = glm.vec2(800, 800)
        self.center = self.win_size / 2
        # self.bubbles = {i : Bubble(self, glm.vec2(random.randrange(-5, 5), random.randrange(-5, 5)), glm.vec2(0, 0), glm.vec3(235 + random.randrange(-20, 20), 20 + random.randrange(-20, 20), 20 + random.randrange(-20, 20))) for i in range(20)}
        self.bubbles = {}

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
            elif event.type == pg.MOUSEWHEEL:
                self.unit += event.y * 2
                self.unit = glm.clamp(self.unit, 2, 100)
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    for bubble in self.bubbles.values():
                        bubble.vote = not bubble.vote
                        if bubble.vote:
                            bubble.target_color = glm.vec3(20 + random.randrange(-20, 20), 235 + random.randrange(-20, 20), 20 + random.randrange(-20, 20))
                        else:
                            bubble.target_color = glm.vec3(235 + random.randrange(-20, 20), 20 + random.randrange(-20, 20), 20 + random.randrange(-20, 20))


    def render(self):
        self.win.fill((15, 15, 15, 255))

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

            bubble = self.bubbles[ip]

            if bubble.vote != vote:
                if vote:
                    bubble.target_color = glm.vec3(20 + random.randrange(-20, 20), 235 + random.randrange(-20, 20), 20 + random.randrange(-20, 20))
                else:
                    bubble.target_color = glm.vec3(235 + random.randrange(-20, 20), 20 + random.randrange(-20, 20), 20 + random.randrange(-20, 20))
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