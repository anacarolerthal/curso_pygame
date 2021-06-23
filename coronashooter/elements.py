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
        """ ElementSprite constructor
        :param image: path e nome da imagem desejada para o sprite
        :type image: string
        :param position: posição inicial do elemento
        :type position: list
        :param speed: velocidade inicial do elemento em ambos os eixos. Default None
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
        """ Checa se o eleemnto está fora das bordas da tela, e o elimina se estiver
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
        """ Define a imagem do elemento
        :param image: Imagem
        :type image: string
        :param scale: Escala da imagem
        :type scale: float
        """
        self.image = pygame.image.load(os.path.join('images', image))
        self.scale(scale)

    def rot_center(self, angle):
        """Rotaciona a imagem mantendo seu centro
        :param angle: Ângulo do elemento
        :type angle: float
        """
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)


class Block(ElementSprite):
    def __init__(self, position, speed=0, image=None, direction=(0, 0), player=None, size=(80, 80), value=None):
        """ ShieldPowerUp constructor
        :param position: posição inicial do escudo
        :type position: list
        :param speed: velocidade inicial do elemento em ambos os eixos
        :type speed: int
        :param image: path e nome da imagem desejada para escudo. Default None
        :type image: string
        :param direction: direções para movimentação
        :type direction: tuple
        :param player: Player. Default None
        :type player: main.Player
        """

        # define a imagem padrão
        if not image:
            image = "escudo.png"

        # chama ElementSprite.__init__()
        super().__init__(image, position, speed, direction=direction, new_size=size)
        self.value = value

    def get_value(self):
        return self.value


class ShieldPowerUp(ElementSprite):
    """ Classe do power up de escudo. Tem herança de ElementSprite
    """

    def __init__(self, position, speed=.6, image=None, direction=(0, -1), player=None, size=(27, 36)):
        """ ShieldPowerUp constructor
        :param position: posição inicial do escudo
        :type position: list
        :param speed: velocidade inicial do elemento em ambos os eixos
        :type speed: int
        :param image: path e nome da imagem desejada para escudo. Default None
        :type image: string
        :param direction: direções para movimentação
        :type direction: tuple
        :param player: Player. Default None
        :type player: main.Player
        """

        # define a imagem padrão
        if not image:
            image = "escudo.png"

        # chama ElementSprite.__init__()
        super().__init__(image, position, speed, direction=direction, new_size=size)
        self.player = player

    def update(self, dt):
        """ Faz update da posição do escudo
        :param dt: variação de tempo
        :type dt: int
        """
        pos_x = self.player.rect.center[0]
        pos_y = self.player.rect.center[1]
        self.rect.center = (pos_x, pos_y)


class Spaceship(ElementSprite):
    """ Classe do elemento controlável, que será utilizada para o player e para os inimigos.
    Herda de ElementSprite, para que o pygame possa fazer o que quiser com sprites.
    """

    def __init__(self, position, lives=0, speed=3.5, image=None, new_size=[83, 248]):
        """ Spaceship constructor
        :param position: a posição inicial do elemento
        :type position: list
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: int
        :param speed: a velocidade inicial do elemento em ambos os eixos.
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param new_size: o tamanho desejado do sprite. Veja ElementSprite.scale()
        :type new_size: list
        """

        # define a imagem padrão
        image = "virus.png" if not image else image

        # chama ElementSprite.__init__()
        super().__init__(image, position, speed, new_size)
        self.set_lives(lives)  # define as vidas da nave

    def get_lives(self):
        """Retorna a quantidade de vidas do objeto
        """
        return self.lives

    def set_lives(self, lives):
        """ Define as vidas do objeto
        :param lives: Vidas
        :type lives: int
        """
        self.lives = lives


