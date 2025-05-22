import pygame
import time
import random
import math
import sys
import json
import requests
import threading
from queue import Queue

# Ollama dialogue generator class
class DialogueGenerator:
    def __init__(self, model=None):
        self.predator_anger_levels = {"Eagle": 1, "Mongoose": 1, "Hawk": 1}
        self.running = True
        
        # No dialogue caches needed
    
# No need for Ollama connection check
    def _update_anger_level(self, predator_type, action=None):
        """Update predator anger level based on action"""
        if predator_type in self.predator_anger_levels:
            if action == "about to strike" or action == "diving to attack":
                # Increase anger more for aggressive actions
                increase = 2
            else:
                increase = 1
                
            self.predator_anger_levels[predator_type] = min(self.predator_anger_levels[predator_type] + increase, 4)
    
    def generate_predator_dialogue(self, predator_type, predator_action):
        """Update predator anger level but don't generate dialogue"""
        # Update anger level based on action
        self._update_anger_level(predator_type, predator_action)
        # Return None to indicate no dialogue
        return None
    
    def generate_snake_response(self, predator_type):
        """Update predator anger level but don't generate dialogue"""
        # Increase anger level of the predator when snake taunts
        self._update_anger_level(predator_type, "taunted")
        # Return None to indicate no dialogue
        return None
    
    def shutdown(self):
        """Clean up resources"""
        self.running = False

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
DARK_GREEN = (0, 100, 0)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
GRAY = (100, 100, 100)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)
YELLOW = (255, 255, 0)
LIME = (50, 205, 50)
TEAL = (0, 128, 128)
BROWN = (139, 69, 19)
LAVENDER = (230, 230, 250)
BROWN = (165, 42, 42)
NAVY = (0, 0, 128)
CORAL = (255, 127, 80)

# Color schemes for snake
COLOR_SCHEMES = {
    "Classic": {
        "body": GREEN,
        "head": DARK_GREEN,
        "food": RED,
        "special_food": GOLD,
        "background": BLACK
    },
    "Ocean": {
        "body": BLUE,
        "head": NAVY,
        "food": CORAL,
        "special_food": CYAN,
        "background": (0, 20, 40)  # Dark blue
    },
    "Fire": {
        "body": ORANGE,
        "head": RED,
        "food": YELLOW,
        "special_food": WHITE,
        "background": (40, 0, 0)  # Dark red
    },
    "Forest": {
        "body": LIME,
        "head": DARK_GREEN,
        "food": BROWN,
        "special_food": ORANGE,
        "background": (20, 40, 20)  # Dark green
    },
    "Candy": {
        "body": PINK,
        "head": PURPLE,
        "food": CYAN,
        "special_food": YELLOW,
        "background": LAVENDER
    },
    "Monochrome": {
        "body": WHITE,
        "head": GRAY,
        "food": WHITE,
        "special_food": WHITE,
        "background": BLACK
    }
}

# Default color scheme
CURRENT_SCHEME = "Classic"

# Set display dimensions
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600

# Track fullscreen state
FULLSCREEN = False
SCALE_FACTOR_X = 1.0
SCALE_FACTOR_Y = 1.0
SCREEN_WIDTH = DISPLAY_WIDTH
SCREEN_HEIGHT = DISPLAY_HEIGHT

# Create display with caption and icon
display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Super Snake Game')

# Try to load and set an icon
try:
    icon = pygame.Surface((32, 32))
    icon.fill(GREEN)
    pygame.draw.rect(icon, DARK_GREEN, (8, 8, 16, 16))
    pygame.display.set_icon(icon)
except:
    pass  # Skip if icon setting fails

# Set game clock
clock = pygame.time.Clock()

# Set snake block size and initial speed
SNAKE_BLOCK = 20
INITIAL_SPEED = 8  # Reduced initial speed
MAX_SPEED = 25
MAX_BOOST_CHARGE = 5  # Maximum boost charge level

# Set font styles
try:
    title_font = pygame.font.SysFont("arial", 60, bold=True)
    font_style = pygame.font.SysFont("arial", 25)
    score_font = pygame.font.SysFont("arial", 35)
    button_font = pygame.font.SysFont("arial", 30, bold=True)
except:
    # Fallback to default font if specific fonts not available
    title_font = pygame.font.Font(None, 60)
    font_style = pygame.font.Font(None, 25)
    score_font = pygame.font.Font(None, 35)
    button_font = pygame.font.Font(None, 30)

# Try to load sound effects
try:
    eat_sound = pygame.mixer.Sound("eat.wav")
    game_over_sound = pygame.mixer.Sound("game_over.wav")
    # Set default volume
    eat_sound.set_volume(0.5)
    game_over_sound.set_volume(0.5)
except:
    eat_sound = None
    game_over_sound = None

# Game states
class GameState:
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    PAUSED = 3

