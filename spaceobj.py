import pygame
import math
import time
from random import randint
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

class Resolution:
    w = 700
    h = 500

class Over_World_Size:
    width = Resolution.w*6
    height = Resolution.h*6

class Planet(pygame.sprite.Sprite):

    sprite_path = {"city":"planets\City1.png",
                       "ice":"planets\Ice1.png",
                       "lava":"planets\Lava1.png",
                       "terran":"planets\Terran1.png"}
    
    def __init__(self, x,y,type_of, camera):
        super().__init__()

        self.star = False

        self.camera = camera
        self.type_of = type_of
        self.x = x
        self.y = y

        path = Planet.sprite_path[self.type_of]

        #this loads a reference prototype
        self.image_reference = pygame.image.load(path).convert_alpha()
        self.size = self.image_reference.get_size()
        self.scale = .05
        self.image_reference = pygame.transform.scale(self.image_reference, (int(self.size[0]*self.scale), int(self.size[1]*self.scale)))

        self.image = self.image_reference
        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y

    def render(self):

        camera = self.camera
                
        #this method renders the sprite objects
        global_x = self.x
        global_y = self.y
        
        center_x = Resolution.w/2
        center_y = Resolution.h/2

        #sprite offset
        offset_x = self.rect.w/2
        offset_y = self.rect.h/2
        
        local_0_x = camera.state_vector.x
        local_0_y = camera.state_vector.y


        local_x = global_x - local_0_x - offset_x + center_x
        local_y = global_y - local_0_y - offset_y + center_y

            
        self.rect.x = local_x
        self.rect.y = local_y   
        
        

class Star(pygame.sprite.Sprite):

    def __init__(self, camera):
        self.star = True
        
        mag = randint(1,14)
        self.x = randint(-3*Resolution.w, 3*Resolution.w)
        self.y = randint(-3*Resolution.h, 3*Resolution.h)

        super().__init__()

        self.camera = camera

        self.image = pygame.Surface([10, 10])
        self.image.fill(Color.BLACK)
        self.image.set_colorkey(Color.BLACK)
        pygame.draw.rect(self.image, (255-mag, 255 - mag, 255 - mag), [0,0, 2,2])

        self.rect = self.image.get_rect()    

        self.rect.x = self.x
        self.rect.y = self.y

    def render(self):

        camera = self.camera
                
        #this method renders the sprite objects
        global_x = self.x
        global_y = self.y
        
        center_x = Resolution.w/2
        center_y = Resolution.h/2

        #sprite offset
        offset_x = self.rect.w/2
        offset_y = self.rect.h/2
        
        local_0_x = camera.state_vector.x
        local_0_y = camera.state_vector.y


        local_x = global_x - local_0_x - offset_x + center_x
        local_y = global_y - local_0_y - offset_y + center_y

            
        self.rect.x = local_x
        self.rect.y = local_y
      
        

#make a pygame window
def make_window(size, caption):

    screen = pygame.display.set_mode(size)
    #screen = pygame.display.set_mode((640,480),pygame.FULLSCREEN)

    pygame.display.set_caption(caption)

    return screen

class Camera:
    def __init__(self,ship):
        self.ship = ship