class Laser(ElementSprite):
    """ Classe do elemento Laser (tiros em geral).
    Herda de ElementSprite.
    """

    def __init__(self, position, speed=.6, image=None, direction=(0, -1), angle=None):
        """ Laser constructor
        :param position: a posição inicial do elemento
        :type position: list
        :param speed: a velocidade inicial do elemento em ambos os eixos.
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param direction: direções para movimentação
        :type direction: tuple
        :param new_size: o tamanho desejado do sprite. Veja ElementSprite.scale()
        :type new_size: list
        :param angle: Ângulo do elemento. Default None
        :type angle: float
        """

        # define a imagem padrão
        if not image:
            image = "tironave1.png"

        # chama ElementSprite.__init__()
        super().__init__(image, position, speed, direction=direction)

        # define ângulação
        if angle:
            self.rot_center(angle)

    def update(self, dt):
        """ Atualiza a posição do elemento.
        :param dt: variação do tempo
        :type dt: int
        """

        # posição
        pos_x = self.rect.center[0] + self.direction[0] * self.speed*dt
        pos_y = self.rect.center[1] + self.direction[1] * self.speed*dt
        self.rect.center = (pos_x, pos_y)

        # mata o elemento se ele estiver fora dos limites da tela
        self.check_borders()


class Explosion(ElementSprite):
    """ Classe do elemento Explosion (sprite de explosão).
    Herda de ElementSprite.
    """

    def __init__(self, position, speed=0, image=None, direction=(0, 0), angle=None, type=1, color='G', hits=[]):
        """ Explosion constructor
        :param position: a posição inicial do elemento
        :type position: list
        :param speed: a velocidade inicial do elemento em ambos os eixos.
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param direction: direções para movimentação
        :type direction: tuple
        :param angle: ângulo do elemento. Default None
        :type angle: float
        :param color: cor do sprite, utilizado para escolher a imagem
        :type color: string
        """
        # define a imagem padrão
        if not image:
            self.image = f"laser{type}{color}.png"
        self.position = position
        self.speed = speed
        self.direction = direction
        # chama ElementSprite.__init__() e define valores iniciais de objetos lógicos
        self.count = 0
        self.hits = hits
        self.duration = 50
        super().__init__(self.image, self.position, self.speed, direction=self.direction)

        # define ângulação
        if angle:
            self.rot_center(angle)

    def update(self, dt):
        """ Atualiza a posição do elemento.
        :param dt: variação do tempo
        :type dt: int
        """
        self.count += 1
        # if self.count == 1:
        if self.count > self.duration:
            self.kill()


class PowerUp(ElementSprite):
    """ Classe do elemento PowerUp
    Herda de ElementSprite.
    """

    def __init__(self, position, speed=.4, image=None, direction=(0, 1), kind='speed', power=None, size=(40, 40)):
        """ PowerUp constructor
        :param position: a posição inicial do elemento
        :type position: list
        :param speed: a velocidade inicial do elemento em ambos os eixos.
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param direction: direções para movimentação
        :type direction: tuple
        :param kind: tipo de power up
        :type kind: string
        :param power: número relacionado ao tipo de power up
        :type power: int. Default None
        :param size: tamanho do powerup
        :type size: tuple
        """

        # define o tipo do power up
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

        # define a imagem padrão
        if not image:
            image = f"powerup{self.power}.png"

        # chama ElementSprite.__init__()
        super().__init__(image, position, speed, direction=direction, new_size=size)

    def get_power(self):
        """Retorna o powerup setado
        """
        return self.power


class Enemy(Spaceship):
    """ Classe de todos os inimigos do jogo
    Herda de Spaceship.
    """

    def __init__(self, position, lives=0, speed=.35, image=None, size=(75, 50), color='G'):
        """Enemy construtor. Basicamente o mesmo que Spaceship.__init__(), sendo a única diferença o valor padrão para a imagem
        :param position: a posição inicial do inimigo.
        :type position: list
        :param lives: vidas do inimigo
        :type lives: int
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param size: o tamanho desejado do inimigo
        :type size: tuple
        :param color: cor do inimigo, utilizado para escolher a imagem
        :type color: string
        """

        self.id = "enemy"

        # define a imagem padrão
        image = f"inimigo1{color}.png" if not image else image

        # chama ElementSprite.__init__() e define valores iniciais de objetos lógicos
        super().__init__(position, lives, speed, image, size)
        self.isdead = False
        self.shield = False

    def got_hit(self):
        """ Define os reflexos do dano tomado pelo inimigo
        """
        self.lives -= 1
        if self.lives <= 0:
            self.isdead = True
            self.kill()
        return None

    def get_pos_enemy(self):
        """ Retorna a posição de um inimigo
        """
        return (self.rect.center[0], self.rect.center[1])

    def get_state(self):
        """ Retorna o estado do inimigo (vivo/morto)
        """
        return self.isdead

    def get_id(self):
        return self.id


