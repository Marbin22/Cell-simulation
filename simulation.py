import pygame  # for graphics and game functions
import random  # import random numbers
import sys  # system functions
import math  # import math operations

# set up pygame
pygame.init()  # start pygame
width, height = 800, 600  # pygame window size
screen = pygame.display.set_mode((width, height))  # create the window
pygame.display.set_caption("Cell: Osmosis + Apoptosis")  #title

white = (255, 255, 255)  # background
black = (0, 0, 0)  # text
blue = (0, 0, 255)  # water 
red = (255, 0, 0)  # solutes 
green = (0, 255, 0)  # healthy cell border/wall
dark_green = (0, 100, 0)  # dead cell
gray = (200, 200, 200)  # button color

#again button
button_rect = pygame.Rect(width//2 - 50, height - 50, 100, 40)  # button position and size
button_font = pygame.font.SysFont('Arial', 20)  # buttonstyle 
button_text = button_font.render("retry", True, black)  # button text

cell_radius = 100  # starting cell size
cell_x, cell_y = width//2, height//2  # center position
cell_health = 200  # cells starting health

particles = []  # particles inside cell
env_particles = []  # particles outside cell
fragments = []  # cell fragments when dying
apoptosis_triggered = False  # track if the cell is dying

def reset_simulation():
    global particles, env_particles, fragments, apoptosis_triggered, cell_radius, cell_health
    
    # clear all existing particles
    particles.clear()
    env_particles.clear()
    fragments.clear()
    
    # reset the cells properties
    cell_radius = 100
    cell_health = 200
    apoptosis_triggered = False
    
    # create particles inside cell
    for _ in range(50):
        is_water = random.random() < 0.7  # 70% chance to have water
        radius = 5 if is_water else 8  # make the water is smaller than solute
        particles.append([
            random.randint(int(cell_x - cell_radius + 20), int(cell_x + cell_radius - 20)),  # x position
            random.randint(int(cell_y - cell_radius + 20), int(cell_y + cell_radius - 20)),  # y position
            radius,  # size
            random.uniform(-1, 1),  # x movement speed
            random.uniform(-1, 1),  # y movement speed
            is_water  # determine if its water or solute
        ])
    
    # create floating water particles outside of the cell
    for _ in range(30):
        while True:
            x = random.randint(50, width - 50)  # random x position
            y = random.randint(50, height - 50)  # random y position
            # this makes sure water particle spawns outside cell
            if math.sqrt((x - cell_x)**2 + (y - cell_y)**2) > cell_radius + 20:
                env_particles.append([x, y, 5, random.uniform(-1, 1), random.uniform(-1, 1), True])
                break

# start the simulation
reset_simulation()

# set up game clock with font
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20)

def draw_text(text, x, y, color=black):
    # function to draw text on screen
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# main game loop
running = True
while running:
    screen.fill(white)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # if window closed
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:  # if mouse clicked
            if apoptosis_triggered and button_rect.collidepoint(event.pos):  # if clicked retry 
                reset_simulation()
    
    # draw cell 
    border_color = dark_green if apoptosis_triggered else green
    pygame.draw.circle(screen, border_color, (cell_x, cell_y), int(cell_radius), 4)
    
    # track the particles inside of the cell
    water_inside = 0
    solute_inside = 0
    
    # update particles inside cell
    for p in particles[:]:
        # move particles
        p[0] += p[3]
        p[1] += p[4]
        
        # create the cells boundries 
        if not apoptosis_triggered:
            distance = math.sqrt((p[0] - cell_x)**2 + (p[1] - cell_y)**2)
            if distance + p[2] > cell_radius:
                if p[5]:  # if its water, let it escape
                    env_particles.append(p.copy())
                    particles.remove(p)
                    continue
                else:  # if its a solute, bounce back/block
                    p[3] *= -0.5
                    p[4] *= -0.5
        
        # counts water and solute particles
        if p[5]: water_inside += 1
        else: solute_inside += 1
        pygame.draw.circle(screen, blue if p[5] else red, (int(p[0]), int(p[1])), p[2])
    
    # updates the particles outside cell
    for p in env_particles[:]:
        # move particle
        p[0] += p[3]
        p[1] += p[4]
        
        # bounces particles off screen edges
        if p[0] <= 0 or p[0] >= width: p[3] *= -1
        if p[1] <= 0 or p[1] >= height: p[4] *= -1
        
        # allows water to enter cell
        if p[5] and not apoptosis_triggered:
            distance = math.sqrt((p[0] - cell_x)**2 + (p[1] - cell_y)**2)
            if distance < cell_radius + 20 and random.random() < 0.02:
                particles.append(p.copy())
                env_particles.remove(p)
                continue
        
        pygame.draw.circle(screen, blue, (int(p[0]), int(p[1])), p[2])
    
    # Demonstrates the osmosis effect
    if not apoptosis_triggered:
        osmotic_balance = water_inside - (solute_inside * 2) # calculate water balance
        # change cell size based on water balance
        cell_radius += osmotic_balance * 0.01
        cell_radius = max(50, min(150, cell_radius))
        # change cell health
        cell_health += osmotic_balance * 0.02
        cell_health = max(0, min(200, cell_health))
        if cell_health <= 0:
            apoptosis_triggered = True # trigger cell death if health reaches 0
    
    if apoptosis_triggered and cell_radius > 10: # handle cell death animation
        cell_radius -= 0.5  # shrink cell
        if random.random() < 0.1:  # randomly create fragments (bigger red dots)
            fragments.append([
                cell_x + random.randint(-50, 50),
                cell_y + random.randint(-50, 50),
                random.randint(5, 15)
            ])
    
    # draw cell fragments
    for frag in fragments:
        pygame.draw.circle(screen, red, (frag[0], frag[1]), frag[2])
    
    # display stats
    draw_text(f"water: {water_inside}", 10, 10)
    draw_text(f"solute: {solute_inside}", 10, 30)
    draw_text(f"health: {int(cell_health)}", 10, 50)
    
    # display status messages
    if apoptosis_triggered:
        draw_text("cell death triggered!", 10, 70, red)
        #retry button
        pygame.draw.rect(screen, gray, button_rect)
        pygame.draw.rect(screen, black, button_rect, 2)
        screen.blit(button_text, (button_rect.x + 30, button_rect.y + 10))
    else:
        status = "normal"
        if water_inside > solute_inside * 1.5: status = "swelling (water entering)"
        elif solute_inside > water_inside * 1.5: status = "shrinking (water exiting)"
        draw_text(f"status: {status}", 10, 70, black)
    
    pygame.display.flip()  
    clock.tick(60)  # maintains 60 fps

pygame.quit()  # end pygame
sys.exit()  # close program