# Snake on SenseHat
#
# Simple snake game using pygame, running in Raspberry Pi + SenseHat
# Using SenseHat joystick to control movement
 
import pygame
from random import randint
from sense_hat import SenseHat, ACTION_PRESSED
 
sense = SenseHat()
 
# Screen size and layout
GAMESPEED = 20                      # overall game speed; 30 = 1 fps, 10 = 3 fps
WIN_LENGTH = 10                     # reaching WIN_LENGTH means winning the game
RANGEX, RANGEY = 8,8                # SenseHat grid size in cells
CELLSIZE = 50                       # pygame graphics cell size in pixels
WALLSIZE = 2                        # padding between grid cells
 
# Colours
COLOR_BACK  = (30, 30, 30)          # sensehat needs darker background than computer screen
COLOR_SNAKE = (0,150,250)
COLOR_FOOD  = (250,150,150)
COLOR_MSG   = (255,200,200)     
 
# End game, stop moving, show message on pygame screen
# Show :) or :( on SenseHat 
def end_game(mode, message):
    global game_status
    game_status = mode
    font = pygame.font.Font(pygame.font.get_default_font(), 32)
    text = font.render(message, True, COLOR_MSG)
    screen.blit(text, (((CELLSIZE * RANGEX) - text.get_width()) // 2, CELLSIZE + 5) )
    pygame.display.flip()
    sense.show_message(":( :(" if mode == 1 else ":) :)", scroll_speed = 0.1)
     
# Draw things on screen and SenseHat
def draw_something(location):
    c = COLOR_BACK
    if location == food:      
        c = COLOR_FOOD
    elif location in snake:
        c = COLOR_SNAKE
    pygame.draw.rect(screen, c, (CELLSIZE * location[0] + WALLSIZE, CELLSIZE * location[1] + WALLSIZE, CELLSIZE - 2*WALLSIZE, CELLSIZE - 2*WALLSIZE))
    # set_pixel throws error at bad coordinates, pygame.draw.() does not
    if (0 <= location[0] < RANGEX and 0 <= location[1] < RANGEY): 
        sense.set_pixel(location[0], location[1], c)
 
# Create new food, check that it's outside of snake, draw it
def place_food():
    global food
    food = snake[0]
    while(food in snake):
        food = [randint(0, RANGEX-1), randint(0, RANGEY-1)]
    draw_something(food)
 
 
##### MAIN LOOP #####
 
done = False    # becomes True when player manually closes game from main window
skip = False    # becomes True when player pauses game with K_SPACE
tick = 0        # ticker for controlling game speed
game_status = 0 # 0 - game in progress, 1 - player lost, 2 - player won
 
food = []       # food location, list of [x,y]
dirx, diry = 0,0 # current moving direction
 
# Graphics init
pygame.init()                                  
screen = pygame.display.set_mode((RANGEX*CELLSIZE, RANGEY*CELLSIZE))
pygame.display.set_caption("Snake")      
screen.fill(COLOR_BACK)
clock = pygame.time.Clock()                    
 
sense.set_pixels([COLOR_BACK]*(RANGEX*RANGEY)) # set sensehat display to background color
 
# Create and draw snake, create first food
snake = [[0,2], [0,1], [0,0]] # head first!
for s in snake:
    draw_something(s)
place_food()
pygame.display.flip()
 
while not done:
    clock.tick(30)
 
    # Get & process user input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: skip = not skip
           
    # read SenseHat joystick, process only down pressed events
    for event in sense.stick.get_events():
        if event.action == ACTION_PRESSED:
            if event.direction == "down":   dirx, diry = 0, 1
            if event.direction == "up":     dirx, diry = 0, -1
            if event.direction == "left":   dirx, diry = -1, 0
            if event.direction == "right":  dirx, diry = 1, 0
 
    tick = (tick + 1) % GAMESPEED               # to speed game up / down
    if skip or game_status != 0 or tick != 0 or (dirx == 0 and diry == 0):   # game stopped or finished, or "dummy tick", or no movement defined
        continue
 
    x = snake[0][0] + dirx      # move snake: add new segment in moving direction
    y = snake[0][1] + diry
    if [x,y] in snake:
        end_game(1, "You hit self :(")
    if x<0 or y<0 or x>=RANGEX or y>=RANGEY:
        end_game(1, "Wall crash :(")
    snake.insert(0,[x,y])      
 
    if [x,y] == food:           # if snake reached apple, create another apple elsewhere. current apple will get drawn over by snake
        place_food()
    else:
        x1, y1 = snake.pop()    # no apple => delete last snake segment
        draw_something([x1, y1])
    draw_something([x, y])
 
    pygame.display.set_caption("Snake length: " + str(len(snake)) + " / " + str(WIN_LENGTH))
    if len(snake) >= WIN_LENGTH:
        end_game(2, "You win!!! :)")
 
    pygame.display.flip()
 
pygame.quit()