class Spider(Enemy):
    """Classe do inimigo Spider
    Herda de Enemy
    """

    def __init__(self, position, lives=0, speed=.35, image=None, size=(75, 50), color='G'):
        """Spider construtor
        :param position: a posição inicial do elemento.
        :type position: list
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: int
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param size: o tamanho do spider
        :type size: tuple
        :param color: cor do spider, utilizado para escolher a imagem
        :type color: string
        """

        # define a imagem padrão
        image = f"inimigo1{color}.png" if not image else image

        # chama ElementSprite.__init__()
        super().__init__(position, lives, speed, image, size)

    def update(self, dt, playerposx, enemies, lst=None, lst2=None):
        """ Atualiza a posição e situação do spider
        :param dt: variação do tempo
        :type dt: int
        :param playerposx: posição do jogador
        :type playerposx: int
        :param enemies: lista dos inimigos vivos
        :type enemies: list
        :param lst: não usada no spider
        :type lst: list
        """

        # posição e movimento, perseguindo o player
        pos_y = self.rect.center[1] + self.direction[1] * self.speed*dt
        if playerposx - self.rect.center[0] > 0:
            pos_x = self.rect.center[0] + 1 * self.speed*dt/4
        else:
            pos_x = self.rect.center[0] - 1 * self.speed*dt/4
        self.rect.center = (pos_x, pos_y)

        # mata o elemento se ele estiver fora dos limites da tela
        self.check_borders()


class Shooter(Enemy):
    """ Classe do inimigo Shooter
    Herda de Enemy.
    """

    def __init__(self, position, lives=2, speed=.35, image=None, size=(60, 45), color='G'):
        """Shooter construtor
        :param position: a posição inicial do elemento.
        :type position: list
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: int
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param size: o tamanho do spider
        :type size: tuple
        :param color: cor do spider, utilizado para escolher a imagem
        :type color: string
        """

        # define a imagem padrão
        image = f"inimigo2{color}.png" if not image else image

        # chama ElementSprite.__init__()
        super().__init__(position, lives, speed, image, size)
        self.direction = (1, 0)
        self.shtcounter = 0
        self.color = color

    def update(self, dt, playerposx, enemies, lst=None, lst2=None):
        """ Atualiza a posição e situação do shooter
        :param dt: variação do tempo
        :type dt: int
        :param playerposx: posição do jogador
        :type playerposx: int
        :param enemies: lista dos inimigos vivos
        :type enemies: list
        :param lst: lista de todos os tiros do shooter
        :type lst: list
        """

        # posição e movimento, fixando em y=50 definindo sua movimentação de um lado para o outro da tela
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

        # definindo frequência de tiros do shooter
        if self.shtcounter > 60:
            self.shoot(lst)
            self.shtcounter = 0
        self.shtcounter += 1

        # mata o elemento se ele estiver fora dos limites da tela
        self.check_borders()

    def shoot(self, shoots):
        """Define os efeitos do tiro do shooter
        :param shoots: tiros do shooter
        :type shoots: list
        """
        # som do tiro
        play_sound("Enemy Shoot.ogg")

        # cria o tiro (laser), mudando a imagem padrão da classe Laser e o adiciona à lista de tiros
        laser = Laser((self.rect.center[0], self.rect.top),
                      image=f'tiroinimigo{self.color}.png', direction=(0, 1))
        shoots.append([laser, pygame.sprite.RenderPlain(laser)])


