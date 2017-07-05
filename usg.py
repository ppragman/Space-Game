#this is the main "run loop" for untitled space game!
#Patrick Pragman and Alex Rybicki
#6/1/2017

import math
import pygame #obviously, import the pygame library
pygame.init() #fire that badboy up!

#let's define some convenient colors
#these are globals, probably should come up with a better way to abstract
#this later, but whatever

BLACK = (0,0,0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (211,211,211)
YELLOW = (255,255,0)

#make a pygame window
def make_window(size, caption):

    screen = pygame.display.set_mode(size)
    #screen = pygame.display.set_mode((640,480),pygame.FULLSCREEN)

    pygame.display.set_caption(caption)

    return screen


class Bullet(pygame.sprite.Sprite):
    #this is the bullet class

    ammo_colors = {"dumb_lead":GRAY, "laser": GREEN, "tracer":YELLOW}
    ammo_velocities = {"dumb_lead":5, "laser": 7, "tracer":5}
    reload_time = {"dumb_lead":2, "laser": 20, "tracer":2}

    def __init__(self, type_of, x,y,theta):
        #self.shot_from = shot_from #this is so your bullets don't impact yourself as you shoot them
        self.type_of = type_of
        
        super().__init__()

        self.x = x
        self.y = y
        self.theta = theta

        av = Bullet.ammo_velocities[type_of]

        self.dx, self.dy = av*math.sin(self.theta), av*math.cos(self.theta)

        self.image = pygame.Surface([abs(self.dx), abs(self.dy)])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)

        pygame.draw.line(self.image, Bullet.ammo_colors[type_of], (self.x, self.y), (self.dx, self.dy), 2)




    def physics_update(self):
        self.x += self.dx
        self.y += self.dy


    def render(self):
        #self.rect = self.image.get_rect(center=self.rect.center)    
        pass
    
    def update(self):
        self.physics_update()
        self.render()
        

        

class Spacecraft(pygame.sprite.Sprite):
    #this is the spacecraft class
    #it holds it's location (in the world map, not in the window), and it's type
    #spacecraft class also holds it's HP

    #these are the types of ships, they're hard coded in
    #I know we could probably look into the folder and populate
    #a dict with this info, and maybe at some point we will, but
    #for now that seems like overkill.
    sprite_path = {"fighter":"sprite\PNG\Sprites\Ships\spaceShips_001.png",
                       "interceptor":"sprite\PNG\Sprites\Ships\spaceShips_002.png",
                       "light_shuttle":"sprite\PNG\Sprites\Ships\spaceShips_003.png",
                       "station_defense":"sprite\PNG\Sprites\Ships\spaceShips_004.png"}
    #obviously, don't be a dick and add more of these

    
                       
    #initialize the spacecraft
    def __init__(self, x,y, heading, ship_type, player):

        #first we'll call the parent class (Sprite) constructor
        super().__init__() #Why?  Who the fuck knows - learn this!
        
        self.ship_type = ship_type #this is the type of ship
        self.player = player #this is whether the player is flying the ship or not - it's a boolean
        self.exploding = False #uhh, we've just initialized this one, obviously we're not exploding
        
        #load up the image
        path = Spacecraft.sprite_path[self.ship_type]


        self.reference = pygame.image.load(path).convert_alpha() #this is the main image reference


        #health points
        self.hp = 100 #this is given in percent for now, I'll figure out some better system later
        

        #maxes
        self.max_angular_velocity = .1 #this is in radians - be cautious
        self.max_thrust = 1/1000
        self.max_v = .1



        #state vectors
        self.acceleration = 0
        self.velocity = 0,0
        self.angular_velocity = 0
        self.theta = math.pi/2 #this is the heading of the craft
        self.position = x,y #eventually we'll need to adjust this to hold the playership at the center then move everything around it

        self.x, self.y = x,y

        #scale the thing to a manageable size
        self.size = self.reference.get_size()        
        self.scale = .3 #scale factor for the sprites - these things are huge if you don't adjust this
        self.reference = pygame.transform.scale(self.reference, (int(self.size[0]*self.scale), int(self.size[1]*self.scale)))

        #AI stuff
        self.ai_rotate_retrograde = False
        self.target = self.theta

        #bullet list
        self.bullet_list = []

        #controls logic - this goes to the controls class and builds a control model
        #with just the player's ship this won't do much, but AI can control this too ideally

        #these are the control mappings
        self.LEFT = pygame.K_LEFT
        self.RIGHT = pygame.K_RIGHT
        self.UP = pygame.K_UP
        self.DOWN = pygame.K_DOWN
        self.FIRE = pygame.K_SPACE

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.fire_pressed = False

        
        self.image = self.reference #ok make our image our reference now


        #let's get the rect that has the dimension of the image
        self.rect = self.reference.get_rect()


        self.rect.x, self.rect.y = self.position #this sticks it out the "location" - i'll need to adjust this later so that it's on the "world map" relative to the user screen.

        
    def autopilot(self):
        #the reverse course autopilot
        if self.ai_rotate_retrograde:


            #get target heading
            vx, vy = self.velocity 

            #target heading is equal to the tan inverse of the velocity - pi/2 radians
            self.target = math.atan2(vx,vy)-math.pi

            


            
            #reverse heading information
            hdg = self.theta
            tgt = self.target
            
            if tgt < 0:
                tgt += 2*math.pi


            dif = abs(hdg - tgt)    

            if dif >= (3*self.max_angular_velocity):
                #if you're not close, then find the shortest direction to turn
                #then turn to it
                self.angular_velocity = self.max_angular_velocity
                    
            if dif < (3*self.max_angular_velocity):
                self.angular_velocity = 0
                self.theta = tgt
                self.ai_rotate_retrograde = False


    def physics_update(self):
        #update the bullets
        if len(self.bullet_list)>0:
            for bullet in self.bullet_list:
                bullet.update()
        
        self.theta += self.angular_velocity #this points the craft one way or another

        a = self.acceleration

        dv = a*math.sin(self.theta), a*math.cos(self.theta)

        self.dx, self.dy = self.velocity
            
        self.velocity = tuple(v+a for v,a in zip(self.velocity, dv))
        self.position = tuple(p+v for p,v in zip(self.position, self.velocity))



        #this changes the heading of the ship, then adjust the image as appropriate
        if self.theta >= 2*math.pi:
            self.theta = self.theta - 2*math.pi

        if self.theta < 0:
            self.theta = self.theta + 2*math.pi


    def control_input(self):
        
        if self.left_pressed:
            self.angular_velocity = self.max_angular_velocity

        if self.right_pressed:
            self.angular_velocity = -self.max_angular_velocity

        if self.right_pressed == False and self.left_pressed == False and self.down_pressed == False:
            self.angular_velocity = 0
        


        if self.up_pressed:
            self.acceleration += self.max_thrust
            
        elif self.up_pressed == False:
            self.acceleration = 0
        
            
            
        if self.down_pressed:
            self.ai_rotate_retrograde = True


        if self.fire_pressed:
            x = self.x
            y = self.y
            t = self.theta 
            self.bullet_list.append(Bullet("laser",x,y,t))



        if self.player:

            pressed = pygame.key.get_pressed()

            if pressed[self.LEFT]:
                self.left_pressed = True
            else:
                self.left_pressed = False

            if pressed[self.RIGHT]:
                self.right_pressed = True
            else:
                self.right_pressed = False

            if pressed[self.UP]:
                self.up_pressed = True
            else:
                self.up_pressed = False

            if pressed[self.DOWN]:
                self.down_pressed = True
            else:
                self.down_pressed = False

            if pressed[self.FIRE]:
                self.fire_pressed = True
            else:
                self.fire_pressed = False
                

    
    def render(self):

        #this scales the rect a bit so that it's it's not so janky when you rotate
        self.rect.w, self.rect.h = self.size[0] + (self.scale * 5), self.size[1] + (self.scale*5)

        x,y = self.position
        x = x - self.rect.w/2
        y = y - self.rect.h/2
            
        self.rect.x, self.rect.y = x,y
        self.x, self.y = x,y
        
        
        self.image = pygame.transform.rotate(self.reference, math.degrees(self.theta))
        self.rect = self.image.get_rect(center=self.rect.center)    


    def update(self):
        #this method queries the AI for updates
        #the AI updates the controls
        #the controls update the physics
        #the physics updates the world
        #then any changes get rendered
        

        self.autopilot()
        self.control_input()
        self.physics_update()
        self.render()
                
        
                
 

