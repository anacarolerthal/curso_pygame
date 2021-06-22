import pygame
import os
import random


class ElementSprite(pygame.sprite.Sprite):
    """ The basic class of every element in the game.
    Inherits from pygame.sprite.Sprite so pygame can do with it everything it does with sprites
    """

    def __init__(self, image, position, speed=None, new_size=None, direction=(0, 1)):
        """ Element constructor
        :param image: the location and name of the desired image for the sprite
        :type image: string
        :param position: the initial position of the element
        :type position: list
        :param speed: the initial speed of the element
        :type speed: list
        :param new_size: the desired size of the loaded image
        :type new_size: list
        """
        pygame.sprite.Sprite.__init__(self)
        # Tries to load the image
        if isinstance(image, str):
            self.image = pygame.image.load(os.path.join('images', image))
        else:
            raise TypeError("image must be of type str")
        # Checks if the image has to be resized and if so, does it
        if new_size:
            self.scale(new_size)
        self.rect = self.image.get_rect()  # gets a pygame.Rect object out of the image
        screen = pygame.display.get_surface()
        self.direction = direction  # 1 -> down, -1 -> up
        self.area = screen.get_rect()
        self.speed = speed
        self.set_pos(position)  # sets the position of the sprite
        # sets the speed. If None, the speed is set to (0,2)

    def update(self, dt):
        """ Updates the position of the element
        :param dt: time variation
        :type dt: float (?)
        """
        # move_speed = (self.speed * dt / 16,
        #               self.speed * dt / 16)  # note that dt=16, so dt/16 == 1
        pos_y = self.rect.center[1] + self.direction[1] * self.speed*dt
        self.rect.center = (self.rect.center[0], pos_y)
        # self.rect = self.rect.move(move_speed)
        # kills the element if it is out of the screen borders
        self.check_borders()

    def check_borders(self):
        if (self.rect.left > self.area.right) or \
                (self.rect.top > self.area.bottom) or \
                (self.rect.right < 0):
            self.kill()
            return True
        if (self.rect.bottom < - 40):
            self.kill()
            return True
        return False

    def get_speed(self):
        return self.speed

    def set_speed(self, speed):
        self.speed = speed

    def get_pos(self):
        # gets the position of the pygame.Rect object
        return (self.rect.center[0],
                self.rect.bottom)

    def set_pos(self, pos):
        # sets the position of the pygame.Rect object
        self.rect.center = (pos[0], pos[1])

    def get_size(self):
        return self.image.get_size()

    def scale(self, new_size):
        # resizes the sprite
        self.image = pygame.transform.scale(self.image, new_size)

    def set_image(self, image, scale):
        self.image = pygame.image.load(os.path.join('images', image))
        self.scale(scale)

    def rot_center(self, angle):
        """rotate an image while keeping its center"""
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)


class Spaceship(ElementSprite):
    """ class of the controlable element.
    Inherits from ElementSprite (which inherits from pygame.sprite.Sprite) so pygame can do with it whatever it does with sprites.
    """

    def __init__(self, position, lives=0, speed=3.5, image=None, new_size=[83, 248]):
        """ Spaceship constructor
        :param position: the initial position of the element
        :type position: list
        :param lives: how many times the element can get hit before dying
        :type lives: integer (?)
        :param speed: the initial speed of the element on both axis
        :type speed: list
        :param image: the image of the element. The class has a default value that gets overwritten when this parameter is not None
        :type image: string
        :param new_size: the desired size of the sprite. See ElementSprite.scale()
        :type new_size: list
        """

        image = "virus.png" if not image else image  # sets the default image
        # calls ElementSprite.__init__()
        super().__init__(image, position, speed, new_size)
        self.set_lives(lives)  # sets the lives of the spaceship

    def get_lives(self):
        return self.lives

    def set_lives(self, lives):
        self.lives = lives


class Laser(ElementSprite):
    def __init__(self, position, speed=.6, image=None, direction=(0, -1), angle=None):
        if not image:
            image = "tironave1.png"
        super().__init__(image, position, speed, direction=direction)

        if angle:
            self.rot_center(angle)

    def update(self, dt):
        """ Updates the position of the element
        :param dt: time variation
        :type dt: float (?)
        """
        # move_speed = (self.speed * dt / 16,
        #               self.speed * dt / 16)  # note that dt=16, so dt/16 == 1
        pos_x = self.rect.center[0] + self.direction[0] * self.speed*dt
        pos_y = self.rect.center[1] + self.direction[1] * self.speed*dt
        self.rect.center = (pos_x, pos_y)
        # self.rect = self.rect.move(move_speed)
        # kills the element if it is out of the screen borders
        self.check_borders()