class Bomb(Enemy):
    """ Classe do inimigo Bomb
    Herda de Enemy.
    """

    def __init__(self, position, lives=3, speed=.15, image=None, size=(55, 60), color='G'):
        """Bomb construtor
        :param position: a posição inicial do elemento.
        :type position: list
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: int
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param size: o tamanho do spider
        :type size: tuple
        :param color: cor do spider, utilizado para escolher a imagem
        :type color: string
        """

        # define a imagem padrão
        image = f"inimigo3{color}.png" if not image else image
        self.shield = True

        # chama ElementSprite.__init__()
        super().__init__(position, lives, speed, image, size)
        self.id = "bomb"

    def update(self, dt, playerposx, enemies, lst=None, lst2=None):
        """ Atualiza a posição e situação do bomb
        :param dt: variação do tempo
        :type dt: int
        :param playerposx: posição do jogador
        :type playerposx: int
        :param enemies: lista dos inimigos vivos
        :type enemies: list
        :param lst: lista de todos os elementos ativos: inimigos, tiros do player e tiros dos inimigos
        :type lst: list
        """

        # posição
        pos_y = self.rect.center[1] + self.direction[1] * self.speed*dt
        self.rect.center = (self.rect.center[0], pos_y)

        # mata o elemento se ele estiver fora dos limites da tela
        self.check_borders()


class Shield(Enemy):
    """ Classe do inimigo Shield
    Herda de Enemy.
    """

    def __init__(self, position, lives=4, speed=.35, image=None, size=(50, 50), color='G'):
        """Shield construtor
        :param position: a posição inicial do elemento.
        :type position: list
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: int
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param size: o tamanho do spider
        :type size: tuple
        :param color: cor do spider, utilizado para escolher a imagem
        :type color: string
        """

        # define a imagem padrão
        image = f"inimigo4{color}.png" if not image else image

        # chama ElementSprite.__init__() e define valores iniciais de objetos lógicos
        super().__init__(position, lives, speed, image, size)
        self.enemy = None
        self.enemyposx = 0
        self.enemyposy = 0
        self.shield = True

    def choose_rand_enemy(self, enemylist):
        """ Escolhe um inimigo aleatório na lista de inimigos vivos, confere se sua posição está acima do Shield e se o inimigo já não está sendo protegido por outro escudo
        :param enemylist: lista de inimigos ativos
        :type enemylist: list
        """

        if len(enemylist) > 0:
            enemy = random.choice(enemylist)[0]
            if not enemy.shield and self.rect.center[1] > enemy.rect.center[1]:
                self.enemy = enemy
                self.enemy.shield = True
        else:
            self.enemy = None

    def update(self, dt, playerposx, enemylist, lst=None, lst2=None):
        """ Atualiza a posição e situação do Shield
        :param dt: variação do tempo
        :type dt: int
        :param playerposx: posição do jogador
        :type playerposx: int
        :param enemylist: lista dos inimigos vivos
        :type enemylist: list
        :param lst: lista de todos os elementos ativos: inimigos, tiros do player e tiros dos inimigos
        :type lst: list
        """

        # atualiza a situação quanto à lista de inimigos, usando o choose_rand_enemy
        # se já houver inimigo selecionado, pega sua posição
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

        # Define a posição e movimentação do Shield, posicionando-o abaixo do inimigo aleatório selecionado
        pos_y = self.rect.center[1]

        if self.enemyposx - self.rect.center[0] > 5:
            pos_x = self.rect.center[0] + 1 * self.speed*dt
        elif self.enemyposx - self.rect.center[0] < -5:
            pos_x = self.rect.center[0] - 1 * self.speed*dt
        else:
            pos_x = self.enemyposx
        if (self.rect.center[1] - self.enemyposy) < 50:
            pos_y += self.direction[1] * self.speed * \
                dt
        elif (self.rect.center[1] - self.enemyposy) > 200:
            pos_y -= self.direction[1] * self.speed * \
                dt
        elif (self.rect.center[1] - self.enemyposy) > 50:
            pos_y -= self.direction[1] * self.speed * \
                dt
        self.rect.center = (pos_x, pos_y)

        # mata o elemento se ele estiver fora dos limites da tela
        self.check_borders()


