import pygame
import random
import numpy as np

pygame.display.set_caption('orbits')
(width, height) = (650, 650)
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

white = (255,255,255)
black = (0,0,0)
blue = (0,0,255)

# Global Properties
outside_box_range = 100
accelerate_state = 1
merge = True
running = True
show_lines = True
(mouseX1, mouseY1) = (0, 0)

line_tick = 0
line_step = 10 

def draw_ngon(x, y, n, scale):
    points = []
    if n >= 3:
        for i in range(0,n):
            points.append(( scale * np.cos(2 * np.pi * i/ n) + x, - scale * np.sin(2 * np.pi * i/ n) + y))
        pygame.draw.polygon(screen, white, points, 1)

class Particle:
    def __init__(self, x, y, mass):
        self.pos = np.array([x, y])
        self.vel = np.array([0, 0])
        self.mass = mass
        self.radius =  1.5 * np.sqrt(self.mass / np.pi)
        
        self.prev_pos = self.pos
        self.sun = False
    
    def update(self):
        self.radius = 1.5 * np.sqrt(self.mass / np.pi) 
        if line_tick == 1:
            self.prev_pos = self.pos
        if self.sun == False:
            self.pos = np.add(self.pos, self.vel)
        if self.radius > 1:
            pygame.draw.circle(screen, white, (self.pos[0], self.pos[1]), self.radius)
        else:
            pygame.draw.circle(screen, white, (self.pos[0], self.pos[1]), 1)
        
particles = []

def create_particle(x, y, mass):
    particle = Particle(x, y, mass)
    particles.append(particle)

def create_particles(number, scale):
    for i in range(number):
        x = random.randint(int(width * scale), int(width - width * scale))
        y = random.randint(int(height * scale), int(height - height * scale))
        mass = random.uniform(.5, 1)
        particle = Particle(x, y, mass)
        max_vel = .3
        dx = random.uniform(-max_vel, max_vel)
        dy = random.uniform(-max_vel, max_vel)
        particle.vel = np.array([dx, dy])
        particles.append(particle)
    
def accelerate(p1, p2, state):
    x = p1.pos[0] - p2.pos[0]
    y = p1.pos[1] - p2.pos[1]
    dist = np.hypot(x, y)
    G = 0 #gravitational constant
    force = 0

    if state == 1:
        G = 1
        if dist >= 1:
            force = G * p1.mass * p2.mass / dist**2 # Newtons gravitation
    elif state == 2:
        G = .04
        force = G * p1.mass * p2.mass / dist
    elif state == 3:
        G = 0.00001
        force = G * p1.mass * p2.mass * dist
    elif state == 4:
        G = 0.01
        force = G * p1.mass * p2.mass * np.sin(dist)

    angle1 = np.arctan2(y, x)
    p1.vel = np.add(p1.vel, -(force/p1.mass) * np.array([np.cos(angle1), np.sin(angle1)]) ) # a = g = GM/d^2

    angle2 = angle1 - np.pi
    p2.vel = np.add(p2.vel, -(force/p2.mass) * np.array([np.cos(angle2), np.sin(angle2)]) )

def check_merge(p1, p2):
    x = p1.pos[0] - p2.pos[0]
    y = p1.pos[1] - p2.pos[1]
    dist = np.hypot(x, y)
    if dist < p1.radius or dist < p2.radius:
        if p1.mass < p2.mass:
            if p2.sun == True or p1.sun == True:
                p2.vel = np.array([0 ,0])
                p2.sun = True
            else:
                p2.vel = (p1.mass * p1.vel + p2.mass * p2.vel)/ (p1.mass + p2.mass) # conservation of momentum
            p2.mass += p1.mass
            particles.remove(p1)
        else:
            if p2.sun == True or p1.sun == True:
                p1.vel = np.array([0 ,0])
                p1.sun = True
            else:
                p1.vel = (p2.mass * p2.vel + p1.mass * p1.vel)/ (p2.mass + p1.mass)
            p1.mass += p2.mass
            particles.remove(p2)
        


class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.brightness = 255
        self.fade_speed = .5

    def update(self):
        self.brightness -= self.fade_speed
        pygame.draw.line(screen, (self.brightness, self.brightness, self.brightness), (self.x1, self.y1), (self.x2, self.y2))
    
lines = []

def create_line(p):
    line = Line(p.prev_pos[0], p.prev_pos[1], p.pos[0], p.pos[1])
    lines.append(line)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.VIDEORESIZE:
            width, height = pygame.display.get_surface().get_size()
        #create a particle with initial velocity when mouse is dragged    
        if event.type == pygame.MOUSEBUTTONDOWN:
            (mouseX1, mouseY1) = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONUP:
            (mouseX2, mouseY2) = pygame.mouse.get_pos()
            particle = Particle(mouseX1, mouseY1, 1)
            dx = mouseX2 - mouseX1
            dy = mouseY2 - mouseY1
            magnitude = np.hypot(dx, dy)
            if magnitude > 0:
                particle.vel = .005 * np.array([dx, dy])
            particles.append(particle)

        if event.type == pygame.KEYDOWN:
            #creates 5 particles
            if event.key == pygame.K_SPACE:
                create_particles(5, 1/4)
            #creates 100 particels all over the screen
            if event.key == pygame.K_g:
                create_particles(100, 0)
                show_lines = False
            #creates a "sun" ,particle with big mass and fixes it to mouse postition
            if event.key == pygame.K_s:
                (mouseX1, mouseY1) = pygame.mouse.get_pos()
                particle = Particle(mouseX1, mouseY1, 25)
                particle.sun = True
                particles.append(particle)
            #resets everything
            if event.key == pygame.K_x:
                particles = []
                lines = []
            #toggles lines/trails
            if event.key == pygame.K_l:
                if show_lines:
                    lines = []
                    show_lines = False
                else:
                    show_lines = True
            
            if event.key == pygame.K_1:
                merge = True
                accelerate_state = 1
            if event.key == pygame.K_2:
                merge = False
                accelerate_state = 2
            if event.key == pygame.K_3:
                merge = False
                accelerate_state = 3
            if event.key == pygame.K_4:
                merge = False
                accelerate_state = 4

            if event.key == pygame.K_m:
                if merge:
                    merge = False
                else:
                    merge = True

    screen.fill(black)

    line_tick +=1
    if line_tick == line_step:
        line_tick = 0

    if show_lines:
        for i, line in enumerate(lines):
            if line.brightness <= 0:
                lines.remove(line)
            else:
                line.update()

    for i, p1 in enumerate(particles):
        if p1.pos[0] < -outside_box_range or p1.pos[0] > width + outside_box_range or p1.pos[1] < -outside_box_range or p1.pos[1] > height + outside_box_range:
            particles.remove(p1)
        p1.update()
        if show_lines:
            if line_tick == 0:
                create_line(p1)
        for p2 in particles[i+1:]:
            accelerate(p1, p2, accelerate_state)
            if merge:
                check_merge(p1, p2)

    draw_ngon(40, 40, len(particles), 20)

    pygame.display.flip()