class PowerUp(ElementSprite):
    def __init__(self, position, speed=.4, image=None, direction=(0, 1), kind='speed', power=None, size=(40, 40)):
        self.kind = kind.lower()
        if not power:
            if self.kind == 'speed':
                self.power = 1
            elif self.kind == 'damage':
                self.power = 2
            elif self.kind == 'bomb':
                self.power = 3
            elif self.kind == 'shield':
                self.power = 4
            else:
                self.kill()
        else:
            self.power = power
        if not image:
            image = f"powerup{self.power}.png"
        super().__init__(image, position, speed, direction=direction, new_size=size)

    def get_power(self):
        return self.power


class Enemy(Spaceship):
    def __init__(self, position, lives=0, speed=.35, image=None, size=(75, 50), color='G'):
        """  constructor. Basically the same as Spaceship.__init__(), only difference is the default value for image
        :param position: the initial position of the element
        :type position: list
        :param lives: how many times the element can get hit before dying
        :type lives: integer (?)
        :param speed: the initial speed of the element on both axis
        :type speed: list
        :param image: the image of the element. The class has a default value that gets overwriten when this parameter is not None
        :type image: string
        :param new_size: the desired size of the sprite. See ElementSprite.scale()
        :type new_size: list
        """
        image = f"inimigo1{color}.png" if not image else image
        super().__init__(position, lives, speed, image, size)
        self.isdead = False
        self.shield = False

    def got_hit(self):
        self.lives -= 1
        if self.lives <= 0:
            self.isdead = True
            self.kill()

    def get_pos_enemy(self):  # é isto então nao, player tem um got_hit tb
        return (self.rect.center[0], self.rect.center[1])

    def get_state(self):
        return self.isdead


class Spider(Enemy):
    def __init__(self, position, lives=0, speed=.35, image=None, size=(75, 50), color='G'):
        """  constructor. Basically the same as Spaceship.__init__(), only difference is the default value for image
        :param position: the initial position of the element
        :type position: list
        :param lives: how many times the element can get hit before dying
        :type lives: integer (?)
        :param speed: the initial speed of the element on both axis
        :type speed: list
        :param image: the image of the element. The class has a default value that gets overwriten when this parameter is not None
        :type image: string
        :param new_size: the desired size of the sprite. See ElementSprite.scale()
        :type new_size: list
        """
        image = f"inimigo1{color}.png" if not image else image
        super().__init__(position, lives, speed, image, size)

    def update(self, dt, playerposx, enemies, lst=None):
        """ Updates the position of the element
        :param dt: time variation
        :type dt: float (?)
        """
        # move_speed = (self.speed * dt / 16,
        #               self.speed * dt / 16)  # note that dt=16, so dt/16 == 1
        pos_y = self.rect.center[1] + self.direction[1] * self.speed*dt
        if playerposx - self.rect.center[0] > 0:
            pos_x = self.rect.center[0] + 1 * self.speed*dt/4
        else:
            pos_x = self.rect.center[0] - 1 * self.speed*dt/4
        self.rect.center = (pos_x, pos_y)
        self.check_borders()


class Shooter(Enemy):
    def __init__(self, position, lives=0, speed=.35, image=None, size=(60, 45), color='G'):
        """  constructor. Basically the same as Spaceship.__init__(), only difference is the default value for image
        :param position: the initial position of the element
        :type position: list
        :param lives: how many times the element can get hit before dying
        :type lives: integer (?)
        :param speed: the initial speed of the element on both axis
        :type speed: list
        :param image: the image of the element. The class has a default value that gets overwriten when this parameter is not None
        :type image: string
        :param new_size: the desired size of the sprite. See ElementSprite.scale()
        :type new_size: list
        """
        image = f"inimigo2{color}.png" if not image else image
        super().__init__(position, lives, speed, image, size)
        self.direction = (1, 0)
        self.shtcounter = 0
        self.color = color

    def update(self, dt, playerposx, enemies, lst=None):
        """ Updates the position of the element
        :param dt: time variation
        :type dt: float (?)
        """
        # move_speed = (self.speed * dt / 16,
        #               self.speed * dt / 16)  # note that dt=16, so dt/16 == 1
        pos_x = self.rect.center[0]
        pos_y = self.rect.center[1]
        if pos_y < 50:
            pos_y += self.speed*dt
        if pos_x >= 580:
            self.direction = (-0.71, 0)
        elif pos_x <= 40:
            self.direction = (1, 0)
        pos_x += self.direction[0]*self.speed*dt/4
        self.rect.center = (pos_x, pos_y)

        if self.shtcounter > 60:
            self.shoot(lst)
            self.shtcounter = 0
        self.shtcounter += 1

        self.check_borders()

    def shoot(self, shoots):
        laser = Laser((self.rect.center[0], self.rect.top),
                      image=f'tiroinimigo{self.color}.png', direction=(0, 1))
        shoots.append([laser, pygame.sprite.RenderPlain(laser)])