class BossSpider(Enemy):
    """ Classe do Boss Spider.
    Herda de Enemy"""

    def __init__(self, position, lives=30, speed=.35, image=None, size=(160, 160), color=None):
        """BossSpider construtor
        :param position: a posição inicial do elemento.
        :type position: list
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: int
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param size: o tamanho do spider
        :type size: tuple
        :param color: cor do spider, utilizado para escolher a imagem. Default None
        :type color: string
        """

        # define a imagem padrão
        image = "boss1G.png" if not image else image

        # chama ElementSprite.__init__()
        super().__init__(position, lives, speed, image, size)
        self.id = "boss"

    def update(self, dt, playerposx, enemies, lst=None, lst2=None):
        """ Atualiza a posição e situação do elemento
        :param dt: variação do tempo
        :type dt: int
        """

        # define movimento do Boss Spider, tornando seu movimento cíclico, ou seja, ao sair na tela embaixo, ele retorna em cima
        pos_y = self.rect.center[1] + self.direction[1] * self.speed*dt
        if playerposx - self.rect.center[0] > 0:
            pos_x = self.rect.center[0] + 1 * self.speed*dt/2
        else:
            pos_x = self.rect.center[0] - 1 * self.speed*dt/2
        if pos_x < 0:
            pos_x = 640
        elif pos_x > 640:
            pos_x = 0
        if pos_y < 0:
            pos_y = 640
        elif pos_y > 640:
            pos_y = 0
        self.rect.center = (pos_x, pos_y)


class BossShooter(Enemy):
    """ Classe do Boss Shooter
    Herda de Enemy.
    """

    def __init__(self, position, lives=40, speed=.35, image=None, size=(145, 140), color=None):
        """BossShooter construtor
        :param position: a posição inicial do elemento.
        :type position: list
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: int
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param size: o tamanho do spider
        :type size: tuple
        :param color: cor do spider, utilizado para escolher a imagem. Default None
        :type color: string
        """

        # define a imagem padrão
        image = "boss2Y.png" if not image else image

        # chama ElementSprite.__init__() e define valores iniciais de objetos lógicos
        super().__init__(position, lives, speed, image, size)
        self.direction = (1, 0)
        self.shtcounter = 0
        self.color = color
        self.id = "boss"

    def update(self, dt, playerposx, enemies, lst=None, lst2=None):
        """ Atualiza a posição e situação do elemento
        :param dt: variação do tempo
        :type dt: int
        """

        # posição e movimento, fixando em y=200 definindo sua movimentação de um lado para o outro da tela
        pos_x = self.rect.center[0]
        pos_y = self.rect.center[1]
        if pos_y < 200:
            pos_y += self.speed*dt
        if pos_x >= 580:
            self.direction = (-0.71, 0)
            self.speed *= 1.2
        elif pos_x <= 40:
            self.direction = (1, 0)
            self.speed *= 1.2
        pos_x += self.direction[0]*self.speed*dt/4
        self.rect.center = (pos_x, pos_y)

        # definindo frequência de tiros do Boss Shooter
        if self.shtcounter > 60:
            self.shoot(lst)
            self.shtcounter = 0
        self.shtcounter += 1

        # mata o elemento se ele estiver fora dos limites da tela
        self.check_borders()

    def shoot(self, shoots):
        """Define os efeitos do tiro do Boss Shooter
        :param shoots: tiros do Boss Shooter
        :type shoots: list
        """
        # som do tiro
        play_sound("Enemy Shoot.ogg")
        # cria os tiros (laser), mudando a imagem padrão da classe Laser e o adiciona à lista de tiros
        laser1 = Laser((self.rect.center[0], self.rect.top),
                       image=f'tiroinimigoY.png', direction=(0, 1))
        laser2 = Laser((self.rect.center[0], self.rect.top),
                       image=f'tiroinimigoY.png', direction=(1, 1), angle=45)
        laser3 = Laser((self.rect.center[0], self.rect.top),
                       image=f'tiroinimigoY.png', direction=(-1, 1), angle=-45)
        lst = [[laser1, pygame.sprite.RenderPlain(laser1)], [laser2, pygame.sprite.RenderPlain(
            laser2)], [laser3, pygame.sprite.RenderPlain(laser3)]]
        for laser in lst:
            shoots.append(laser)


