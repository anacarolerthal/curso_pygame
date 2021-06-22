import pygame
import os
import random

_sound_library = {}  # Mesmo método de biblioteca de efeitos sonoros que main.py


def play_sound(path):
    """Função que toca efeitos sonoros presentes na pasta /songs
    param path: nome do arquivo do efeito sonoro
    type path: string
    """
    global _sound_library
    sound = _sound_library.get(path)
    if sound == None:
        correctpath = os.path.join('songs', path)
        sound = pygame.mixer.Sound(correctpath)
        _sound_library[path] = sound
    sound.play()


class ElementSprite(pygame.sprite.Sprite):
    """ Classe básica de todos os elementos do jogo
    Tem herança de pygame.sprite.Sprite para que o pygame possa fazer tudo que faz com sprites
    """

    def __init__(self, image, position, speed=None, new_size=None, direction=(0, 1)):
        """ Construtor de elementos
        :param image: path e nome da imagem desejada para o sprite
        :type image: string
        :param position: posição inicial do elemento
        :type position: list
        :param speed: velocidade inicial do elemento
        :type speed: int
        :param new_size: tamanho desejado para a imagem
        :type new_size: tup
        :param direction: direções para movimentação
        :type direction: tuple
        """
        pygame.sprite.Sprite.__init__(self)

        # Tenta fazer upload da imagem
        if isinstance(image, str):
            self.image = pygame.image.load(os.path.join('images', image))
        else:
            raise TypeError("image must be of type str")
        # Checa se a imagem precia ter escala modificada. Caso sim, refaz a escala.
        if new_size:
            self.scale(new_size)

        self.rect = self.image.get_rect()  # extrai um objeto pygame.Rect da imagem
        screen = pygame.display.get_surface()
        self.direction = direction  # 1 -> baixo, -1 -> cima
        self.area = screen.get_rect()
        self.speed = speed  # define a speed. Se for None, a speed será setada na classe
        self.set_pos(position)  # define a posição do sprite

    def update(self, dt):
        """ Faz o update da posição do elemento
        :param dt: variação do tempo
        :type dt: int
        """
        pos_y = self.rect.center[1] + self.direction[1] * self.speed*dt
        self.rect.center = (self.rect.center[0], pos_y)
        # chama a função check_borders para matar detectar o que estiver fora da tela
        self.check_borders()

    def check_borders(self):
        """ Checa as bordas por elementos e os elimina
        """
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
        """ Retorna a velocidade do objeto pygame.Rect
        """
        return self.speed

    def set_speed(self, speed):
        """ Define a velocidade do objeto pygame.Rect
        :param speed: Velocidade
        :type speed: int
        """
        self.speed = speed

    def get_pos(self):
        """Retorna a posição do objeto pygame.Rect
        """
        return (self.rect.center[0],
                self.rect.bottom)

    def set_pos(self, pos):
        """Define a posição do objeto pygame.Rect
        :param pos: Posição
        :type pos: list
        """
        self.rect.center = (pos[0], pos[1])

    def get_size(self):
        """Retorna o tamanho do objeto pygame.Rect
        """
        return self.image.get_size()

    def scale(self, new_size):
        """ Redefine o tamanho do sprite
        :param new_size: tamanho desejado
        :type new_size: tuple
        """
        self.image = pygame.transform.scale(self.image, new_size)

    def set_image(self, image, scale):
        """
        """
        self.image = pygame.image.load(os.path.join('images', image))
        self.scale(scale)

    def rot_center(self, angle):
        """rotate an image while keeping its center"""
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)


class ShieldPowerUp(ElementSprite):
    def __init__(self, position, speed=.6, image=None, direction=(0, -1), player=None, size=(27, 36)):
        if not image:
            image = "escudo.png"
        super().__init__(image, position, speed, direction=direction, new_size=size)
        self.player = player

    def update(self, dt):
        """ Updates the position of the element
        :param dt: time variation
        :type dt: float (?)
        """
        # move_speed = (self.speed * dt / 16,
        #               self.speed * dt / 16)  # note that dt=16, so dt/16 == 1
        pos_x = self.player.rect.center[0]
        pos_y = self.player.rect.center[1]
        self.rect.center = (pos_x, pos_y)
        # self.rect = self.rect.move(move_speed)
        # kills the element if it is out of the screen borders