class Bomb(Enemy):
    def __init__(self, position, lives=0, speed=.25, image=None, size=(55, 60), color='G'):
        """  constructor. Basically the same as Spaceship.__init__(), only difference is the default value for image
        :param position: the initial position of the element
        :type position: list
        :param lives: how many times the element can get hit before dying
        :type lives: integer (?)
        :param speed: the initial speed of the element on both axis
        :type speed: list
        :param image: the image of the element. The class has a default value that gets overwriten when this parameter is not None
        :type image: string
        :param new_size: the desired size of the sprite. See ElementSprite.scale()
        :type new_size: list
        """
        image = f"inimigo3{color}.png" if not image else image
        super().__init__(position, lives, speed, image, size)


class Shield(Enemy):
    def __init__(self, position, lives=0, speed=.35, image=None, size=(50, 50), color='G'):
        """  constructor. Basically the same as Spaceship.__init__(), only difference is the default value for image
        :param position: the initial position of the element
        :type position: list
        :param lives: how many times the element can get hit before dying
        :type lives: integer (?)
        :param speed: the initial speed of the element on both axis
        :type speed: list
        :param image: the image of the element. The class has a default value that gets overwriten when this parameter is not None
        :type image: string
        :param new_size: the desired size of the sprite. See ElementSprite.scale()
        :type new_size: list
        """
        image = f"inimigo4{color}.png" if not image else image
        super().__init__(position, lives, speed, image, size)
        self.enemy = None
        self.enemyposx = 0
        self.enemyposy = 0
        self.shield = True

    def choose_rand_enemy(self, enemylist):
        if len(enemylist) > 0:
            enemy = random.choice(enemylist)[0]
            if not enemy.shield and self.rect.center[1]>enemy.rect.center[1]:
                self.enemy = enemy
                self.enemy.shield = True
        else:
            self.enemy = None
            #self.enemyposx = rand_enemy.get_pos_enemy()[0]
            #self.enemyposy = rand_enemy.get_pos_enemy()[1]
        # else:
            #self.enemyposx = self.rect.center[0]
            #self.enemyposy = 640

    def update(self, dt, playerposx, enemylist, lst=None):
        """ Updates the position of the element 
        :param dt: time variation
        :type dt: float (?)
        """
        # move_speed = (self.speed * dt / 16,
        #               self.speed * dt / 16)  # note that dt=16, so dt/16 == 1
        if not self.enemy:
            self.choose_rand_enemy(enemylist)
            self.enemyposx = self.rect.center[0]
            self.enemyposy = 640
        else:
            if self.enemy.get_state():
                self.enemy = None
            else:
                self.enemyposx = self.enemy.get_pos_enemy()[0]
                self.enemyposy = self.enemy.get_pos_enemy()[1]

        pos_y = self.rect.center[1]
        
        
        if self.enemyposx - self.rect.center[0] > 5:
            pos_x = self.rect.center[0] + 1 * self.speed*dt
        elif self.enemyposx - self.rect.center[0] < -5:
            pos_x = self.rect.center[0] - 1 * self.speed*dt
        else:
            pos_x = self.enemyposx
        # baixo -> diferença negativa
        #  talvez seja uma boa mudar esse 50 pra ver onde o escudo para
        if (self.rect.center[1] - self.enemyposy) < 50:
            pos_y += self.direction[1] * self.speed * \
                dt  # se não estiver 50 pixels abaixo
        elif (self.rect.center[1] - self.enemyposy) > 200:
            pos_y -= self.direction[1] * self.speed * \
                dt  # se não estiver 50 pixels abaixo
        elif (self.rect.center[1] - self.enemyposy) > 50:
            pos_y -= self.direction[1] * self.speed * \
                dt  # se não estiver 50 pixels abaixo
        self.rect.center = (pos_x, pos_y)
        self.check_borders()  # also, nao quer dar uma pausa nao? pra almoçar?
