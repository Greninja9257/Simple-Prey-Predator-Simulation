import random
import time
import pygame
import math
import matplotlib.pyplot as plt

import tkinter as tk

root = tk.Tk()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

print(screen_width)
print(screen_height)

root.mainloop()

# Define the prey and predator classes
class Prey:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 150
        self.last_reproduce = time.time()
        self.alive = True
        self.vision = 80
        self.speed = random.randint(10, 15)
        self.age = 0
        self.size = 3  # Smaller size for prey
        
    def move(self, predator_list):
        # Some movement
        closest_predator = None
        min_distance = float('inf')
        for predator in predator_list:
            distance = math.sqrt((self.x - predator.x)**2 + (self.y - predator.y)**2)
            if distance < min_distance:
                min_distance = distance
                closest_predator = predator
        
        if closest_predator and min_distance < self.vision:
            # Move away from the closest predator
            dx = self.x - closest_predator.x
            dy = self.y - closest_predator.y
            self.x += max(6, self.speed - self.age // 11) * dx / min_distance
            self.y += max(6, self.speed - self.age // 11) * dy / min_distance
        else:
            # Move randomly
            self.x += random.randint(-max(6, self.speed - self.age // 11), max(5, self.speed - self.age // 10))
            self.y += random.randint(-max(6, self.speed - self.age // 11), max(5, self.speed - self.age // 10))
        
        # Wrap around the screen
        self.x = (self.x + screen_width) % screen_width
        self.y = (self.y + screen_height) % screen_height
        
        self.age += 1
        
    def reproduce(self, prey_list):
        if time.time() - self.last_reproduce > random.randint(4, 7):
            # Create a new prey
            new_prey = Prey(self.x, self.y)
            prey_list.append(new_prey)
            self.last_reproduce = time.time()
            
    def die(self):
        self.alive = False
        # Apply penalty for dying
        
class Predator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 150
        self.last_reproduce = time.time()
        self.alive = True
        self.vision = 200
        self.speed = random.randint(10, 15)
        self.age = 0
        self.size = 6  # Smaller size for predators
        
    def move(self, prey_list, predator_list):
        # Some more movement
        closest_prey = None
        min_distance = float('inf')
        for prey in prey_list:
            if prey.alive:
                distance = math.sqrt((self.x - prey.x)**2 + (self.y - prey.y)**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_prey = prey
        
        if closest_prey and min_distance < self.vision:
            # Move towards the closest prey
            dx = closest_prey.x - self.x
            dy = closest_prey.y - self.y
            self.x += max(5, self.speed - self.age // 11) * dx / min_distance
            self.y += max(5, self.speed - self.age // 11) * dy / min_distance
        else:
            # Move randomly
            self.x += random.randint(-max(5, self.speed - self.age // 11), max(5, self.speed - self.age // 10))
            self.y += random.randint(-max(5, self.speed - self.age // 11), max(5, self.speed - self.age // 10))
        
        # Wrap around the screen
        self.x = (self.x + screen_width) % screen_width
        self.y = (self.y + screen_height) % screen_height
        
        # Check for collisions with other predators
        for other_predator in predator_list:
            if other_predator != self and abs(other_predator.x - self.x) < 10 and abs(other_predator.y - self.y) < 10:
                self.energy -= 5  # Apply penalty for touching another predator
        
        self.age += 1
        
    def eat(self, prey):
        self.energy += prey.energy
        prey.die()
        
    def reproduce(self, predator_list):
        if self.energy >= 200:
            # Create a new predator
            new_predator = Predator(self.x, self.y)
            predator_list.append(new_predator)
            self.energy = 100
            
    def lose_energy(self):
        self.energy -= 1
        if self.energy <= 0:
            self.die()
            
    def die(self):
        self.alive = False
        # Apply penalty for dying
        
# Initialize the simulation
num_prey = 20
num_predators = 4
prey_list = [Prey(random.randint(0, screen_width), random.randint(0, screen_height)) for _ in range(num_prey)]
predator_list = [Predator(random.randint(0, screen_width), random.randint(0, screen_height)) for _ in range(num_predators)]

# Initialize Pygame
pygame.init()
screen_width, screen_height = 1000, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Prey-Predator Simulation")
clock = pygame.time.Clock()

# Zoom level
zoom_level = 1.0

# Lists to store data for plotting
prey_counts = []
predator_counts = []
kill_counts = []

# Run the simulation
running = True
while running:
    # Move and reproduce prey
    for prey in prey_list:
        prey.move(predator_list)
        prey.reproduce(prey_list)
        
    # Move, eat, reproduce, and lose energy for predators
    kills = 0
    for predator in predator_list:
        predator.move(prey_list, predator_list)
        for prey in prey_list:
            if prey.alive and abs(prey.x - predator.x) < 5 and abs(prey.y - predator.y) < 5:
                predator.eat(prey)
                kills += 1
        predator.reproduce(predator_list)
        predator.lose_energy()
        
    # Remove dead prey and predators
    prey_list = [prey for prey in prey_list if prey.alive]
    predator_list = [predator for predator in predator_list if predator.alive]
    
    # Randomly spawn prey if all died off
    if not prey_list:
        num_prey = 20
        prey_list = [Prey(random.randint(0, screen_width), random.randint(0, screen_height)) for _ in range(num_prey)]
    
    # Randomly spawn predators if all died off
    if not predator_list:
        num_predators = 4
        predator_list = [Predator(random.randint(0, screen_width), random.randint(0, screen_height)) for _ in range(num_predators)]
    
    # Limit the total number of creatures to 600
    total_creatures = len(prey_list) + len(predator_list)
    if total_creatures > 600:
        prey_to_remove = random.sample(prey_list, total_creatures - 600)
        predator_to_remove = random.sample(predator_list, total_creatures - 600 - len(prey_to_remove))
        prey_list = [prey for prey in prey_list if prey not in prey_to_remove]
        predator_list = [predator for predator in predator_list if predator not in predator_to_remove]
    
    # Clear the screen
    screen.fill((255, 255, 255))
    
    # Draw the prey and predators
    for prey in prey_list:
        pygame.draw.circle(screen, (0, 255, 0), (int(prey.x * zoom_level), int(prey.y * zoom_level)), int(prey.size * zoom_level))
    for predator in predator_list:
        pygame.draw.circle(screen, (255, 0, 0), (int(predator.x * zoom_level), int(predator.y * zoom_level)), int(predator.size * zoom_level))
    
    # Update the display
    pygame.display.flip()
    
    # Wait for a short time
    clock.tick(40)  # Limit the frame rate to 60 FPS
    
    # Check for quit event and zoom in/out
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                zoom_level *= 1.1  # Zoom in
            elif event.key == pygame.K_MINUS:
                zoom_level /= 1.1  # Zoom out
    
    # Store data for plotting
    prey_counts.append(len(prey_list))
    predator_counts.append(len(predator_list))
    kill_counts.append(kills)

# Quit Pygame
pygame.quit()

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(prey_counts, label='Number of Prey')
plt.plot(predator_counts, label='Number of Predators')
plt.plot(kill_counts, label='Number of Kills')
plt.xlabel('Time')
plt.ylabel('Count')
plt.title('Prey-Predator Simulation')
plt.legend()
plt.show()