class Spaceship(ElementSprite):
    """ Classe do elemento controlável.
    Herda de ElementSprite, (que herda de pygame.sprite.Sprite), para que o pygame possa fazer o que quiser com sprites.
    """

    def __init__(self, position, lives=0, speed=3.5, image=None, new_size=[83, 248]):
        """ Spaceship constructor
        :param position: a posição inicial do elemento
        :type position: lista
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: inteiro (?)
        :param speed: a velocidade inicial do elemento em ambos os eixos.
        :type speed: lista
        :param image: a imagem do elemento. A classe possui um valor padrão que é sobrescrito quando este parâmetro não é "None".
        :type image: string
        :param new_size: o tamanho desejado do sprite. Veja ElementSprite.scale()
        :type new_size: list
        """

        image = "virus.png" if not image else image  # define a imagem padrão
        # chama ElementSprite.__init__()
        super().__init__(image, position, speed, new_size)
        self.set_lives(lives)  # define as vidas da nave

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
        """ Atualiza a posição do elemento.
        :param dt: variação do tempo
        :type dt: float (?)
        """
        # move_speed = (self.speed * dt / 16,
        #               self.speed * dt / 16)  # note that dt=16, so dt/16 == 1
        pos_x = self.rect.center[0] + self.direction[0] * self.speed*dt
        pos_y = self.rect.center[1] + self.direction[1] * self.speed*dt
        self.rect.center = (pos_x, pos_y)
        # self.rect = self.rect.move(move_speed)
        # mata o elemento se ele estiver fora dos limites da tela
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
        """  construtor. Basicamente o mesmo que Spaceship.__init__(), sendo a única diferença o valor padrão para a imagem
        :param position: a posição inicial do elemento.
        :type position: lista
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: inteiro (?)
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: lista
        :param image: a imagem do elemento. A classe possui um valor padrão  que é sobrescrito quando este parâmetro não é "None"
        :type image: string
        :param new_size: o tamanho desejado do sprite. Veja ElementSprite.scale()
        :type new_size: lista
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
        """  construtor. Basically the same as Spaceship.__init__(), only difference is the default value for image
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
        """ Atualiza a posição do elemento
        :param dt: variação do tempo
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
        """  construtor. Basicamente o mesmo que Spaceship.__init__(), sendo a única diferença o valor padrão para a imagem
        :param position: a posição inicial do elemento.
        :type position: lista
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: inteiro (?)
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: lista
        :param image: a imagem do elemento. A classe possui um valor padrão  que é sobrescrito quando este parâmetro não é "None"
        :type image: string
        :param new_size: o tamanho desejado do sprite. Veja ElementSprite.scale()
        :type new_size: lista
        """
        image = f"inimigo2{color}.png" if not image else image
        super().__init__(position, lives, speed, image, size)
        self.direction = (1, 0)
        self.shtcounter = 0
        self.color = color

    def update(self, dt, playerposx, enemies, lst=None):
        """ Atualia a posição do elemento
        :param dt: variação do tempo
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
        play_sound("Enemy Shoot.ogg")
        laser = Laser((self.rect.center[0], self.rect.top),
                      image=f'tiroinimigo{self.color}.png', direction=(0, 1))
        shoots.append([laser, pygame.sprite.RenderPlain(laser)])


class Bomb(Enemy):
    def __init__(self, position, lives=0, speed=.25, image=None, size=(55, 60), color='G'):
        """  construtor. Basicamente o mesmo que Spaceship.__init__(), sendo a única diferença o valor padrão para a imagem
        :param position: a posição inicial do elemento.
        :type position: lista
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: inteiro (?)
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: lista
        :param image: a imagem do elemento. A classe possui um valor padrão  que é sobrescrito quando este parâmetro não é "None"
        :type image: string
        :param new_size: o tamanho desejado do sprite. Veja ElementSprite.scale()
        :type new_size: lista
        """
        image = f"inimigo3{color}.png" if not image else image
        super().__init__(position, lives, speed, image, size)


class Shield(Enemy):
    def __init__(self, position, lives=0, speed=.35, image=None, size=(50, 50), color='G'):
        """  construtor. Basicamente o mesmo que Spaceship.__init__(), sendo a única diferença o valor padrão para a imagem
        :param position: a posição inicial do elemento.
        :type position: lista
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: inteiro (?)
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: lista
        :param image: a imagem do elemento. A classe possui um valor padrão  que é sobrescrito quando este parâmetro não é "None"
        :type image: string
        :param new_size: o tamanho desejado do sprite. Veja ElementSprite.scale()
        :type new_size: lista
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
            if not enemy.shield and self.rect.center[1] > enemy.rect.center[1]:
                self.enemy = enemy
                self.enemy.shield = True
        else:
            self.enemy = None
            # self.enemyposx = rand_enemy.get_pos_enemy()[0]
            # self.enemyposy = rand_enemy.get_pos_enemy()[1]
        # else:
            # self.enemyposx = self.rect.center[0]
            # self.enemyposy = 640

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