class Color:
    BLACK = (0,0,0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GRAY = (211,211,211)
    YELLOW = (255,255,0)
    ORANGE = (215,135,0)



class Player_Controls:

    def __init__(self):
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

class Sounds:
    explosion = pygame.mixer.Sound("sounds\explode.wav")
    fire_sound = pygame.mixer.Sound("sounds\laser.wav")


class Explosion(pygame.sprite.Sprite):

    def __init__(self, x,y, source):

        
        super().__init__()

        self.source = source
        self.camera = source.camera



        self.x = x
        self.y = y

        self.seed = randint(0,5)
        self.clock = 0
        self.scale = 0


        self.fade = False

        self.theta = math.radians(randint(0,360))
        v = randint(0,3)
        r = randint(1,3)

        self.dx = round(v*math.sin(self.theta),2)
        self.dy = round(v*math.cos(self.theta),2)

        self.image_reference = pygame.Surface([50, 50])
        self.image_reference.fill(Color.BLACK)
        self.image_reference.set_colorkey(Color.BLACK)
        for i in range(0,self.seed):
            offset_x = 0#randint(-4,4)
            offset_y = 0#randint(-4,4)
            color = (255,randint(95,175),0)
            pygame.draw.circle(self.image_reference, color, (25+offset_x,25+offset_y), 2**r)
        

        self.rect = self.image_reference.get_rect()    
        self.size = self.image_reference.get_size()
        
        self.image = self.image_reference
        self.rect.x = self.x
        self.rect.y = self.y

    def physics(self):

        self.x += self.dx
        self.y += self.dy

        self.theta += math.radians(self.seed)

        self.clock += 1

        
        if self.clock >= self.seed:
            if not self.source.health.exploding:
                self.fade = True

    def render(self):

        Sounds.explosion.play()

        camera = self.camera
                
        #this method renders the sprite objects
        global_x = self.x
        global_y = self.y
        
        center_x = Resolution.w/2
        center_y = Resolution.h/2

        #sprite offset
        offset_x = self.rect.w/2
        offset_y = self.rect.h/2
        
        local_0_x = camera.state_vector.x
        local_0_y = camera.state_vector.y


        local_x = global_x - local_0_x - offset_x + center_x
        local_y = global_y - local_0_y - offset_y + center_y

        self.scale += .1

        self.image = pygame.transform.scale(self.image_reference, (int(self.size[0]*self.scale), int(self.size[1]*self.scale)))

        self.rect.x = local_x
        self.rect.y = local_y
        

class Damage(pygame.sprite.Sprite):

    def __init__(self, x,y, source):
        super().__init__()

        self.camera = source.camera

        self.clock = 0

        self.x = x
        self.y = y

        self.seed = randint(0,10)

        self.fade = False

        self.theta = math.radians(randint(0,360))
        v = randint(0,3)

        self.dx = round(v*math.sin(self.theta),2)
        self.dy = round(v*math.cos(self.theta),2)

        self.image = pygame.Surface([10, 10])
        self.image.fill(Color.BLACK)
        self.image.set_colorkey(Color.BLACK)
        pygame.draw.rect(self.image, Color.YELLOW, [0,0, 1,5])

        self.image = pygame.transform.rotate(self.image, math.degrees(self.theta))
        self.rect = self.image.get_rect()    

        self.rect.x = self.x
        self.rect.y = self.y
        
    def physics(self):

        self.x += self.dx
        self.y += self.dy

        self.clock += 1

        
        
        if self.clock >= self.seed:
            self.fade = True

    def render(self):

        camera = self.camera
                
        #this method renders the sprite objects
        global_x = self.x
        global_y = self.y
        
        center_x = Resolution.w/2
        center_y = Resolution.h/2

        #sprite offset
        offset_x = self.rect.w/2
        offset_y = self.rect.h/2
        
        local_0_x = camera.state_vector.x
        local_0_y = camera.state_vector.y


        local_x = global_x - local_0_x - offset_x + center_x
        local_y = global_y - local_0_y - offset_y + center_y

            
        self.rect.x = local_x
        self.rect.y = local_y


class Bullet(pygame.sprite.Sprite):
    #this is the bullet class

    ammo_colors = {"dumb_lead":Color.GRAY, "laser": Color.GREEN, "tracer":Color.YELLOW, "sparks":Color.YELLOW}
    ammo_velocities = {"dumb_lead":10, "laser": 7, "tracer":5, "sparks":2}
    ammo_dp = {"dumb_lead":1, "laser": 1, "tracer":.001, "sparks":0}

    def __init__(self, type_of, source):
        #self.shot_from = shot_from #this is so your bullets don't impact yourself as you shoot them
        self.type_of = type_of
        
        super().__init__()
        self.source = source

        self.clock = 0

        self.dp = Bullet.ammo_dp[type_of]

        self.kill_me = False

        self.x = source.state_vector.x
        self.y = source.state_vector.y
        self.dx = source.state_vector.dx
        self.dy = source.state_vector.dy
        self.theta = source.state_vector.theta

        self.bullet_haze = min(randint(5,10),10)/10

        more_haze = math.radians(randint(-10,10))
        self.theta += more_haze

        self.camera = source.camera

        av = Bullet.ammo_velocities[type_of]

        self.dx = round(av*math.sin(self.theta),2)+self.bullet_haze
        self.dy = round(av*math.cos(self.theta),2)+self.bullet_haze

        self.image = pygame.Surface([10, 10])
        self.image.fill(Color.BLACK)
        self.image.set_colorkey(Color.BLACK)
        pygame.draw.rect(self.image, Bullet.ammo_colors[type_of], [0,0, 2,10])

        self.image = pygame.transform.rotate(self.image, math.degrees(self.theta))
        self.rect = self.image.get_rect()    

        self.rect.x = self.x
        self.rect.y = self.y
    
    def physics(self):

        self.x += self.dx
        self.y += self.dy

        self.clock += 1

        
        
        if self.clock >= int(Ship.Weapons.reload_time[self.type_of])*3:
            self.kill_me = True
            

    def render(self):

        camera = self.camera
                
        #this method renders the sprite objects
        global_x = self.x
        global_y = self.y
        
        center_x = Resolution.w/2
        center_y = Resolution.h/2

        #sprite offset
        offset_x = self.rect.w/2
        offset_y = self.rect.h/2
        
        local_0_x = camera.state_vector.x
        local_0_y = camera.state_vector.y


        local_x = global_x - local_0_x - offset_x + center_x
        local_y = global_y - local_0_y - offset_y + center_y

            
        self.rect.x = local_x
        self.rect.y = local_y


class Ship(pygame.sprite.Sprite):
    #this is the spacecraft class

    sprite_path = {"fighter":"sprite\PNG\Sprites\Ships\spaceShips_001.png",
                       "interceptor":"sprite\PNG\Sprites\Ships\spaceShips_002.png",
                       "light_shuttle":"sprite\PNG\Sprites\Ships\spaceShips_003.png",
                       "station_defense":"sprite\PNG\Sprites\Ships\spaceShips_004.png"}

    #we can fix these programmatically
    MAX_ROT = .1
    MAX_THRUST = 1/50

    def ai(self):

        if not self.player:                
            
            if not (self.target == self):
                if not self.autopilot.kill_velocity:

                    if self.target.health.exploding:
                        self.target = self
                        
                    #AI code goes here for targetting

                    x = self.state_vector.x
                    y = self.state_vector.y

                    xt = self.target.state_vector.x
                    yt = self.target.state_vector.y

                    d = math.sqrt((x-xt)**2 + (y-yt)**2)

                    dx = self.state_vector.dx
                    dy = self.state_vector.dy
                    dtx = self.target.state_vector.dx
                    dty = self.target.state_vector.dy
                    

                    rel_v = math.sqrt((dtx-dx)**2+(dty-dy)**2)


                    difx = x-xt
                    dify = y-yt

                    tgt = math.atan2(difx,dify)+math.pi

                    hdg = self.state_vector.theta

                    dif = (hdg - tgt)

                    if abs(dif) >= (3*Ship.MAX_ROT):
                        self.thrusters.rotate_right = True

                    if abs(dif) < (3*Ship.MAX_ROT):
                        self.thrusters.rotate_right = False
                        self.thrusters.rotate_left = False
                        self.state_vector.theta = tgt
                        self.autopilot.turn_retrograde = False

                    if d < 100:
                        self.thrusters.main_thruster = False
                    elif d < 200:
                        self.fire_control = True
                    elif d > 300 and abs(dif) < math.pi/4 and rel_v > 5:
                        self.autopilot.kill_velocity = True
                    else:
                        self.thrusters.main_thruster = True
                        self.fire_control = False



            

        #fire control system
        if self.fire_control:
            self.fire("dumb_lead")

        #retrograde system

        if self.autopilot.turn_retrograde:
            dx = self.state_vector.dx
            dy = self.state_vector.dy
            hdg = self.state_vector.theta
            tgt = math.atan2(dx, dy) - math.pi

            dx = self.state_vector.dx
            dy = self.state_vector.dy
            v_mag = math.sqrt(dx**2+dy**2)

            if tgt < 0:
                tgt += 2*math.pi

            dif = (hdg - tgt)


            if abs(dif) >= (3*Ship.MAX_ROT):
                self.thrusters.rotate_right = True
                self.thrusters.main_thruster = False

            if abs(dif) < (3*Ship.MAX_ROT):
                self.thrusters.rotate_right = False
                self.thrusters.rotate_left = False
                self.state_vector.theta = tgt
                if self.player:
                    self.autopilot.turn_retrograde = False
                if not self.player:
                    if self.autopilot.kill_velocity:
                        self.thrusters.main_thruster = True
                        if v_mag <1:
                            self.autopilot.kill_velocity = False
                            self.thrusters.main_thruster = False
                    else:
                        self.thrusters.main_thruster = False

    def damage(self, dp):
        if self.health.shield > 0:
            self.health.shield -= dp

        if self.health.shield <= 0:
            self.health.shield = 0
            self.health.hull -= dp
            
        if self.health.hull <= 0:
            self.health.exploding = True

    def physics(self):
        mr = Ship.MAX_ROT
        mt = Ship.MAX_THRUST
        theta = self.state_vector.theta
        
        hdg = self.state_vector.theta
        
        #which thrusters are firing
        if self.thrusters.rotate_left:
            self.state_vector.dtheta = mr
        if self.thrusters.rotate_right:
            self.state_vector.dtheta = -mr

        if not (self.thrusters.rotate_left or self.thrusters.rotate_right):
            self.state_vector.dtheta = 0
            
        if self.thrusters.rotate_left and self.thrusters.rotate_right:
            self.state_vector.dtheta = 0


        if self.thrusters.main_thruster:
            a = mt
            self.state_vector.ddx = a*math.sin(theta)
            self.state_vector.ddy = a*math.cos(theta)
        else:
            self.state_vector.ddx = 0
            self.state_vector.ddy = 0
        
        #add velocity to position
        self.state_vector.x += self.state_vector.dx
        self.state_vector.y += self.state_vector.dy

        #add acceleration to velocity
        self.state_vector.dx += self.state_vector.ddx
        self.state_vector.dy += self.state_vector.ddy

        #change theta
        self.state_vector.theta += self.state_vector.dtheta
        
        #keep theta from getting out of hand.
        if theta >= 2*math.pi:
            self.state_vector.theta = self.state_vector.theta - 2*math.pi

        if theta < 0:
            self.state_vector.theta = self.state_vector.theta + 2*math.pi

    def render(self, camera):

        self.camera = camera
        
        self.rect.w, self.rect.h = self.size[0] + (self.scale * 5), self.size[1] + (self.scale*5)
        
        #this method renders the sprite objects
        global_x = self.state_vector.x
        global_y = self.state_vector.y
        
        center_x = Resolution.w/2
        center_y = Resolution.h/2

        #sprite offset
        offset_x = self.rect.w/2
        offset_y = self.rect.h/2
        
        theta = self.state_vector.theta


        #need to fix this so that it renders based on a "camera" position

        if self.player:
            self.rect.x = center_x - offset_x
            self.rect.y = center_y - offset_y
        else:
            local_0_x = camera.state_vector.x
            local_0_y = camera.state_vector.y

            local_x = global_x - local_0_x-offset_x + center_x
            local_y = global_y - local_0_y-offset_y + center_y
            
            self.rect.x = local_x
            self.rect.y = local_y






        self.image = pygame.transform.rotate(self.image_reference, math.degrees(theta))
        self.rect = self.image.get_rect(center=self.rect.center)    
            

        #player center logic here for when we get to that point

    class State_Vector:
        #this class contains the physical status of each and every vessel
        #we adjust these and physics "acts" on the state vector

        def __init__ (self):

            #x,y map position and orientation in space - all ships start "nose down"
            self.x = 0
            self.y = 0
            self.theta = 0

            #this is the velocity and change in heading
            self.dx = 0
            self.dy = 0
            self.dtheta = 0

            #this is the acceleration of the vehicle
            self.ddx = 0
            self.ddy = 0
            #self.ddtheta = 0 #currently unused, comment out if appropriate in the future

    class Health:
        #this class contains health information about the vessels

        def __init__(self):
            self.hull = 100
            self.shield = 100
            self.disabled = False #when vessels get damaged enough, they become derelicts
            self.exploding = False #obviously, we shouldn't be exploding yet


            #subsystems - eventually, damage will mess with these
            self.main_computer = True
            self.main_thrusters = True
            self.rcs_control_thrusters = True
            self.life_support = True
            self.core = True
            #obviously we could add more

    class Weapons:
        #this class will contain the weapon system that are installed

        reload_time = {"dumb_lead":6, "laser": 15, "tracer":10}

        def __init__(self):

            #weapon reload time
            self.cool_off = Ship.Weapons.reload_time["dumb_lead"]


    def fire(self, type_of):
        self.time += 1

        if (self.time % self.weapons.cool_off) == 0:
            Sounds.fire_sound.play()
            self.bullets.append(Bullet(type_of,self))
            self.time = 0

        


    class Autopilot:
        #this class controls a lot of the logic for operating the ship
        #the "reverse course" autopilot is in here and is available to everyone
        #as are the controls for the AI ships.
        #the autopilot adjusts "controls"

        def __init__(self):
            self.target_heading = 3/2*math.pi
            self.turn_retrograde = False
            self.kill_velocity = False

        
 
        

    class Thrusters:

        #this class contains information about the control systems        

        def __init__(self):

            #thrusters are "actuated" by controls
            #these all start "false" becuase nothing is
            #operating when you fire up a session
            
            self.rotate_left = False
            self.rotate_right = False
            self.main_thruster = False


    def control_input(self, control_map=None):
        
        if self.player:

            cm = control_map

            pressed = pygame.key.get_pressed()

            if pressed[cm.LEFT]:
                self.thrusters.rotate_left = True
            else:
                self.thrusters.rotate_left = False

            if pressed[cm.RIGHT]:
                self.thrusters.rotate_right = True
            else:
                self.thrusters.rotate_right = False

            if pressed[cm.UP]:
                self.thrusters.main_thruster = True
            else:
                self.thrusters.main_thruster = False

            if pressed[cm.DOWN]:
                self.autopilot.turn_retrograde = True
            else:
                self.autopilot.turn_retrograde = False

            if pressed[cm.FIRE]:
                self.fire_control = True #let'er rip!
            else:
                self.fire_control = False
                
            
    

    def __init__(self, ship_type, player):

        super().__init__()


        #ship type is one of the types of ships - this is loaded in the "sprite path"
        #above, player is a boolean that tells you whether controls are active or not

        self.ship_type = ship_type
        self.player = player

        path = Ship.sprite_path[self.ship_type]

        #this loads a reference prototype
        self.image_reference = pygame.image.load(path).convert_alpha()
        self.size = self.image_reference.get_size()
        self.scale = .4
        self.image_reference = pygame.transform.scale(self.image_reference, (int(self.size[0]*self.scale), int(self.size[1]*self.scale)))

        self.image = self.image_reference

        #initialize the other classes containing all the important stuff
        self.state_vector = Ship.State_Vector()
        self.health = Ship.Health()
        self.weapons = Ship.Weapons()
        self.autopilot = Ship.Autopilot()
        self.thrusters = Ship.Thrusters()

        self.vector_overlay = False

        self.target = self

        self.fire_control = False
        self.bullets = []
        self.damage_list = []
        self.time = 0

        self.explodey_time = 0
        
        self.rect = self.image_reference.get_rect()
       
