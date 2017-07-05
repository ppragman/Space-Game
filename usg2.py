import pygame
import math
from spaceobj import *
import time
import os

#start initializing the basics
colors = Color()
player_controls = Player_Controls()
resolution = Resolution()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()




def overlay_vector(ship, canvas):

    if ship.vector_overlay:
        debug_x = ship.rect.x + ship.rect.w/2
        debug_y = ship.rect.y + ship.rect.w/2

        debug_vx = ship.state_vector.dx
        debug_vy = ship.state_vector.dy

        target = math.atan2(debug_vx, debug_vy) - math.pi
        theta = ship.state_vector.theta

        hdg = debug_x+20*math.sin(theta), debug_y+20*math.cos(theta)
        tgt = debug_x+20*math.sin(target), debug_y+20*math.cos(target)

        #pygame.draw.line(canvas, Color.BLUE, (debug_x, debug_y), hdg, 3)
        pygame.draw.line(canvas, Color.GREEN, (debug_x, debug_y), (debug_x-20*debug_vx, debug_y-20*debug_vy), 3)
        pygame.draw.line(canvas, Color.RED, (debug_x, debug_y), (debug_x+20*debug_vx, debug_y+20*debug_vy),3)


def health_bar(shield, hull, canvas):
    if shield <= 0:
        shield = 0
    else:
        pygame.draw.line(canvas, Color.BLUE, (10,10), (10 + shield,10), 4)

    if hull <= 0:
        hull = 0
    else:
        pygame.draw.line(canvas, Color.GRAY, (10,20), (10 + hull,20), 4)

def radar(canvas, ships, planets, player):

    w = Over_World_Size.width
    h = Over_World_Size.height

    pygame.draw.rect(canvas, Color.GRAY, [Resolution.w-115,5,110, 110])
    pygame.draw.rect(canvas, Color.BLACK, [Resolution.w-110,10,100,100])

    for planet in planets:

        if not planet.star:
            x = planet.x
            y = planet.y
            
            x = int(round((x/w)*100+50,0))
            y = int(round((y/w)*100+50,0))

            pygame.draw.circle(canvas, Color.YELLOW, (Resolution.w - 110 + x,y),5, 1)

    for ship in ships:
        x = ship.state_vector.x
        y = ship.state_vector.y

        x = int(round((x/w)*100+50,0))
        y = int(round((y/w)*100+50,0))

        color = Color.GREEN



        if ship.target == player:
            color = Color.RED

        if ship.player:
            color = Color.BLUE

        if abs(x) < 100 and abs(y) <100 and x > 0 and y > 0:            
            pygame.draw.circle(canvas,color, (Resolution.w - 110 + x,y),1, 1)


            

def main():
    #let's setup pygame
    clock = pygame.time.Clock()
    screen_size = (resolution.w, resolution.h)
    main_window = make_window(screen_size, "Untitled Space Game .2")

    #let's build a "player ship"
    player_ship = Ship("light_shuttle",True)
    player_ship.state_vector.x = 0
    player_ship.state_vector.y = 0
    player_ship.vector_overlay = True
    master_camera = player_ship


    #let's build a "badguy ship"
    bad_ship = Ship("fighter", False)
    bad_ship.state_vector.x, bad_ship.state_vector.y = 100,250

    #let's build another
    b = Ship("fighter",False)
    b.state_vector.x, b.state_vector.y = -100,-100

    #let's make a ton of stars
    stars = []
    for i in range(0,1000):
        stars.append(Star(master_camera))

    #let's make a few planets
    city_planet = Planet(0,0,"terran",master_camera)
    lava_planet = Planet(400,1200, "lava", master_camera)


    #we'll make a list of sprites we'll render
    background_sprites = pygame.sprite.Group()
    bullet_layer = pygame.sprite.Group()
    foreground_sprites = pygame.sprite.Group()

    #here we'll load the sprites into it
    for star in stars:
        background_sprites.add(star)

    background_sprites.add(city_planet)
    background_sprites.add(lava_planet)
    
    foreground_sprites.add(player_ship)
    foreground_sprites.add(bad_ship)
    foreground_sprites.add(b)


    #this loop contains the game code
    running = True
    while running:
        #first thing we should do is build a way to exit the window

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                

        #let's update the sprites
        background_sprites.update()
        
        foreground_sprites.update()

        bullet_layer.update()

        #draw the background pallet then draw on it
        main_window.fill(colors.BLACK)

        background_sprites.draw(main_window)
        foreground_sprites.draw(main_window)
        bullet_layer.draw(main_window)

        #draw a health bar
        shield = player_ship.health.shield
        hull = player_ship.health.hull

        health_bar(shield, hull, main_window)

        #draw radar
        radar(main_window, foreground_sprites, background_sprites, player_ship)
        
        for obj in background_sprites:
            obj.render()



        for ship in foreground_sprites:
            ship.control_input(player_controls)
            ship.ai()
            ship.physics()
            ship.render(master_camera)
            #overlay_vector(ship, main_window)

            #replenish health slowly
            ship.health.shield += .3
            ship.health.hull += .1

            if ship.health.exploding == False:
                ship.health.shield = min(ship.health.shield, 100)
                ship.health.hull = min (ship.health.hull, 100)

            #explodey stuff
            if ship.health.exploding:
                ship.explodey_time += 1
                if ship.explodey_time >= 120:
                    ship.reference_image = pygame.Surface([10,10])
                    ship.reference_image.fill(Color.BLACK)
                    ship.reference_image.set_colorkey(Color.BLACK)
                    ship.damage_list.append(Damage(ship.state_vector.x,ship.state_vector.y,ship))
                    ship.damage_list.append(Explosion(ship.state_vector.x, ship.state_vector.y, ship))
                    
                    
                    for bullet in ship.bullets:
                        bullet.kill()
                    for damage in ship.damage_list:
                        damage.kill()

                    if not ship.player:
    
                        ship.kill()

                    if ship.player:
                        running = False

                    continue


            for damage in ship.damage_list:
                bullet_layer.add(damage)

            for damage in ship.damage_list:
                damage.physics()
                damage.render()

                if damage.fade:
                    ship.damage_list.remove(damage)
                    damage.kill()

            for bullet in ship.bullets:
                bullet_layer.add(bullet)

            for bullet in ship.bullets:
                bullet.physics()
                bullet.render()
                
                if bullet.kill_me:
                    ship.bullets.remove(bullet)
                    bullet.kill()

                for target in foreground_sprites:
                    col = pygame.sprite.collide_rect(bullet, target)
                    if col and not (bullet.source == target):
                        target.target = bullet.source
                        target.damage(bullet.dp)
                        target.damage_list.append(Damage(bullet.x, bullet.y, target))
                        seed = randint(0,100)
                        if seed > 80:
                            target.damage_list.append(Explosion(bullet.x, bullet.y, target))
                        bullet.kill()

        
        #update the screen
        pygame.display.flip()

        #limit to 60 fps
        clock.tick(60)

main()


pygame.quit()
