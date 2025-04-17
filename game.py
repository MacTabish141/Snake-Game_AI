import pygame
import random
from enum import Enum
from collections import namedtuple
from pygame.math import Vector2
import numpy as np

pygame.init()
font = pygame.font.Font(None, 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
GRASS_COLOR = (34, 139, 34)

BLOCK_SIZE = 20
SPEED = 40

class SnakeGameAI:
    
    def __init__(self, w=800, h=800):
        self.w = w
        self.h = h
        self.cell_num = self.w // BLOCK_SIZE
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()
        
        # Load graphics
        self.load_graphics()
        
    def load_graphics(self):
        # You would need to provide these graphics or create simple versions
        try:
            # Snake head sprites
            self.head_up = pygame.image.load('Graphics/head_up.png').convert_alpha()
            self.head_down = pygame.image.load('Graphics/head_down.png').convert_alpha()
            self.head_right = pygame.image.load('Graphics/head_right.png').convert_alpha()
            self.head_left = pygame.image.load('Graphics/head_left.png').convert_alpha()
            
            # Snake tail sprites
            self.tail_up = pygame.image.load('Graphics/tail_up.png').convert_alpha()
            self.tail_down = pygame.image.load('Graphics/tail_down.png').convert_alpha()
            self.tail_right = pygame.image.load('Graphics/tail_right.png').convert_alpha()
            self.tail_left = pygame.image.load('Graphics/tail_left.png').convert_alpha()
            
            # Snake body sprites
            self.body_vertical = pygame.image.load('Graphics/body_vertical.png').convert_alpha()
            self.body_horizontal = pygame.image.load('Graphics/body_horizontal.png').convert_alpha()
            self.body_tr = pygame.image.load('Graphics/body_tr.png').convert_alpha()
            self.body_tl = pygame.image.load('Graphics/body_tl.png').convert_alpha()
            self.body_br = pygame.image.load('Graphics/body_br.png').convert_alpha()
            self.body_bl = pygame.image.load('Graphics/body_bl.png').convert_alpha()
            
            # Fruit sprite
            self.fruit_image = pygame.image.load('Graphics/frt.png').convert_alpha()
            
            self.has_graphics = True
        except:
            print("Graphics files not found, using simple shapes instead")
            self.has_graphics = False
    
    def reset(self):
        # init game state
        self.direction = Direction.RIGHT
        self.game_over = False

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        
    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE 
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
        
    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move(action)
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score
            
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        
        # 6. return game over and score
        return reward, game_over, self.score
    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x >= self.w or pt.x < 0 or pt.y >= self.h or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True
        
        return False
    
    def _update_ui(self):
        self.display.fill(GREEN)
        
        # Draw grass pattern
        self._draw_grass()
        
        # Draw snake with sprites if available
        if self.has_graphics:
            self._draw_snake_with_sprites()
        else:
            # Fallback to original drawing method
            self._draw_snake_simple()
        
        # Draw food with sprite if available
        if self.has_graphics:
            fruit_rect = pygame.Rect(self.food.x - 5, self.food.y - 5, BLOCK_SIZE, BLOCK_SIZE)
            self.display.blit(self.fruit_image, fruit_rect)
        else:
            # Fallback to original food drawing
            pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw score
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
    
    def _draw_grass(self):
        for row in range(self.cell_num):
            if row % 2 == 0:
                for col in range(self.cell_num):
                    if col % 2 == 0:
                        grass_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                        pygame.draw.rect(self.display, GRASS_COLOR, grass_rect)
            else:
                for col in range(self.cell_num):
                    if col % 2 != 0:
                        grass_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                        pygame.draw.rect(self.display, GRASS_COLOR, grass_rect)
    
    def _draw_snake_simple(self):
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
    
    def _draw_snake_with_sprites(self):
        # Update head graphics direction
        self._update_head_graphics()
        
        # Update tail graphics direction
        self._update_tail_graphics()
        
        for index, block in enumerate(self.snake):
            x_pos = block.x
            y_pos = block.y
            block_rect = pygame.Rect(x_pos, y_pos, BLOCK_SIZE, BLOCK_SIZE)
            
            if index == 0:
                # Draw head
                self.display.blit(self.head_sprite, block_rect)
            elif index == len(self.snake) - 1:
                # Draw tail
                self.display.blit(self.tail_sprite, block_rect)
            else:
                # Calculate which body part to use based on neighboring segments
                prev_block = self.snake[index + 1]
                next_block = self.snake[index - 1]
                
                # Convert to vectors for easier calculations
                current = Vector2(block.x, block.y)
                previous = Vector2(prev_block.x, prev_block.y)
                next_pos = Vector2(next_block.x, next_block.y)
                
                previous_direction = previous - current
                next_direction = next_pos - current
                
                if previous_direction.x == next_direction.x:
                    # Vertical body segment
                    self.display.blit(self.body_vertical, block_rect)
                elif previous_direction.y == next_direction.y:
                    # Horizontal body segment
                    self.display.blit(self.body_horizontal, block_rect)
                else:
                    # Corner body segment
                    if (previous_direction.x == -BLOCK_SIZE and next_direction.y == -BLOCK_SIZE) or \
                       (previous_direction.y == -BLOCK_SIZE and next_direction.x == -BLOCK_SIZE):
                        self.display.blit(self.body_tl, block_rect)
                    elif (previous_direction.x == -BLOCK_SIZE and next_direction.y == BLOCK_SIZE) or \
                         (previous_direction.y == BLOCK_SIZE and next_direction.x == -BLOCK_SIZE):
                        self.display.blit(self.body_bl, block_rect)
                    elif (previous_direction.x == BLOCK_SIZE and next_direction.y == -BLOCK_SIZE) or \
                         (previous_direction.y == -BLOCK_SIZE and next_direction.x == BLOCK_SIZE):
                        self.display.blit(self.body_tr, block_rect)
                    elif (previous_direction.x == BLOCK_SIZE and next_direction.y == BLOCK_SIZE) or \
                         (previous_direction.y == BLOCK_SIZE and next_direction.x == BLOCK_SIZE):
                        self.display.blit(self.body_br, block_rect)
    
    def _update_head_graphics(self):
        if len(self.snake) >= 2:
            head_relation_x = self.snake[0].x - self.snake[1].x
            head_relation_y = self.snake[0].y - self.snake[1].y
            
            if head_relation_x == BLOCK_SIZE:
                self.head_sprite = self.head_right
            elif head_relation_x == -BLOCK_SIZE:
                self.head_sprite = self.head_left
            elif head_relation_y == BLOCK_SIZE:
                self.head_sprite = self.head_down
            elif head_relation_y == -BLOCK_SIZE:
                self.head_sprite = self.head_up
            else:
                # Default
                self.head_sprite = self.head_right
        else:
            # Default if snake is too short
            self.head_sprite = self.head_right
    
    def _update_tail_graphics(self):
        if len(self.snake) >= 2:
            tail_idx = len(self.snake) - 1
            before_tail_idx = len(self.snake) - 2
            
            tail_relation_x = self.snake[before_tail_idx].x - self.snake[tail_idx].x
            tail_relation_y = self.snake[before_tail_idx].y - self.snake[tail_idx].y
            
            if tail_relation_x == BLOCK_SIZE:
                self.tail_sprite = self.tail_left
            elif tail_relation_x == -BLOCK_SIZE:
                self.tail_sprite = self.tail_right
            elif tail_relation_y == BLOCK_SIZE:
                self.tail_sprite = self.tail_up
            elif tail_relation_y == -BLOCK_SIZE:
                self.tail_sprite = self.tail_down
            else:
                # Default
                self.tail_sprite = self.tail_left
        else:
            # Default if snake is too short
            self.tail_sprite = self.tail_left
        
    def _move(self, action):
        #[straight, left, right]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)
        
        if np.array_equal(action, [1,0,0]):
            new_dir = clock_wise[idx] 
        elif np.array_equal(action, [0,1,0]):
            next_idx = (idx + 1) % 4 
            new_dir = clock_wise[next_idx]
        else:
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] 
        
        self.direction = new_dir
        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)