class Planet(pygame.sprite.Sprite):
    pass

class Spacestation(pygame.sprite.Sprite):
    pass


    

def main():

    intro()

    gameplay()

    credit_scroll()

    

def intro():
    pass


        

def gameplay():

    screen_size = (700, 500)
    main_window = make_window(screen_size, "Untitled Space Game")
    
    running = True #this bool runs the main while loop

    clock = pygame.time.Clock() # this controls the screen update speed

    player_ship = Spacecraft(350, 250, 360, "light_shuttle", True)
    ship_two = Spacecraft(100,100,0, "fighter", False)


    

    #these two vars hold lists of the foreground and background sprites
    #the background sprites contain the world, the foreground sprites contain spaceships that can fight
    background_sprites = pygame.sprite.Group()
    bullet_layer = pygame.sprite.Group()
    foreground_sprites = pygame.sprite.Group()

    #add sprites to the list
    foreground_sprites.add(player_ship)
    foreground_sprites.add(ship_two)




    while running:
        #the magic happens in here

        for event in pygame.event.get(): #this looks for user input
            if event.type == pygame.QUIT: #this is if the user clicks close
                print('Exiting Pygame')
                running = False

            
        
        #logic for the game goes in here
        background_sprites.update()
        bullet_layer.update()
        foreground_sprites.update()


        #update the player ship
        player_ship.update()

        #then drawing code
        main_window.fill(BLACK)
        
        
        foreground_sprites.draw(main_window)



        #debug vectors
        debug_x, debug_y = player_ship.position
        debug_vx, debug_vy = player_ship.velocity
        
        hdg = debug_x+20*math.sin(player_ship.theta), debug_y+20*math.cos(player_ship.theta)
        tgt = debug_x+20*math.sin(player_ship.target), debug_y+20*math.cos(player_ship.target)
        pygame.draw.line(main_window, BLUE, (debug_x, debug_y), hdg, 3)
        pygame.draw.line(main_window, GREEN, (debug_x, debug_y), tgt, 3)
        pygame.draw.line(main_window, RED, (debug_x, debug_y), (debug_x+20*debug_vx, debug_y+20*debug_vy),3)
        
        
        

        #update the screen
        pygame.display.flip()

        #limit to 60 fps
        clock.tick(60)



def credit_scroll():
    pass



main()

#code to kill pygame
pygame.quit()