class BossBomb(Enemy):
    """ Classe do Boss Bomb
    Herda de Enemy.
    """

    def __init__(self, position, lives=50, speed=.35, image=None, size=(150, 140), color=None):
        """BossBomb construtor
        :param position: a posição inicial do elemento.
        :type position: list
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: int
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param size: o tamanho do spider
        :type size: tuple
        :param color: cor do spider, utilizado para escolher a imagem. Default None
        :type color: string
        """

        # define a imagem padrão
        image = "Boss3R.png" if not image else image

        # chama ElementSprite.__init__() e define valores iniciais de objetos lógicos
        super().__init__(position, lives, speed, image, size)
        self.direction = (1, 0)
        self.shtcounter = 0
        self.color = color
        self.id = "boss"

    def update(self, dt, playerposx, enemies, lst=None, lst2=None):
        """ Atualiza a posição e situação do shooter
        :param dt: variação do tempo
        :type dt: int
        :param playerposx: posição do jogador
        :type playerposx: int
        :param enemies: lista dos inimigos vivos
        :type enemies: list
        :param lst: lista de todos os tiros do shooter. Default None
        :type lst: list
        """

        # posição e movimento, fixando em y=50 definindo sua movimentação de um lado para o outro da tela
        pos_x = self.rect.center[0]
        pos_y = self.rect.center[1]
        if (pos_x <= 60) and (pos_y >= 580):
            self.direction = (0, -0.71)
        elif (pos_x <= 60) and (pos_y <= 60):
            self.direction = (1, 0)
        elif (pos_x >= 580) and (pos_y >= 580):
            self.direction = (-0.71, 0)
        elif (pos_x >= 580) and (pos_y <= 60):
            self.direction = (0, 1)
        pos_x += self.direction[0]*self.speed*dt/2
        pos_y += self.direction[1]*self.speed*dt/2
        self.rect.center = (pos_x, pos_y)

        if (pos_x > 318 and pos_x < 322) or (pos_y > 318 and pos_y < 322):
            print("in range")
            self.explode(lst2)

    def explode(self, explosions):
        explosion1 = Explosion(
            (320, self.rect.center[1]), type='1', color='R', hits=[self])
        explosion2 = Explosion(
            (self.rect.center[0], 320), type='2', color='R', hits=[self])
        explosions.append(
            [explosion1, pygame.sprite.RenderPlain(explosion1)])
        explosions.append(
            [explosion2, pygame.sprite.RenderPlain(explosion2)])