# Food class
class Food:
    def __init__(self, snake_positions=None):
        self.regenerate(snake_positions)
        self.color = COLOR_SCHEMES[CURRENT_SCHEME]["food"]
        self.special = False
        self.special_timer = 0
        self.pulse_value = 0
        self.pulse_direction = 1
    
    def regenerate(self, snake_positions=None):
        if snake_positions is None:
            snake_positions = []
        
        # Generate position not occupied by snake
        while True:
            self.x = round(random.randrange(0, DISPLAY_WIDTH - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
            self.y = round(random.randrange(0, DISPLAY_HEIGHT - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
            
            # Check if position is not occupied by snake
            position_valid = True
            for pos in snake_positions:
                if pos[0] == self.x and pos[1] == self.y:
                    position_valid = False
                    break
            
            if position_valid:
                break
        
        # 10% chance for special food
        self.special = random.random() < 0.1
        if self.special:
            self.color = COLOR_SCHEMES[CURRENT_SCHEME]["special_food"]
            self.special_timer = 150  # Special food disappears after 150 frames
    
    def update(self):
        if self.special:
            self.special_timer -= 1
            
            # Pulse effect for special food
            self.pulse_value += 0.1 * self.pulse_direction
            if self.pulse_value >= 1.0:
                self.pulse_direction = -1
            elif self.pulse_value <= 0.0:
                self.pulse_direction = 1
            
            # Calculate pulsing color
            pulse_intensity = 0.5 + 0.5 * math.sin(self.pulse_value * math.pi)
            r = int(255 * pulse_intensity)
            g = int(215 * pulse_intensity)
            b = 0
            self.color = (r, g, b)
            
            return self.special_timer > 0
        return True
    
    def draw(self, display):
        if self.special:
            # Draw special food with glow effect
            glow_radius = SNAKE_BLOCK + 4 + int(math.sin(self.pulse_value * math.pi * 2) * 3)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, 100), (glow_radius, glow_radius), glow_radius)
            display.blit(glow_surface, (self.x - glow_radius + SNAKE_BLOCK//2, self.y - glow_radius + SNAKE_BLOCK//2))
            
            # Draw star shape for special food
            points = []
            for i in range(5):
                # Outer points (star tips)
                angle = math.pi/2 + i * 2*math.pi/5
                points.append((self.x + SNAKE_BLOCK/2 + math.cos(angle) * SNAKE_BLOCK/2,
                              self.y + SNAKE_BLOCK/2 + math.sin(angle) * SNAKE_BLOCK/2))
                
                # Inner points
                angle += math.pi/5
                points.append((self.x + SNAKE_BLOCK/2 + math.cos(angle) * SNAKE_BLOCK/4,
                              self.y + SNAKE_BLOCK/2 + math.sin(angle) * SNAKE_BLOCK/4))
            
            pygame.draw.polygon(display, self.color, points)
        else:
            # Draw regular food as a circle
            pygame.draw.circle(display, self.color, 
                              (self.x + SNAKE_BLOCK//2, self.y + SNAKE_BLOCK//2), 
                              SNAKE_BLOCK//2)

# Base Predator class
class Predator:
    def __init__(self, size_factor=1.5, speed=2.5, spawn_time_min=300, spawn_time_max=600, active_duration=200, predator_type="Predator"):
        self.active = False
        self.x = 0
        self.y = 0
        self.size = SNAKE_BLOCK * size_factor
        self.speed = speed
        self.spawn_timer = random.randint(spawn_time_min, spawn_time_max)
        self.active_duration = active_duration
        self.animation_counter = 0
        self.predator_type = predator_type
        self.speech_bubble = SpeechBubble(owner=self)
        self.dialogue_timer = 0
        self.dialogue_interval = random.randint(180, 300)  # Random interval between dialogues
        self.anger_level = 1  # Initialize anger level to 1 (neutral)
        
    def update(self, snake_head, dialogue_generator=None, snake_body=None):
        # Update speech bubble
        self.speech_bubble.update()
        
        # Get anger level if dialogue generator is available
        self.anger_level = 1
        if dialogue_generator and hasattr(dialogue_generator, 'predator_anger_levels'):
            self.anger_level = dialogue_generator.predator_anger_levels.get(self.predator_type, 1)
        
        if not self.active:
            # Count down to spawn
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                self.spawn()
            return False, False  # No collision with head or body
        
        # Only despawn if predator goes off-screen by a large margin
        screen_margin = 200  # Allow predators to go a bit off-screen before despawning
        if (self.x < -screen_margin or self.x > DISPLAY_WIDTH + screen_margin or 
            self.y < -screen_margin or self.y > DISPLAY_HEIGHT + screen_margin):
            self.active = False
            self.spawn_timer = random.randint(300, 600)  # Set next spawn time
            return False, False
        
        # Handle dialogue generation
        if dialogue_generator and self.active:
            self.dialogue_timer -= 1
            if self.dialogue_timer <= 0:
                # Determine predator action based on distance to snake
                action = "hunting"
                if snake_head:
                    dx = snake_head[0] - self.x
                    dy = snake_head[1] - self.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist < DISPLAY_WIDTH / 4:
                        action = "closing in"
                    if dist < DISPLAY_WIDTH / 8:
                        action = "about to strike"
                
                # Queue dialogue generation
                dialogue = dialogue_generator.generate_predator_dialogue(self.predator_type, action)
                if dialogue:
                    self.speech_bubble.set_text(dialogue, self)
                
                # Reset dialogue timer with some randomness
                self.dialogue_interval = random.randint(180, 300)
                self.dialogue_timer = self.dialogue_interval
        
        # Move towards snake head
        if snake_head:
            dx = snake_head[0] - self.x
            dy = snake_head[1] - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                dx = dx / dist * self.speed
                dy = dy / dist * self.speed
                
                self.x += dx
                self.y += dy
            
            # Check for collision with snake head
            head_collision = dist < SNAKE_BLOCK
            
            # Check for collision with snake body
            body_collision = False
            if snake_body:
                predator_rect = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
                for segment in snake_body[:-1]:  # Exclude head which is already checked
                    segment_rect = pygame.Rect(segment[0], segment[1], SNAKE_BLOCK, SNAKE_BLOCK)
                    if predator_rect.colliderect(segment_rect):
                        body_collision = True
                        break
            
            return head_collision, body_collision
                
        # Update animation
        self.animation_counter += 0.2
        
        return False, False  # No collision with head or body
        
    def spawn(self):
        # Spawn at a random edge of the screen
        side = random.randint(0, 3)
        if side == 0:  # Top
            self.x = random.randint(0, DISPLAY_WIDTH)
            self.y = -self.size
        elif side == 1:  # Right
            self.x = DISPLAY_WIDTH + self.size
            self.y = random.randint(0, DISPLAY_HEIGHT)
        elif side == 2:  # Bottom
            self.x = random.randint(0, DISPLAY_WIDTH)
            self.y = DISPLAY_HEIGHT + self.size
        else:  # Left
            self.x = -self.size
            self.y = random.randint(0, DISPLAY_HEIGHT)
            
        self.active = True
        
        # Randomize active duration to create more varied predator behaviors
        # This helps prevent all predators from disappearing at the same time
        self.active_duration = random.randint(150, 250)
        
        # Set a short dialogue timer so predator speaks soon after spawning
        self.dialogue_timer = random.randint(30, 60)
        
    def draw(self, display):
        # To be implemented by subclasses
        pass

# Eagle class - predator that follows the snake
class Eagle(Predator):
    def __init__(self):
        super().__init__(size_factor=1.5, speed=2.5, spawn_time_min=300, spawn_time_max=600, active_duration=200, predator_type="Eagle")
        
    def draw(self, display):
        if not self.active:
            return
            
        # Draw eagle body
        body_color = BROWN
        wing_color = (139, 69, 19)  # Darker brown
        beak_color = ORANGE
        
        # Make eagle redder when angry
        if hasattr(self, 'anger_level') and self.anger_level > 1:
            # Add red tint based on anger level
            red_tint = min(50 * (self.anger_level - 1), 150)
            body_color = (min(body_color[0] + red_tint, 255), 
                          max(body_color[1] - red_tint//2, 0), 
                          max(body_color[2] - red_tint//2, 0))
            beak_color = (min(beak_color[0] + red_tint, 255),
                          max(beak_color[1] - red_tint//3, 0),
                          beak_color[2])
        
        # Draw wings (flapping animation)
        wing_span = self.size * (0.8 + 0.2 * math.sin(self.animation_counter))
        wing_height = self.size * 0.4
        
        # Left wing
        points_left = [
            (self.x, self.y),
            (self.x - wing_span, self.y - wing_height),
            (self.x, self.y + wing_height/2)
        ]
        pygame.draw.polygon(display, wing_color, points_left)
        
        # Right wing
        points_right = [
            (self.x, self.y),
            (self.x + wing_span, self.y - wing_height),
            (self.x, self.y + wing_height/2)
        ]
        pygame.draw.polygon(display, wing_color, points_right)
        
        # Body
        pygame.draw.circle(display, body_color, (int(self.x), int(self.y)), int(self.size/2))
        
        # Head
        head_x = self.x
        head_y = self.y - self.size/3
        pygame.draw.circle(display, body_color, (int(head_x), int(head_y)), int(self.size/3))
        
        # Beak
        beak_length = self.size/3
        pygame.draw.polygon(display, beak_color, [
            (head_x, head_y - self.size/6),
            (head_x + beak_length, head_y),
            (head_x, head_y + self.size/6)
        ])
        
        # Eye
        pygame.draw.circle(display, BLACK, (int(head_x + self.size/8), int(head_y - self.size/10)), int(self.size/10))
        
        # Draw speech bubble
        self.speech_bubble.draw(display)

# Mongoose class - fast predator that hunts snakes
class Mongoose(Predator):
    def __init__(self):
        super().__init__(size_factor=1.2, speed=3.5, spawn_time_min=500, spawn_time_max=800, active_duration=150, predator_type="Mongoose")
        self.direction = 0  # Direction angle
        
    def update(self, snake_head, dialogue_generator=None, snake_body=None):
        # Update speech bubble
        self.speech_bubble.update()
        
        # Get anger level if dialogue generator is available
        self.anger_level = 1
        if dialogue_generator and hasattr(dialogue_generator, 'predator_anger_levels'):
            self.anger_level = dialogue_generator.predator_anger_levels.get(self.predator_type, 1)
            
        if not self.active:
            # Count down to spawn
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                self.spawn()
            return False, False  # No collision with head or body
        
        # Only despawn if mongoose goes off-screen by a large margin
        screen_margin = 200  # Allow predators to go a bit off-screen before despawning
        if (self.x < -screen_margin or self.x > DISPLAY_WIDTH + screen_margin or 
            self.y < -screen_margin or self.y > DISPLAY_HEIGHT + screen_margin):
            self.active = False
            self.spawn_timer = random.randint(500, 800)
            return False, False
            
        # Handle dialogue generation
        if dialogue_generator and self.active:
            self.dialogue_timer -= 1
            if self.dialogue_timer <= 0:
                # Determine predator action based on distance to snake
                action = "hunting"
                if snake_head:
                    dx = snake_head[0] - self.x
                    dy = snake_head[1] - self.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist < DISPLAY_WIDTH / 4:
                        action = "closing in"
                    if dist < DISPLAY_WIDTH / 8:
                        action = "about to strike"
                
                # Queue dialogue generation
                dialogue = dialogue_generator.generate_predator_dialogue(self.predator_type, action)
                if dialogue:
                    self.speech_bubble.set_text(dialogue, self)
                
                # Reset dialogue timer with some randomness
                self.dialogue_interval = random.randint(180, 300)
                self.dialogue_timer = self.dialogue_interval
        
        # Move towards snake head with more erratic movement
        if snake_head:
            dx = snake_head[0] - self.x
            dy = snake_head[1] - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                # Calculate direction to snake
                target_direction = math.atan2(dy, dx)
                
                # Gradually adjust current direction towards target (smoother turning)
                angle_diff = target_direction - self.direction
                # Normalize angle difference to [-pi, pi]
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                
                # Adjust direction with some randomness for erratic movement
                self.direction += angle_diff * 0.1 + (random.random() - 0.5) * 0.2
                
                # Move in current direction
                self.x += math.cos(self.direction) * self.speed
                self.y += math.sin(self.direction) * self.speed
            
            # Check for collision with snake head
            head_collision = dist < SNAKE_BLOCK
            
            # Check for collision with snake body
            body_collision = False
            if snake_body:
                predator_rect = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
                for segment in snake_body[:-1]:  # Exclude head which is already checked
                    segment_rect = pygame.Rect(segment[0], segment[1], SNAKE_BLOCK, SNAKE_BLOCK)
                    if predator_rect.colliderect(segment_rect):
                        body_collision = True
                        break
            
            if head_collision or body_collision:
                return head_collision, body_collision
                
        # Update animation
        self.animation_counter += 0.3  # Faster animation for mongoose
        
        return False, False
        
    def draw(self, display):
        if not self.active:
            return
            
        # Draw mongoose
        body_color = (200, 150, 100)  # Light brown
        
        # Make mongoose redder when angry
        if hasattr(self, 'anger_level') and self.anger_level > 1:
            # Add red tint based on anger level
            red_tint = min(50 * (self.anger_level - 1), 150)
            body_color = (min(body_color[0] + red_tint, 255), 
                          max(body_color[1] - red_tint//2, 0), 
                          max(body_color[2] - red_tint//2, 0))
        
        # Calculate body points based on direction
        body_length = self.size * 1.5
        head_x = self.x + math.cos(self.direction) * (body_length/2)
        head_y = self.y + math.sin(self.direction) * (body_length/2)
        tail_x = self.x - math.cos(self.direction) * (body_length/2)
        tail_y = self.y - math.sin(self.direction) * (body_length/2)
        
        # Body (elongated ellipse approximated with a polygon)
        body_width = self.size * 0.6
        perp_x = math.cos(self.direction + math.pi/2) * body_width/2
        perp_y = math.sin(self.direction + math.pi/2) * body_width/2
        
        body_points = [
            (head_x - perp_x, head_y - perp_y),
            (head_x + perp_x, head_y + perp_y),
            (tail_x + perp_x, tail_y + perp_y),
            (tail_x - perp_x, tail_y - perp_y)
        ]
        pygame.draw.polygon(display, body_color, body_points)
        
        # Head
        pygame.draw.circle(display, body_color, (int(head_x), int(head_y)), int(self.size/2))
        
        # Eyes
        eye_offset_x = math.cos(self.direction + math.pi/4) * (self.size/4)
        eye_offset_y = math.sin(self.direction + math.pi/4) * (self.size/4)
        pygame.draw.circle(display, BLACK, (int(head_x + eye_offset_x), int(head_y + eye_offset_y)), int(self.size/10))
        
        eye_offset_x = math.cos(self.direction - math.pi/4) * (self.size/4)
        eye_offset_y = math.sin(self.direction - math.pi/4) * (self.size/4)
        pygame.draw.circle(display, BLACK, (int(head_x + eye_offset_x), int(head_y + eye_offset_y)), int(self.size/10))
        
        # Tail with wave animation
        tail_wave = math.sin(self.animation_counter) * (self.size/3)
        tail_perp_x = math.cos(self.direction + math.pi/2) * tail_wave
        tail_perp_y = math.sin(self.direction + math.pi/2) * tail_wave
        
        tail_points = [
            (tail_x, tail_y),
            (tail_x - math.cos(self.direction) * (self.size/2) + tail_perp_x, 
             tail_y - math.sin(self.direction) * (self.size/2) + tail_perp_y)
        ]
        pygame.draw.line(display, body_color, tail_points[0], tail_points[1], int(self.size/4))
        
        # Draw speech bubble
        self.speech_bubble.draw(display)

# Hawk class - predator that dives quickly at the snake
class Hawk(Predator):
    def __init__(self):
        super().__init__(size_factor=1.3, speed=1.8, spawn_time_min=700, spawn_time_max=1000, active_duration=180, predator_type="Hawk")
        self.diving = False
        self.dive_target_x = 0
        self.dive_target_y = 0
        self.dive_speed = 8.0
        self.circling_radius = 150
        self.circling_angle = random.random() * 2 * math.pi
        self.circling_speed = 0.02
        
    def update(self, snake_head, dialogue_generator=None, snake_body=None):
        # Update speech bubble
        self.speech_bubble.update()
        
        # Get anger level if dialogue generator is available
        self.anger_level = 1
        if dialogue_generator and hasattr(dialogue_generator, 'predator_anger_levels'):
            self.anger_level = dialogue_generator.predator_anger_levels.get(self.predator_type, 1)
            
        if not self.active:
            # Count down to spawn
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                self.spawn()
            return False, False  # No collision with head or body
        
        # Only despawn if hawk goes off-screen by a large margin
        screen_margin = 200  # Allow predators to go a bit off-screen before despawning
        if (self.x < -screen_margin or self.x > DISPLAY_WIDTH + screen_margin or 
            self.y < -screen_margin or self.y > DISPLAY_HEIGHT + screen_margin):
            self.active = False
            self.spawn_timer = random.randint(700, 1000)
            return False, False
            
        # Handle dialogue generation
        if dialogue_generator and self.active:
            self.dialogue_timer -= 1
            if self.dialogue_timer <= 0:
                # Determine predator action based on state
                action = "circling above"
                if self.diving:
                    action = "diving to attack"
                
                # Queue dialogue generation
                dialogue = dialogue_generator.generate_predator_dialogue(self.predator_type, action)
                if dialogue:
                    self.speech_bubble.set_text(dialogue, self)
                
                # Reset dialogue timer with some randomness
                self.dialogue_interval = random.randint(180, 300)
                self.dialogue_timer = self.dialogue_interval
        
        if snake_head:
            if not self.diving:
                # Circle above the snake
                self.circling_angle += self.circling_speed
                self.x = snake_head[0] + math.cos(self.circling_angle) * self.circling_radius
                self.y = snake_head[1] + math.sin(self.circling_angle) * self.circling_radius
                
                # Randomly decide to dive
                if random.random() < 0.01:  # 1% chance per frame
                    self.diving = True
                    self.dive_target_x = snake_head[0]
                    self.dive_target_y = snake_head[1]
            else:
                # Dive towards the target
                dx = self.dive_target_x - self.x
                dy = self.dive_target_y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > 5:
                    self.x += (dx / dist) * self.dive_speed
                    self.y += (dy / dist) * self.dive_speed
                else:
                    # Reached dive target, go back to circling
                    self.diving = False
                
                # Check for collision with snake head
                dx = snake_head[0] - self.x
                dy = snake_head[1] - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                head_collision = dist < SNAKE_BLOCK
                
                # Check for collision with snake body
                body_collision = False
                if snake_body:
                    predator_rect = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
                    for segment in snake_body[:-1]:  # Exclude head which is already checked
                        segment_rect = pygame.Rect(segment[0], segment[1], SNAKE_BLOCK, SNAKE_BLOCK)
                        if predator_rect.colliderect(segment_rect):
                            body_collision = True
                            break
                
                if head_collision or body_collision:
                    return head_collision, body_collision
        
        # Update animation
        self.animation_counter += 0.15
        
        return False, False
        
    def draw(self, display):
        if not self.active:
            return
            
        # Draw hawk
        body_color = (80, 80, 80)  # Dark gray
        wing_color = (120, 120, 120)  # Light gray
        beak_color = YELLOW
        
        # Make hawk redder when angry
        if hasattr(self, 'anger_level') and self.anger_level > 1:
            # Add red tint based on anger level
            red_tint = min(50 * (self.anger_level - 1), 150)
            body_color = (min(body_color[0] + red_tint, 255), 
                          max(body_color[1] - red_tint//2, 0), 
                          max(body_color[2] - red_tint//2, 0))
            wing_color = (min(wing_color[0] + red_tint, 255),
                          max(wing_color[1] - red_tint//2, 0),
                          max(wing_color[2] - red_tint//2, 0))
            beak_color = (min(beak_color[0] + red_tint//2, 255),
                          max(beak_color[1] - red_tint//3, 0),
                          beak_color[2])
        
        # Draw differently based on if diving or circling
        if self.diving:
            # Streamlined diving pose
            # Body
            pygame.draw.circle(display, body_color, (int(self.x), int(self.y)), int(self.size/2))
            
            # Wings tucked in
            wing_length = self.size * 0.7
            pygame.draw.ellipse(display, wing_color, 
                              (int(self.x - wing_length/2), 
                               int(self.y - self.size/4),
                               int(wing_length),
                               int(self.size/2)))
            
            # Head/beak pointing down
            head_x = self.x
            head_y = self.y + self.size/2
            pygame.draw.circle(display, body_color, (int(head_x), int(head_y)), int(self.size/3))
            
            # Beak
            pygame.draw.polygon(display, beak_color, [
                (head_x - self.size/6, head_y),
                (head_x + self.size/6, head_y),
                (head_x, head_y + self.size/3)
            ])
        else:
            # Circling pose with spread wings
            # Wings (flapping animation)
            wing_span = self.size * (1.5 + 0.2 * math.sin(self.animation_counter))
            wing_height = self.size * 0.3
            
            # Left wing
            points_left = [
                (self.x, self.y),
                (self.x - wing_span, self.y - wing_height),
                (self.x - wing_span/2, self.y),
                (self.x - wing_span, self.y + wing_height),
            ]
            pygame.draw.polygon(display, wing_color, points_left)
            
            # Right wing
            points_right = [
                (self.x, self.y),
                (self.x + wing_span, self.y - wing_height),
                (self.x + wing_span/2, self.y),
                (self.x + wing_span, self.y + wing_height),
            ]
            pygame.draw.polygon(display, wing_color, points_right)
            
            # Body
            pygame.draw.circle(display, body_color, (int(self.x), int(self.y)), int(self.size/2))
            
            # Head
            head_x = self.x
            head_y = self.y - self.size/3
            pygame.draw.circle(display, body_color, (int(head_x), int(head_y)), int(self.size/3))
            
            # Beak
            pygame.draw.polygon(display, beak_color, [
                (head_x - self.size/6, head_y),
                (head_x + self.size/6, head_y),
                (head_x, head_y - self.size/3)
            ])
        
        # Eyes (always visible)
        eye_x = self.x - self.size/8 if not self.diving else self.x - self.size/8
        eye_y = self.y - self.size/3 if not self.diving else self.y + self.size/3
        pygame.draw.circle(display, BLACK, (int(eye_x), int(eye_y)), int(self.size/12))
        
        eye_x = self.x + self.size/8 if not self.diving else self.x + self.size/8
        pygame.draw.circle(display, BLACK, (int(eye_x), int(eye_y)), int(self.size/12))
        
        # Draw speech bubble
        self.speech_bubble.draw(display)

# Snake class
class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_change = 0
        self.y_change = 0
        self.speech_bubble = SpeechBubble()
        self.dialogue_timer = 0
        self.dialogue_interval = random.randint(240, 360)  # Random interval between dialogues
        self.body = []
        self.length = 1
        self.direction = None  # None, 'UP', 'DOWN', 'LEFT', 'RIGHT'
        self.color = COLOR_SCHEMES[CURRENT_SCHEME]["body"]
        self.head_color = COLOR_SCHEMES[CURRENT_SCHEME]["head"]
        self.collision_point = None  # Index of body segment where collision occurred
        self.is_dead = False  # Flag to indicate death state for animation
        self.death_animation_frame = 0  # Counter for death animation
        self.boost_charge = 0  # Current boost charge level
        self.boost_active = False  # Whether speed boost is currently active
        self.boost_timer = 0  # Timer for active boost duration
    
    def change_direction(self, direction):
        # Prevent 180-degree turns
        if direction == 'LEFT' and self.direction != 'RIGHT':
            self.x_change = -SNAKE_BLOCK
            self.y_change = 0
            self.direction = 'LEFT'
        elif direction == 'RIGHT' and self.direction != 'LEFT':
            self.x_change = SNAKE_BLOCK
            self.y_change = 0
            self.direction = 'RIGHT'
        elif direction == 'UP' and self.direction != 'DOWN':
            self.y_change = -SNAKE_BLOCK
            self.x_change = 0
            self.direction = 'UP'
        elif direction == 'DOWN' and self.direction != 'UP':
            self.y_change = SNAKE_BLOCK
            self.x_change = 0
            self.direction = 'DOWN'
    
    def move(self):
        # Update position
        self.x += self.x_change
        self.y += self.y_change
        
        # Add new head position
        self.body.append([self.x, self.y])
        
        # Remove tail if necessary
        if len(self.body) > self.length:
            del self.body[0]
    
    def check_collision_with_self(self):
        # Check if head collides with body
        head = self.body[-1]
        for i, segment in enumerate(self.body[:-1]):
            if segment[0] == head[0] and segment[1] == head[1]:
                # Store collision point for death animation
                self.collision_point = i
                return True
        return False
    
    def check_collision_with_boundaries(self):
        # Check if snake hits the boundaries
        head = self.body[-1]
        return (head[0] >= DISPLAY_WIDTH or head[0] < 0 or 
                head[1] >= DISPLAY_HEIGHT or head[1] < 0)
    
    def check_collision_with_food(self, food):
        # Check if snake eats food
        head = self.body[-1]
        return head[0] == food.x and head[1] == food.y
    
    def grow(self, amount=1):
        self.length += amount
        
    def add_boost_charge(self):
        # Add boost charge when eating food
        if self.boost_charge < MAX_BOOST_CHARGE:
            self.boost_charge += 1
            
    def activate_boost(self):
        # Activate speed boost if there's enough charge
        if self.boost_charge > 0 and not self.boost_active:
            self.boost_active = True
            self.boost_timer = 30  # Boost lasts for 30 frames
            
    def update_boost(self):
        # Update boost status
        if self.boost_active:
            self.boost_timer -= 1
            if self.boost_timer <= 0:
                self.boost_active = False
                self.boost_charge -= 1  # Consume one charge
    
    def update_dialogue(self, dialogue_generator=None, predators=None):
        # Update speech bubble
        self.speech_bubble.update()
        
        # Handle dialogue generation
        if dialogue_generator and not self.is_dead:
            self.dialogue_timer -= 1
            if self.dialogue_timer <= 0:
                # Only respond if there's at least one active predator
                active_predators = [p for p in predators if p.active]
                if active_predators:
                    # Choose a random active predator to respond to
                    predator = random.choice(active_predators)
                    
                    # Generate snake response
                    dialogue = dialogue_generator.generate_snake_response(predator.predator_type)
                    if dialogue:
                        self.speech_bubble.set_text(dialogue, self.body)
                        
                        # FORCE the predator to respond immediately to the snake's insult
                        # This ensures the predator always answers
                        predator.dialogue_timer = 1
                        
                        # Make predator angrier and faster when taunted
                        if hasattr(predator, 'anger_level'):
                            predator.anger_level = min(predator.anger_level + 1, 4)
                            # Increase speed based on anger
                            if isinstance(predator, Eagle):
                                predator.speed += 0.5
                            elif isinstance(predator, Mongoose):
                                predator.speed += 0.7
                            elif isinstance(predator, Hawk):
                                predator.dive_speed += 1.0
                
                # Reset dialogue timer with some randomness
                self.dialogue_interval = random.randint(180, 240)  # Shorter interval for more frequent taunts
                self.dialogue_timer = self.dialogue_interval
    
    def draw(self, display):
        # Draw snake body
        for i, segment in enumerate(self.body):
            # Calculate segment color (gradient effect)
            if i == len(self.body) - 1:  # Head
                # If dead, make head red
                if self.is_dead:
                    color = RED
                else:
                    color = self.head_color
                
                # Draw eyes
                if self.direction == 'RIGHT':
                    eye1_pos = (segment[0] + SNAKE_BLOCK * 3/4, segment[1] + SNAKE_BLOCK/4)
                    eye2_pos = (segment[0] + SNAKE_BLOCK * 3/4, segment[1] + SNAKE_BLOCK * 3/4)
                elif self.direction == 'LEFT':
                    eye1_pos = (segment[0] + SNAKE_BLOCK/4, segment[1] + SNAKE_BLOCK/4)
                    eye2_pos = (segment[0] + SNAKE_BLOCK/4, segment[1] + SNAKE_BLOCK * 3/4)
                elif self.direction == 'UP':
                    eye1_pos = (segment[0] + SNAKE_BLOCK/4, segment[1] + SNAKE_BLOCK/4)
                    eye2_pos = (segment[0] + SNAKE_BLOCK * 3/4, segment[1] + SNAKE_BLOCK/4)
                elif self.direction == 'DOWN':
                    eye1_pos = (segment[0] + SNAKE_BLOCK/4, segment[1] + SNAKE_BLOCK * 3/4)
                    eye2_pos = (segment[0] + SNAKE_BLOCK * 3/4, segment[1] + SNAKE_BLOCK * 3/4)
                else:  # Default eyes if no direction
                    eye1_pos = (segment[0] + SNAKE_BLOCK/4, segment[1] + SNAKE_BLOCK/4)
                    eye2_pos = (segment[0] + SNAKE_BLOCK * 3/4, segment[1] + SNAKE_BLOCK/4)
            else:
                # Create gradient effect for body
                intensity = 0.5 + 0.5 * (i / len(self.body))
                r = int(self.color[0] * intensity)
                g = int(self.color[1] * intensity)
                b = int(self.color[2] * intensity)
                color = (r, g, b)
                
                # Highlight collision point if dead and this is where collision occurred
                if self.is_dead and self.collision_point is not None:
                    if i == self.collision_point:
                        # Pulse the collision segment with red
                        pulse = 0.5 + 0.5 * math.sin(self.death_animation_frame * 0.3)
                        color = (255, int(g * (1 - pulse)), int(b * (1 - pulse)))
            
            # Apply boost effect if active
            if self.boost_active:
                # Create a pulsing glow effect for the snake when boost is active
                pulse_intensity = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 50
                r = min(255, color[0] + pulse_intensity)
                g = min(255, color[1] + pulse_intensity)
                b = min(255, color[2] + pulse_intensity)
                color = (r, g, b)
                
                # Draw a trail effect behind the snake
                if i > 0 and i % 2 == 0:  # Every other segment
                    trail_color = GOLD
                    trail_size = SNAKE_BLOCK // 3
                    trail_x = segment[0] + SNAKE_BLOCK // 2 - trail_size // 2
                    trail_y = segment[1] + SNAKE_BLOCK // 2 - trail_size // 2
                    pygame.draw.rect(display, trail_color, [trail_x, trail_y, trail_size, trail_size], border_radius=2)
            
            # Draw rounded rectangle for segment
            rect = pygame.Rect(segment[0], segment[1], SNAKE_BLOCK, SNAKE_BLOCK)
            pygame.draw.rect(display, color, rect, border_radius=3)
            
            # Draw collision highlight if this is where collision occurred
            if self.is_dead and self.collision_point is not None and i == self.collision_point:
                # Draw pulsing glow around collision point
                glow_size = SNAKE_BLOCK + 6 + int(4 * math.sin(self.death_animation_frame * 0.3))
                glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                
                # Create radial gradient for glow
                for radius in range(glow_size // 2, 0, -1):
                    alpha = int(200 * (radius / (glow_size // 2)))
                    pygame.draw.circle(glow_surface, (255, 0, 0, alpha), 
                                      (glow_size // 2, glow_size // 2), radius)
                
                # Draw glow
                display.blit(glow_surface, 
                            (segment[0] + SNAKE_BLOCK//2 - glow_size//2, 
                             segment[1] + SNAKE_BLOCK//2 - glow_size//2))
                
                # Draw "X" mark at collision point
                line_width = 3
                offset = 5
                pygame.draw.line(display, WHITE, 
                                (segment[0] + offset, segment[1] + offset),
                                (segment[0] + SNAKE_BLOCK - offset, segment[1] + SNAKE_BLOCK - offset), 
                                line_width)
                pygame.draw.line(display, WHITE, 
                                (segment[0] + offset, segment[1] + SNAKE_BLOCK - offset),
                                (segment[0] + SNAKE_BLOCK - offset, segment[1] + offset), 
                                line_width)
            
            # Draw eyes on head
            if i == len(self.body) - 1 and self.direction:
                if self.is_dead:
                    # X eyes when dead
                    eye_size = SNAKE_BLOCK/8
                    pygame.draw.line(display, WHITE, 
                                    (eye1_pos[0] - eye_size, eye1_pos[1] - eye_size),
                                    (eye1_pos[0] + eye_size, eye1_pos[1] + eye_size), 2)
                    pygame.draw.line(display, WHITE, 
                                    (eye1_pos[0] - eye_size, eye1_pos[1] + eye_size),
                                    (eye1_pos[0] + eye_size, eye1_pos[1] - eye_size), 2)
                    
                    pygame.draw.line(display, WHITE, 
                                    (eye2_pos[0] - eye_size, eye2_pos[1] - eye_size),
                                    (eye2_pos[0] + eye_size, eye2_pos[1] + eye_size), 2)
                    pygame.draw.line(display, WHITE, 
                                    (eye2_pos[0] - eye_size, eye2_pos[1] + eye_size),
                                    (eye2_pos[0] + eye_size, eye2_pos[1] - eye_size), 2)
                else:
                    # Normal eyes
                    pygame.draw.circle(display, WHITE, eye1_pos, SNAKE_BLOCK/8)
                    pygame.draw.circle(display, WHITE, eye2_pos, SNAKE_BLOCK/8)
        
        # Draw speech bubble if active
        if not self.is_dead:
            self.speech_bubble.draw(display)

# Speech bubble class for displaying dialogue
class SpeechBubble:
    def __init__(self, text="", owner=None, duration=180):
        self.active = False  # Always inactive
        self.owner = owner
        
    def set_text(self, text, owner=None):
        # Do nothing - no speech bubbles
        pass
        
    def update(self):
        # Do nothing - no speech bubbles
        pass
                
    def draw(self, display):
        # Do nothing - no speech bubbles
        pass

# Button class for UI
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
    
    def draw(self, display):
        # Calculate the center offset to ensure the game is centered in fullscreen
        offset_x = (SCREEN_WIDTH - (DISPLAY_WIDTH * SCALE_FACTOR_X)) / 2
        offset_y = (SCREEN_HEIGHT - (DISPLAY_HEIGHT * SCALE_FACTOR_Y)) / 2
        
        # Scale the button for current display mode with offset
        scaled_rect = pygame.Rect(
            (self.x * SCALE_FACTOR_X) + offset_x,
            (self.y * SCALE_FACTOR_Y) + offset_y,
            self.width * SCALE_FACTOR_X,
            self.height * SCALE_FACTOR_Y
        )
        
        # Draw button with hover effect
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(display, color, scaled_rect, border_radius=int(10 * min(SCALE_FACTOR_X, SCALE_FACTOR_Y)))
        pygame.draw.rect(display, WHITE, scaled_rect, max(1, int(2 * min(SCALE_FACTOR_X, SCALE_FACTOR_Y))), 
                        border_radius=int(10 * min(SCALE_FACTOR_X, SCALE_FACTOR_Y)))  # Scaled border
        
        # Scale font size based on display mode
        font_size = int(30 * min(SCALE_FACTOR_X, SCALE_FACTOR_Y))
        scaled_font = pygame.font.SysFont(None, max(10, font_size))
        
        # Draw text
        text_surf = scaled_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        display.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        if FULLSCREEN:
            # Calculate the center offset
            offset_x = (SCREEN_WIDTH - (DISPLAY_WIDTH * SCALE_FACTOR_X)) / 2
            offset_y = (SCREEN_HEIGHT - (DISPLAY_HEIGHT * SCALE_FACTOR_Y)) / 2
            
            # Adjust position for offset and scaling
            adjusted_pos = [
                (pos[0] - offset_x) / SCALE_FACTOR_X,
                (pos[1] - offset_y) / SCALE_FACTOR_Y
            ]
            self.is_hovered = self.rect.collidepoint(adjusted_pos)
        else:
            self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if FULLSCREEN:
                # Calculate the center offset
                offset_x = (SCREEN_WIDTH - (DISPLAY_WIDTH * SCALE_FACTOR_X)) / 2
                offset_y = (SCREEN_HEIGHT - (DISPLAY_HEIGHT * SCALE_FACTOR_Y)) / 2
                
                # Adjust position for offset and scaling
                adjusted_pos = [
                    (pos[0] - offset_x) / SCALE_FACTOR_X,
                    (pos[1] - offset_y) / SCALE_FACTOR_Y
                ]
                return self.rect.collidepoint(adjusted_pos)
            else:
                return self.rect.collidepoint(pos)
        return False

# Function to scale coordinates for fullscreen
def scale_rect(rect):
    """Scale a rectangle (x, y, width, height) based on current scale factors"""
    return [
        rect[0] * SCALE_FACTOR_X,
        rect[1] * SCALE_FACTOR_Y,
        rect[2] * SCALE_FACTOR_X,
        rect[3] * SCALE_FACTOR_Y
    ]

# Function to scale a position (x, y)
def scale_pos(pos):
    """Scale a position (x, y) based on current scale factors"""
    return [pos[0] * SCALE_FACTOR_X, pos[1] * SCALE_FACTOR_Y]

# Function to unscale a position (from screen coordinates to game coordinates)
def unscale_pos(pos):
    """Convert screen coordinates back to game coordinates"""
    return [pos[0] / SCALE_FACTOR_X, pos[1] / SCALE_FACTOR_Y]

# Function to toggle fullscreen mode
def toggle_fullscreen():
    global FULLSCREEN, display, SCALE_FACTOR_X, SCALE_FACTOR_Y, SCREEN_WIDTH, SCREEN_HEIGHT
    FULLSCREEN = not FULLSCREEN
    
    if FULLSCREEN:
        # Get the actual screen size
        info = pygame.display.Info()
        SCREEN_WIDTH = info.current_w
        SCREEN_HEIGHT = info.current_h
        
        # Calculate scaling factors - use the same scale factor for both dimensions
        # to maintain aspect ratio, based on the smaller of the two ratios
        scale_x = SCREEN_WIDTH / DISPLAY_WIDTH
        scale_y = SCREEN_HEIGHT / DISPLAY_HEIGHT
        
        # Use the larger scaling factor to ensure the game fills the screen
        # This might crop a bit of the game but ensures no black bars
        SCALE_FACTOR_X = max(scale_x, scale_y)
        SCALE_FACTOR_Y = max(scale_x, scale_y)
        
        # Set fullscreen mode with hardware acceleration for better quality
        display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 
                                         pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        print(f"Fullscreen enabled: {SCREEN_WIDTH}x{SCREEN_HEIGHT}, Scale: {SCALE_FACTOR_X}x{SCALE_FACTOR_Y}")
    else:
        # Reset to windowed mode
        SCREEN_WIDTH = DISPLAY_WIDTH
        SCREEN_HEIGHT = DISPLAY_HEIGHT
        SCALE_FACTOR_X = 1.0
        SCALE_FACTOR_Y = 1.0
        display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        print(f"Windowed mode: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")

# Function to display score
def display_score(score, high_score, boost_charge=0, boost_active=False):
    # Scale font size based on current display mode
    if FULLSCREEN:
        font_size = int(35 * min(SCALE_FACTOR_X, SCALE_FACTOR_Y))
        font = pygame.font.SysFont(None, max(10, font_size))
    else:
        font = score_font
    
    # Render text
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    
    # Calculate the center offset to ensure the game is centered in fullscreen
    offset_x = (SCREEN_WIDTH - (DISPLAY_WIDTH * SCALE_FACTOR_X)) / 2
    offset_y = (SCREEN_HEIGHT - (DISPLAY_HEIGHT * SCALE_FACTOR_Y)) / 2
    
    # Scale positions with offset
    padding = 20 * SCALE_FACTOR_X
    score_x = offset_x + padding
    score_y = offset_y + padding
    high_score_x = SCREEN_WIDTH - offset_x - high_score_text.get_width() - padding
    
    # Draw text
    display.blit(score_text, [score_x, score_y])
    display.blit(high_score_text, [high_score_x, score_y])
    
    # Display boost charge
    boost_text = font.render(f"Boost: {boost_charge}/{MAX_BOOST_CHARGE}", True, 
                           GOLD if boost_active else WHITE)
    display.blit(boost_text, [score_x, score_y + (40 * SCALE_FACTOR_Y)])
    
    # Draw boost charge bar (scaled)
    bar_width = 150 * SCALE_FACTOR_X
    bar_height = 20 * SCALE_FACTOR_Y
    border_width = max(1, int(2 * min(SCALE_FACTOR_X, SCALE_FACTOR_Y)))
    
    # Draw border
    bar_y = score_y + (80 * SCALE_FACTOR_Y)
    pygame.draw.rect(display, WHITE, [score_x, bar_y, bar_width, bar_height], border_width)
    
    # Draw filled portion based on charge
    if boost_charge > 0:
        fill_width = int((boost_charge / MAX_BOOST_CHARGE) * (bar_width - 2*border_width))
        fill_color = GOLD if boost_active else GREEN
        pygame.draw.rect(display, fill_color, 
                        [score_x + border_width, 
                         bar_y + border_width, 
                         fill_width, 
                         bar_height - 2*border_width])

# Function to display message
def display_message(msg, color, y_offset=0, size="medium"):
    # Select base font
    if size == "large":
        base_font = title_font
    elif size == "medium":
        base_font = score_font
    elif size == "small":
        base_font = font_style
    else:
        base_font = font_style
    
    # Scale font size based on current display mode
    if FULLSCREEN:
        if size == "large":
            font_size = int(50 * min(SCALE_FACTOR_X, SCALE_FACTOR_Y))
        elif size == "medium":
            font_size = int(35 * min(SCALE_FACTOR_X, SCALE_FACTOR_Y))
        else:
            font_size = int(25 * min(SCALE_FACTOR_X, SCALE_FACTOR_Y))
        font = pygame.font.SysFont(None, max(10, font_size))
    else:
        font = base_font
        
    # Render text with anti-aliasing for better quality
    mesg = font.render(msg, True, color)
    
    # Center in the actual screen (not just the scaled game area)
    x = SCREEN_WIDTH/2 - mesg.get_width()/2
    y = SCREEN_HEIGHT/2 - mesg.get_height()/2 + (y_offset * SCALE_FACTOR_Y)
    
    display.blit(mesg, [x, y])

# Function to draw grid background
def draw_grid():
    # Get background color to determine grid color
    bg_color = COLOR_SCHEMES[CURRENT_SCHEME]["background"]
    
    # Calculate grid color based on background (slightly lighter or darker)
    if sum(bg_color) < 384:  # Dark background
        grid_color = (min(bg_color[0] + 30, 255), 
                     min(bg_color[1] + 30, 255), 
                     min(bg_color[2] + 30, 255))
    else:  # Light background
        grid_color = (max(bg_color[0] - 30, 0), 
                     max(bg_color[1] - 30, 0), 
                     max(bg_color[2] - 30, 0))
    
    # Scale the grid to match the current display size
    scaled_block = SNAKE_BLOCK * SCALE_FACTOR_X
    
    # Calculate the center offset to ensure the game is centered in fullscreen
    offset_x = (SCREEN_WIDTH - (DISPLAY_WIDTH * SCALE_FACTOR_X)) / 2
    offset_y = (SCREEN_HEIGHT - (DISPLAY_HEIGHT * SCALE_FACTOR_Y)) / 2
    
    # Adjust grid line thickness based on scale
    line_thickness = max(1, int(min(SCALE_FACTOR_X, SCALE_FACTOR_Y)))
    
    # Draw vertical grid lines with anti-aliasing for better quality
    for x in range(0, int(DISPLAY_WIDTH * SCALE_FACTOR_X) + 1, max(1, int(scaled_block))):
        x_pos = x + offset_x
        if 0 <= x_pos <= SCREEN_WIDTH:
            # Use aaline for better quality when scaled
            if FULLSCREEN and line_thickness == 1:
                pygame.draw.aaline(display, grid_color, (x_pos, 0), (x_pos, SCREEN_HEIGHT))
            else:
                pygame.draw.line(display, grid_color, (x_pos, 0), (x_pos, SCREEN_HEIGHT), line_thickness)
    
    # Draw horizontal grid lines with anti-aliasing
    for y in range(0, int(DISPLAY_HEIGHT * SCALE_FACTOR_Y) + 1, max(1, int(SNAKE_BLOCK * SCALE_FACTOR_Y))):
        y_pos = y + offset_y
        if 0 <= y_pos <= SCREEN_HEIGHT:
            if FULLSCREEN and line_thickness == 1:
                pygame.draw.aaline(display, grid_color, (0, y_pos), (SCREEN_WIDTH, y_pos))
            else:
                pygame.draw.line(display, grid_color, (0, y_pos), (SCREEN_WIDTH, y_pos), line_thickness)

# Function to draw pause menu
def draw_pause_menu():
    # Semi-transparent overlay
    overlay = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    display.blit(overlay, (0, 0))
    
    # Pause text
    display_message("GAME PAUSED", WHITE, -100, "large")
    display_message("Press P to resume", WHITE, -50)
    
    # Controls info
    display_message("CONTROLS:", WHITE, 0, "medium")
    display_message("Arrow Keys / WASD: Move Snake", WHITE, 40, "small")
    display_message("SPACE: Activate Speed Boost", WHITE, 70, "small")
    display_message("F11: Toggle Fullscreen", WHITE, 100, "small")
    
    # Predator warnings
    display_message("WATCH OUT FOR PREDATORS!", ORANGE, 120, "medium")
    display_message("Eagle: Follows you directly", ORANGE, 150, "small")
    display_message("Mongoose: Fast and erratic movement", ORANGE, 180, "small")
    display_message("Hawk: Circles and dives at you", ORANGE, 210, "small")
    display_message("BEWARE: Multiple predators can appear at once!", RED, 240, "small")
    display_message("Use SPEED BOOST to escape predators!", GOLD, 270, "small")

# Function to show settings menu
def show_settings_menu():
    global CURRENT_SCHEME
    
    settings_running = True
    
    # Create buttons
    back_button = Button(DISPLAY_WIDTH/2 - 100, DISPLAY_HEIGHT - 80, 200, 50, "BACK", BLUE, (30, 100, 180))
    
    # Create color scheme buttons
    scheme_buttons = []
    y_pos = 180
    for i, scheme_name in enumerate(COLOR_SCHEMES.keys()):
        # Arrange buttons in two columns
        if i % 2 == 0:
            x_pos = DISPLAY_WIDTH/2 - 220
        else:
            x_pos = DISPLAY_WIDTH/2 + 20
            y_pos += 70  # Move to next row after second column
        
        # Use the scheme's body color for the button
        scheme_color = COLOR_SCHEMES[scheme_name]["body"]
        # Darken for hover effect
        hover_color = tuple(max(0, c - 50) for c in scheme_color)
        
        button = Button(x_pos, y_pos, 200, 50, scheme_name, scheme_color, hover_color)
        scheme_buttons.append((scheme_name, button))
        
        # Only increment y_pos after every second button (end of row)
        if i % 2 == 1:
            y_pos += 10  # Add some spacing between rows
    
    while settings_running:
        display.fill(BLACK)
        
        # Draw grid background
        draw_grid()
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Handle keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
            
            # Check back button click
            if back_button.is_clicked(mouse_pos, event):
                return
            
            # Check color scheme button clicks
            for scheme_name, button in scheme_buttons:
                if button.is_clicked(mouse_pos, event):
                    CURRENT_SCHEME = scheme_name
                    # Save preference
                    try:
                        with open("snake_settings.txt", "w") as f:
                            f.write(CURRENT_SCHEME)
                    except:
                        pass
        
        # Update button hover states
        back_button.check_hover(mouse_pos)
        for _, button in scheme_buttons:
            button.check_hover(mouse_pos)
        
        # Draw title
        title_text = title_font.render("SETTINGS", True, WHITE)
        display.blit(title_text, [DISPLAY_WIDTH/2 - title_text.get_width()/2, 80])
        
        # Draw subtitle
        subtitle_text = score_font.render("Choose Color Scheme:", True, WHITE)
        display.blit(subtitle_text, [DISPLAY_WIDTH/2 - subtitle_text.get_width()/2, 150])
        
        # Draw color scheme buttons
        for scheme_name, button in scheme_buttons:
            button.draw(display)
            
            # Show "CURRENT" indicator for selected scheme
            if scheme_name == CURRENT_SCHEME:
                indicator = font_style.render("✓ CURRENT", True, WHITE)
                display.blit(indicator, [button.rect.x + button.rect.width/2 - indicator.get_width()/2, 
                                        button.rect.y + button.rect.height + 5])
        
        # Draw back button
        back_button.draw(display)
        
        # Draw preview of selected scheme
        preview_text = font_style.render("Preview:", True, WHITE)
        display.blit(preview_text, [DISPLAY_WIDTH/2 - 150, DISPLAY_HEIGHT - 180])
        
        # Draw preview snake
        preview_snake = Snake(DISPLAY_WIDTH/2 - 100, DISPLAY_HEIGHT - 150)
        preview_snake.direction = 'RIGHT'
        preview_snake.length = 5
        for i in range(preview_snake.length):
            preview_snake.body.append([preview_snake.x + i * SNAKE_BLOCK, preview_snake.y])
        preview_snake.draw(display)
        
        # Draw preview food
        preview_food = Food()
        preview_food.x = DISPLAY_WIDTH/2 + 50
        preview_food.y = DISPLAY_HEIGHT - 150
        preview_food.draw(display)
        
        # Draw preview special food
        preview_special = Food()
        preview_special.x = DISPLAY_WIDTH/2 + 100
        preview_special.y = DISPLAY_HEIGHT - 150
        preview_special.special = True
        preview_special.color = COLOR_SCHEMES[CURRENT_SCHEME]["special_food"]
        preview_special.draw(display)
        
        pygame.display.update()
        clock.tick(60)

# Function to show main menu
def show_main_menu(high_score):
    global CURRENT_SCHEME
    
    # Try to load saved color scheme
    try:
        with open("snake_settings.txt", "r") as f:
            saved_scheme = f.read().strip()
            if saved_scheme in COLOR_SCHEMES:
                CURRENT_SCHEME = saved_scheme
    except:
        pass  # Use default if file doesn't exist
    
    menu_running = True
    
    # Create buttons
    start_button = Button(DISPLAY_WIDTH/2 - 100, DISPLAY_HEIGHT/2 - 40, 200, 50, "START GAME", GREEN, DARK_GREEN)
    settings_button = Button(DISPLAY_WIDTH/2 - 100, DISPLAY_HEIGHT/2 + 30, 200, 50, "SETTINGS", BLUE, (30, 100, 180))
    quit_button = Button(DISPLAY_WIDTH/2 - 100, DISPLAY_HEIGHT/2 + 100, 200, 50, "QUIT", RED, (180, 0, 0))
    
    # Create demo snake for animation
    demo_snake = Snake(DISPLAY_WIDTH/2, DISPLAY_HEIGHT - 100)
    demo_snake.direction = 'RIGHT'
    demo_snake.x_change = SNAKE_BLOCK
    demo_snake.length = 10
    for i in range(demo_snake.length):
        demo_snake.body.append([demo_snake.x - i * SNAKE_BLOCK, demo_snake.y])
    
    # Animation variables
    animation_counter = 0
    
    while menu_running:
        display.fill(COLOR_SCHEMES[CURRENT_SCHEME]["background"])
        
        # Draw grid background
        draw_grid()
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Handle keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
            
            # Check button clicks
            if start_button.is_clicked(mouse_pos, event):
                return True
            if settings_button.is_clicked(mouse_pos, event):
                show_settings_menu()
                # Recreate demo snake with new color scheme
                demo_snake = Snake(DISPLAY_WIDTH/2, DISPLAY_HEIGHT - 100)
                demo_snake.direction = 'RIGHT'
                demo_snake.x_change = SNAKE_BLOCK
                demo_snake.length = 10
                for i in range(demo_snake.length):
                    demo_snake.body.append([demo_snake.x - i * SNAKE_BLOCK, demo_snake.y])
            if quit_button.is_clicked(mouse_pos, event):
                pygame.quit()
                sys.exit()
        
        # Update button hover states
        start_button.check_hover(mouse_pos)
        settings_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        # Draw title with animation
        title_color = (
            int(128 + 127 * math.sin(animation_counter * 0.05)),
            int(128 + 127 * math.sin(animation_counter * 0.05 + 2)),
            int(128 + 127 * math.sin(animation_counter * 0.05 + 4))
        )
        title_text = title_font.render("SUPER SNAKE", True, title_color)
        display.blit(title_text, [DISPLAY_WIDTH/2 - title_text.get_width()/2, 100])
        
        # Draw high score
        if high_score > 0:
            high_score_text = score_font.render(f"High Score: {high_score}", True, GOLD)
            display.blit(high_score_text, [DISPLAY_WIDTH/2 - high_score_text.get_width()/2, 180])
            
        # Display fullscreen hint
        fullscreen_text = font_style.render("Press F11 to toggle fullscreen", True, GRAY)
        display.blit(fullscreen_text, [DISPLAY_WIDTH/2 - fullscreen_text.get_width()/2, DISPLAY_HEIGHT - 30])
        
        # Draw buttons
        start_button.draw(display)
        settings_button.draw(display)
        quit_button.draw(display)
        
        # Animate demo snake
        animation_counter += 1
        if animation_counter % 5 == 0:  # Slow down animation
            # Move demo snake
            demo_snake.body.append([demo_snake.body[-1][0] + demo_snake.x_change, demo_snake.body[-1][1]])
            if len(demo_snake.body) > demo_snake.length:
                del demo_snake.body[0]
            
            # Change direction randomly
            if random.random() < 0.02:
                directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
                current_index = directions.index(demo_snake.direction) if demo_snake.direction in directions else 0
                
                # Don't allow 180-degree turns
                if demo_snake.direction == 'UP':
                    directions.remove('DOWN')
                elif demo_snake.direction == 'DOWN':
                    directions.remove('UP')
                elif demo_snake.direction == 'LEFT':
                    directions.remove('RIGHT')
                elif demo_snake.direction == 'RIGHT':
                    directions.remove('LEFT')
                
                new_direction = random.choice(directions)
                if new_direction == 'LEFT':
                    demo_snake.x_change = -SNAKE_BLOCK
                    demo_snake.y_change = 0
                elif new_direction == 'RIGHT':
                    demo_snake.x_change = SNAKE_BLOCK
                    demo_snake.y_change = 0
                elif new_direction == 'UP':
                    demo_snake.y_change = -SNAKE_BLOCK
                    demo_snake.x_change = 0
                elif new_direction == 'DOWN':
                    demo_snake.y_change = SNAKE_BLOCK
                    demo_snake.x_change = 0
                demo_snake.direction = new_direction
            
            # Keep snake on screen
            head = demo_snake.body[-1]
            if head[0] < 0:
                demo_snake.direction = 'RIGHT'
                demo_snake.x_change = SNAKE_BLOCK
                demo_snake.y_change = 0
            elif head[0] >= DISPLAY_WIDTH:
                demo_snake.direction = 'LEFT'
                demo_snake.x_change = -SNAKE_BLOCK
                demo_snake.y_change = 0
            elif head[1] < 0:
                demo_snake.direction = 'DOWN'
                demo_snake.y_change = SNAKE_BLOCK
                demo_snake.x_change = 0
            elif head[1] >= DISPLAY_HEIGHT:
                demo_snake.direction = 'UP'
                demo_snake.y_change = -SNAKE_BLOCK
                demo_snake.x_change = 0
        
        # Draw demo snake
        demo_snake.draw(display)
        
        pygame.display.update()
        clock.tick(60)
    
    return False

# Function to show game over screen
def show_game_over_screen(score, high_score):
    # Play game over sound
    if game_over_sound:
        game_over_sound.play()
    
    # Create buttons
    restart_button = Button(DISPLAY_WIDTH/2 - 100, DISPLAY_HEIGHT/2 + 50, 200, 50, "PLAY AGAIN", GREEN, DARK_GREEN)
    menu_button = Button(DISPLAY_WIDTH/2 - 100, DISPLAY_HEIGHT/2 + 120, 200, 50, "MAIN MENU", BLUE, (30, 100, 180))
    
    game_over_running = True
    
    while game_over_running:
        display.fill(COLOR_SCHEMES[CURRENT_SCHEME]["background"])
        
        # Draw grid background
        draw_grid()
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Handle keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
            
            # Check button clicks
            if restart_button.is_clicked(mouse_pos, event):
                return "restart"
            if menu_button.is_clicked(mouse_pos, event):
                return "menu"
            
            # Keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                if event.key == pygame.K_m:
                    return "menu"
        
        # Update button hover states
        restart_button.check_hover(mouse_pos)
        menu_button.check_hover(mouse_pos)
        
        # Draw game over text
        display_message("GAME OVER", RED, -120, "large")
        
        # Draw score
        display_message(f"Your Score: {score}", WHITE, -50)
        
        # Draw high score
        if score >= high_score:
            display_message("NEW HIGH SCORE!", GOLD, -10)
        else:
            display_message(f"High Score: {high_score}", WHITE, -10)
        
        # Draw buttons
        restart_button.draw(display)
        menu_button.draw(display)
        
        # Draw keyboard shortcuts
        shortcut_text1 = font_style.render("Press R to restart", True, GRAY)
        shortcut_text2 = font_style.render("Press M for menu", True, GRAY)
        display.blit(shortcut_text1, [DISPLAY_WIDTH/2 - shortcut_text1.get_width()/2, DISPLAY_HEIGHT - 60])
        display.blit(shortcut_text2, [DISPLAY_WIDTH/2 - shortcut_text2.get_width()/2, DISPLAY_HEIGHT - 30])
        
        pygame.display.update()
        clock.tick(60)
    
    return "menu"

# Main game function
def game_loop():
    # Load high score
    try:
        with open("snake_high_score.txt", "r") as f:
            high_score = int(f.read())
    except:
        high_score = 0
    
    # Show main menu
    if not show_main_menu(high_score):
        return
    
    # Game variables
    game_state = GameState.PLAYING
    score = 0
    
    # Create snake
    snake = Snake(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2)
    
    # Create food
    food = Food()
    
    # Create predators with staggered initial spawn times
    predators = [
        Eagle(),      # Eagle - follows directly
        Mongoose(),   # Mongoose - fast and erratic movement
        Hawk()        # Hawk - circles and dives
    ]
    
    # Stagger initial spawn times to increase chance of multiple predators
    predators[0].spawn_timer = random.randint(100, 300)  # Eagle appears first
    predators[1].spawn_timer = random.randint(300, 500)  # Mongoose appears second
    predators[2].spawn_timer = random.randint(500, 700)  # Hawk appears last
    
    # Create dialogue generator for predator anger levels only
    dialogue_generator = DialogueGenerator()
    
    # No dialogue timers needed
    
    # Special food variables
    special_food_active = False
    special_food = None
    
    # Game speed variables
    snake_speed = INITIAL_SPEED
    speed_increase_factor = 0.5  # How much to increase speed per food eaten
    
    # Game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # Pause game
                if event.key == pygame.K_p:
                    if game_state == GameState.PLAYING:
                        game_state = GameState.PAUSED
                    elif game_state == GameState.PAUSED:
                        game_state = GameState.PLAYING
                
                # Control snake
                if game_state == GameState.PLAYING:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        snake.change_direction('LEFT')
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        snake.change_direction('RIGHT')
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        snake.change_direction('UP')
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        snake.change_direction('DOWN')
                    elif event.key == pygame.K_SPACE:
                        # Activate speed boost with spacebar
                        snake.activate_boost()
                
                # Toggle fullscreen (F11) - available in any game state
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
        
        # Update game state
        if game_state == GameState.PLAYING:
            # Update boost status
            snake.update_boost()
            
            # Update snake dialogue
            snake.update_dialogue(dialogue_generator, predators)
            
            # Move snake
            snake.move()
            
            # Check for collisions with boundaries
            if snake.check_collision_with_boundaries():
                snake.is_dead = True
                # Mark collision point as the head (for boundary collision)
                snake.collision_point = len(snake.body) - 1
                game_state = GameState.GAME_OVER
            
            # Check for collisions with self
            if snake.check_collision_with_self():
                snake.is_dead = True
                game_state = GameState.GAME_OVER
            
            # Check for collisions with food
            if snake.check_collision_with_food(food):
                # Increase score
                if food.special:
                    score += 5
                    snake.grow(3)  # Grow more for special food
                    # Add 2 boost charges for special food
                    snake.add_boost_charge()
                    snake.add_boost_charge()
                else:
                    score += 1
                    snake.grow(1)
                    # Add 1 boost charge for regular food
                    snake.add_boost_charge()
                
                # Play eat sound
                if eat_sound:
                    eat_sound.play()
                
                # Increase speed (up to max) but slower than before
                snake_speed = min(snake_speed + speed_increase_factor * 0.5, MAX_SPEED)
                
                # Generate new food
                food.regenerate(snake.body)
                
            # Determine which predator types are available based on score
            available_predator_types = []
            available_predator_types.append(Eagle)  # Eagle always available
            
            if score > 5:  # Lower threshold for mongoose
                available_predator_types.append(Mongoose)
            
            if score > 15:  # Lower threshold for hawk
                available_predator_types.append(Hawk)
                
            # Calculate max simultaneous predators based on score
            max_simultaneous = 1
            if score > 10:
                max_simultaneous = 2
            if score > 20:
                max_simultaneous = 3  # All three can appear at once
                
            # Update predator speeds based on score
            for predator in predators:
                # Only update predators of available types
                predator_type = type(predator)
                if predator_type in available_predator_types:
                    # Increase speed based on score and anger level
                    anger_boost = (predator.anger_level - 1) * 0.5  # Each anger level adds 0.5 to speed
                    
                    if isinstance(predator, Eagle):
                        predator.speed = 2.5 + min(score / 25, 2.0) + anger_boost
                    elif isinstance(predator, Mongoose):
                        predator.speed = 3.5 + min(score / 30, 1.5) + anger_boost
                    elif isinstance(predator, Hawk):
                        predator.dive_speed = 8.0 + min(score / 20, 4.0) + (anger_boost * 2)
                    
                    # Adjust spawn timers to allow multiple predators
                    # The higher the score, the more likely multiple predators appear
                    if not predator.active and predator.spawn_timer > 0:
                        # Count active predators
                        active_count = sum(1 for p in predators if p.active)
                        
                        # If below max simultaneous, increase chance of spawning
                        if active_count < max_simultaneous:
                            # Reduce spawn timer more quickly as score increases
                            reduction_factor = 1.0 + (score / 50)  # Up to 2x faster spawning at score 50
                            predator.spawn_timer -= int(reduction_factor)
                    
                    # Update predator and check for collision with head and body
                    head_collision, body_collision = predator.update(
                        snake.body[-1] if snake.body else None, 
                        dialogue_generator,
                        snake.body
                    )
                    
                    if head_collision:
                        # If boost is active, the snake can escape the predator
                        if snake.boost_active:
                            # Predator misses the snake
                            predator.active = False
                            predator.spawn_timer = random.randint(200, 400)  # Set longer respawn time
                        else:
                            # Predator caught the snake's head - snake dies
                            snake.is_dead = True
                            # Mark collision point as the head
                            snake.collision_point = len(snake.body) - 1
                            game_state = GameState.GAME_OVER
                            
                            # Play game over sound
                            if game_over_sound:
                                game_over_sound.play()
                    
                    elif body_collision:
                        # Predator hit the snake's body - predator disappears
                        predator.active = False
                        predator.spawn_timer = random.randint(300, 500)  # Set respawn time
            
            # Update food
            if not food.update():
                # Special food expired, generate new food
                food.regenerate(snake.body)
            
            # Check for new high score
            if score > high_score:
                high_score = score
                # Save high score
                try:
                    with open("snake_high_score.txt", "w") as f:
                        f.write(str(high_score))
                except:
                    pass
        
        # Draw everything
        display.fill(COLOR_SCHEMES[CURRENT_SCHEME]["background"])
        
        # Draw grid background
        draw_grid()
        
        # Draw food
        food.draw(display)
        
        # Draw all active predators (behind snake)
        for predator in predators:
            # Draw any predator that is currently active
            if predator.active:
                predator.draw(display)
        
        # Draw snake
        snake.draw(display)
        
        # Draw score and boost charge
        display_score(score, high_score, snake.boost_charge, snake.boost_active)
        
        # Draw pause menu if paused
        if game_state == GameState.PAUSED:
            draw_pause_menu()
        
        # Show death animation and game over screen
        if game_state == GameState.GAME_OVER:
            # Run death animation for a short time before showing game over screen
            if snake.death_animation_frame < 60:  # Run animation for 60 frames (about 1 second)
                snake.death_animation_frame += 1
                
                # Shake screen effect
                shake_offset = (random.randint(-3, 3), random.randint(-3, 3)) if snake.death_animation_frame < 20 else (0, 0)
                if shake_offset != (0, 0):
                    display.blit(display.copy(), shake_offset)
            else:
                result = show_game_over_screen(score, high_score)
                if result == "restart":
                    # Reset game
                    snake = Snake(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2)
                    food = Food()
                    # Reset all predators with staggered spawn times
                    predators = [
                        Eagle(),
                        Mongoose(),
                        Hawk()
                    ]
                    
                    # Stagger initial spawn times to increase chance of multiple predators
                    predators[0].spawn_timer = random.randint(100, 300)  # Eagle appears first
                    predators[1].spawn_timer = random.randint(300, 500)  # Mongoose appears second
                    predators[2].spawn_timer = random.randint(500, 700)  # Hawk appears last
                    
                    # No dialogue timers needed
                    score = 0
                    snake_speed = INITIAL_SPEED
                    game_state = GameState.PLAYING
                    # Reset boost properties
                    snake.boost_charge = 0
                    snake.boost_active = False
                    snake.boost_timer = 0
                elif result == "menu":
                    # Return to main menu
                    return game_loop()
        
        # Update display
        pygame.display.update()
        
        # Set game speed with boost if active
        if game_state == GameState.PLAYING:
            current_speed = snake_speed * 2 if snake.boost_active else snake_speed
            clock.tick(current_speed)
        else:
            clock.tick(60)
    
    # Clean up dialogue generator when game ends
    if 'dialogue_generator' in locals():
        dialogue_generator.shutdown()

# Start the game
if __name__ == "__main__":
    while True:
        game_loop()