class BossShield(Enemy):
    """ Classe do Boss Shield
    Herda de Enemy.
    """

    def __init__(self, position, lives=50, speed=.35, image=None, size=(145, 140), color=None):
        """Boss Shield construtor
        :param position: a posição inicial do elemento.
        :type position: list
        :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
        :type lives: int
        :param speed: a velocidade inicial do elemento em ambos os eixos
        :type speed: float
        :param image: a imagem do elemento. Default None
        :type image: string
        :param size: o tamanho do spider
        :type size: tuple
        :param color: cor do spider, utilizado para escolher a imagem. Default None
        :type color: string
        """

        # define a imagem padrão
        image = "boss4B.png" if not image else image

        # chama ElementSprite.__init__() e define valores iniciais de objetos lógicos
        super().__init__(position, lives, speed, image, size)
        self.direction = (1, 0)
        self.shtcounter = 0
        self.color = color
        self.id = "boss"

    def update(self, dt, playerposx, enemies, lst=None, lst2=None):
        """ Atualiza a posição e situação do Bpss Shield
        :param dt: variação do tempo
        :type dt: int
        :param playerposx: posição do jogador
        :type playerposx: int
        :param enemies: lista dos inimigos vivos
        :type enemies: list
        :param lst: lista de todos os tiros do shooter. Default None
        :type lst: list
        """

        # posições do Boss Shield
        pos_x = self.rect.center[0]
        pos_y = self.rect.center[1]

        # movimentação do Boss Shield seguindo o jogador
        if pos_y < 200:
            pos_y += self.speed*dt
        if playerposx - self.rect.center[0] > 0:
            pos_x = self.rect.center[0] + 1 * self.speed*dt/4
        else:
            pos_x = self.rect.center[0] - 1 * self.speed*dt/4
        if pos_x < 0:
            pos_x = 640
        elif pos_x > 640:
            pos_x = 0
        self.rect.center = (pos_x, pos_y)


# class Trojan(Enemy):
#     """ Classe Trojan
#     Herda de Enemy
#     """

#     def __init__(self, position, lives=1000, speed=.35, image=None, size=(640, 160), color=None):
#         """ Trojan construtor.
#         :param position: a posição inicial do elemento.
#         :type position: lista
#         :param lives: quantas vezes o elemento pode ser atingido antes de morrer.
#         :type lives: inteiro (?)
#         :param speed: a velocidade inicial do elemento em ambos os eixos
#         :type speed: lista
#         :param image: a imagem do elemento. A classe possui um valor padrão  que é sobrescrito quando este parâmetro não é "None"
#         :type image: string
#         :param new_size: o tamanho desejado do sprite. Veja ElementSprite.scale()
#         :type new_size: lista
#         """

#         # define a imagem padrão
#         image = "troia1.png" if not image else image

#         # chama ElementSprite.__init__() e define valores iniciais de objetos lógicos
#         super().__init__(position, lives, speed, image, size)
#         self.direction = (1, 0)
#         self.shtcounter = 0
#         self.color = color
#         self.shield = True
#         self.id = "boss"
#         self.sprite = 1
#         self.spr_counter = 0

#     def update(self, dt, playerposx, enemies, lst=None, lst2=None):
#         """ Atualia a posição do Trojan
#         :param dt: variação do tempo
#         :type dt: int
#         """

#         pos_x = 320
#         pos_y = self.rect.center[1]
#         if pos_y < 80:  # 640x160
#             pos_y += self.speed*dt  # po
#         self.rect.center = (pos_x, pos_y)

#         # definindo frequência de tiros do Trojan
#         if self.shtcounter > 20:
#             self.shoot(lst)
#             self.shtcounter = 0
#         self.shtcounter += 1
#         self.animate()

#     def shoot(self, shoots):
#         """Define os efeitos do tiro do Trojan
#         :param shoots: tiros do Trojan
#         :type shoots: list
#         """
#         # som do tiro
#         play_sound("Enemy Shoot.ogg")
#         # cria o tiro (laser), mudando a imagem padrão da classe Laser e o adiciona à lista de tiros
#         laser = Laser((random.randint(0, 640), self.rect.top),
#                       image=f'tiroinimigo{self.color}.png', direction=(0, 1))
#         shoots.append([laser, pygame.sprite.RenderPlain(laser)])

#     def animate(self):
#         if self.lives > 500:
#             if self.spr_counter < 10:
#                 self.set_image(f'troia{self.sprite}.png', self.size)
#                 self.sprite += 1
#                 if self.sprite > 2:
#                     self.sprite = 1:
#             else:
#                 self.spr_counter = 0
#         else:
#             if self.spr_counter < 10:
#                 self.set_image(f'troia{self.sprite}.png', self.size)
#                 self.sprite += 1
#                 if self.sprite > 4:
#                     self.sprite = 3:
#             else:
#                 self.spr_counter = 0
