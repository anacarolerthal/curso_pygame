import pygame
from pygame.locals import (DOUBLEBUF,
                           FULLSCREEN,
                           KEYDOWN,
                           KEYUP,
                           K_LEFT,
                           K_RIGHT,
                           QUIT,
                           K_ESCAPE, K_UP, K_DOWN, K_RCTRL, K_LCTRL, K_SPACE
                           )
from background import Background
from elements import *
import random
import time
import os

_sound_library = {}  # Biblioteca de efeitos sonoros


def play_sound(path):  # Função que toca os efeitos sonoros
    """Função que toca efeitos sonoros presentes na pasta /songs
        param path: nome do arquivo do efeito sonoro
        type path: string
    """
    global _sound_library
    sound = _sound_library.get(path)
    if sound == None:
        # Corrige path para qualquer OS
        correctpath = os.path.join('songs', path)
        sound = pygame.mixer.Sound(correctpath)
        _sound_library[path] = sound
    sound.play()


class Game:
    def __init__(self, size=(640, 640), fullscreen=False):
        """ Cria o objeto que irá controlar o jogo

        :param size: tamanho desejado da tela do jogo
        :type size: tuple
        :param fullscreen: define se o jogo terá tela cheia ou não
        :type fullscreen: boolean. Default False
        """
        self.elements = {}  # cria o dicionário com todas os elementos do jogo
        self.enemies = []  # cria a lista de todos os inimigos
        self.shoots = []  # cria a lista com os projécteis do jogador
        self.enemy_shoots = []  # cria a lista com todos os projécteis inimigos
        self.power_ups = []  # cria a lista de power-ups
        self.explosions = []  # cria a lista de explosões
        self.enemy_counter = 45  # contador usado para a lógica de spawn de inimigos
        self.power_up_counter = 0  # contador usado para a lógica de spawn de power-ups
        # timer de colisão para que o jogador não tome dano várias vezes de uma mesma colisão
        self.colcounter = 0
        self.start = True
        self.color = 'G'  # define a cor dos elementos da primeira fase
        # lista ordenada de cores de cada fase
        self.color_list = ['G', 'Y', 'R', 'B', 'P']
        self.level = 0  # define a fase inicial
        # lista de dicionários para definir a presença dos inimigos nas fases
        self.waves = [{"spider": 1, "shooter": 0, "bomb": 0, "shield": 0}, {"spider": 1, "shooter": 1, "bomb": 0, "shield": 0}, {
            "spider": 1, "shooter": 1, "bomb": 1, "shield": 0}, {"spider": 1, "shooter": 1, "bomb": 1, "shield": 1}]
        self.set_current_wave()
        pygame.init()  # inicia o módulo pygame

        # seta as flags de renderização
        flags = DOUBLEBUF | FULLSCREEN if fullscreen else DOUBLEBUF

        # cria o display
        self.screen = pygame.display.set_mode(size, flags)

        # cria o plano de fundo
        self.background = Background(f'fundo{self.color}.png')

        # seta o titulo da janela
        pygame.display.set_caption('PC Virus Shooter')
        pygame.mouse.set_visible(0)  # deixa o cursor do mouse invisivel
        self.font = pygame.font.Font(os.path.join("fonts", 'Pixels.ttf'), 72)
        self.font_love = pygame.font.Font(
            os.path.join("fonts", 'pixel-love.ttf'), 48)  # configura a fonte para displays
        self.run = True

        self.loop()  # roda o jogo

    def update_elements(self, dt):
        """ Atualiza diversos aspectos do jogo

        :param dt: variação de tempo
        :type dt: int
        """

        self.background.update(dt)
        for enemy in self.enemies:  # atualiza inimigos pela lista de inimigos vivos
            enemy[0].update(dt, self.player.rect.center[0],
                            self.enemies, self.enemy_shoots)
        for shoot in self.shoots:  # atualiza tiros do player pela lista desses
            shoot[0].update(dt)
        for shoot in self.enemy_shoots:  # atualiza tiros dos inimigos pela lista desses
            shoot[0].update(dt)
        for power_up in self.power_ups:  # atualiza power ups pela lista desses
            power_up[0].update(dt)
        for explosion in self.explosions:  # atualiza explosoes pela lista dessas
            explosion[0].update(dt)

    def draw_elements(self):
        """ Desenha elementos na tela
        """
        self.background.draw(self.screen)
        for explosion in self.explosions:  # desenha explosoes
            explosion[1].draw(self.screen)
        for element in self.elements.values():
            element.draw(self.screen)
        for enemy in self.enemies:  # desenha inimigos
            enemy[1].draw(self.screen)
        for shoot in self.shoots:  # desenha tiros do player
            shoot[1].draw(self.screen)
        for shoot in self.enemy_shoots:  # desenha tiros dos inimigos
            shoot[1].draw(self.screen)
        for power_up in self.power_ups:  # desenha power ups
            power_up[1].draw(self.screen)

        if self.player.shield:  # desenha shield se houver
            self.player.shield[1].draw(self.screen)

    def handle_events(self, event, dt=1000):
        """ Lida com os eventos na fila de eventos 
        Na prática, diz respeito ao controle do Player pelo usuário e pelo quit no jogo
        """
        # lida com a janela de quit ("x" no canto superior direito)
        if event.type == pygame.QUIT or self.player.isdead:
            self.run = False
        # lida com inputs do teclado com funções do Pygame
        if event.type in (KEYDOWN,):
            key = event.key
            if key == K_ESCAPE:  # lida com a saída do jogo pelo "esc" do teclado
                self.run = False

        # if self.player.score == 5:
        #     self.change_music("TrojanTheme.ogg")
        #     self.player.score += 5
        #     self.level_changer('R')

        if self.player.score == self.level*10 + 10:
            self.level_changer()
            enemy = BossShield((320, 10), color=self.color)
            self.enemies.append([enemy, pygame.sprite.RenderPlain(enemy)])

    def set_current_wave(self):
        """"""
        new_current_wave = []
        for enemy in self.waves[self.level]:
            for i in range(self.waves[self.level][enemy]):
                new_current_wave.append(enemy)
        self.current_wave = new_current_wave

    def start_music(self, music):
        pygame.mixer.init()
        song = os.path.join('songs', music)
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(-1)

    def change_music(self, music):
        pygame.mixer.music.stop()
        song = os.path.join('songs', music)
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(-1)

    def update_interface(self):
        scoretext = self.font.render(
            "Score = "+str(self.player.get_score()), 1, (0, 0, 0))
        self.screen.blit(scoretext, (15, 570))
        lifestext = self.font_love.render(
            "@"*self.player.get_lives(), 1, (0, 0, 0))
        self.screen.blit(lifestext, (10, 540))

    def spawn(self):
        if self.enemy_counter > 75:
            pos_x = random.randint(0, 640)
            enemy_n = random.randint(0, len(self.current_wave)-1)
            enemy_type = self.current_wave[enemy_n]
            if enemy_type == "spider":
                enemy = Spider([pos_x, -25], color=self.color)
            elif enemy_type == "shooter":
                enemy = Shooter([pos_x, -25], color=self.color)
            elif enemy_type == "bomb":
                enemy = Bomb([pos_x, -25], color=self.color)
            elif enemy_type == "shield":
                enemy = Shield([pos_x, 0], color=self.color)
            self.enemies.append([enemy, pygame.sprite.RenderPlain(enemy)])
            self.enemy_counter = 0
        else:
            self.enemy_counter += 1
        if self.power_up_counter > 180:
            pos_x = random.randint(0, 640)
            pwup_type = random.randint(1, 4)
            power_up = PowerUp([pos_x, -25], power=pwup_type)
            self.power_ups.append(
                [power_up, pygame.sprite.RenderPlain(power_up)])
            self.power_up_counter = 0
        else:
            self.power_up_counter += 1

    def handle_collision(self):
        for enemy in self.enemies:
            plyr_collision = self.player.rect.colliderect(enemy[0].rect)
            if plyr_collision and self.colcounter <= 0:
                print('ui')
                self.player.got_hit()
                enemy[0].got_hit()
                if enemy[0].get_lives() <= 0:
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                self.colcounter = 60
            for shoot in self.shoots:
                enemy_collision = enemy[0].rect.colliderect(shoot[0].rect)
                if enemy_collision:
                    enemy[0].got_hit()
                    if enemy[0].get_lives() <= 0:
                        self.player.add_score()
                        if enemy[0].get_id() == "bomb":
                            # tinha que colocar um (320, y) em outro em (x,320)
                            print('entrou')
                            explosion1 = Explosion(  # pra centralizar
                                (320, enemy[0].rect.center[1]), type='1', color=self.color)
                            explosion2 = Explosion(
                                (enemy[0].rect.center[0], 320), type='2', color=self.color)
                            self.explosions.append([explosion1, pygame.sprite.RenderPlain(
                                explosion1)])
                            self.explosions.append([explosion2, pygame.sprite.RenderPlain(
                                explosion2)])
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                    self.shoots.remove(shoot)
            # Explosions:
            for explosion in self.explosions:
                # explosion hits enemy?
                enemy_collision = enemy[0].rect.colliderect(
                    explosion[0].rect)
                if enemy_collision and enemy[0] not in explosion[0].hits:
                    enemy[0].got_hit()
                    if enemy[0].get_lives() <= 0:
                        self.player.add_score()
                        if enemy[0].get_id() == "bomb":
                            # tinha que colocar um (320, y) em outro em (x,320)
                            print('entrou')
                            explosion1 = Explosion(  # pra centralizar
                                (320, enemy[0].rect.center[1]), type='1', color=self.color)
                            explosion2 = Explosion(
                                (enemy[0].rect.center[0], 320), type='2', color=self.color)
                            self.explosions.append([explosion1, pygame.sprite.RenderPlain(
                                explosion1)])
                            self.explosions.append([explosion2, pygame.sprite.RenderPlain(
                                explosion2)])
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                    explosion[0].hits.append(enemy[0])
                # explosion hits player?
                plyr_collision = self.player.rect.colliderect(
                    explosion[0].rect)
                if plyr_collision and self.colcounter <= 0 and self.player not in explosion[0].hits:
                    self.player.got_hit()
                    self.colcounter = 60
                    # explosion[0].hits.append(self.player)
                if explosion[0].count > explosion[0].duration:
                    self.explosions.remove(explosion)
        for shoot in self.enemy_shoots:
            plyr_collision = self.player.rect.colliderect(shoot[0].rect)
            if plyr_collision and self.colcounter <= 0:
                print('ui')
                self.player.got_hit()
                self.enemy_shoots.remove(shoot)
                self.colcounter = 60

        if self.colcounter > 0:
            self.colcounter -= 1

        for power_up in self.power_ups:
            plyr_collision = self.player.rect.colliderect(power_up[0].rect)
            if plyr_collision:
                print(power_up[0].get_power())
                self.player.set_power_up(power_up[0].get_power())
                power_up[0].kill()
                self.power_ups.remove(power_up)

    def garbage_collector(self):
        for lst in (self.enemies, self.shoots, self.enemy_shoots):
            for entity in lst:
                if entity[0].check_borders():
                    lst.remove(entity)

    def level_changer(self):
        self.level += 1
        self.color = self.color_list[self.level]
        self.set_current_wave()
        self.background = Background(f'fundo{self.color}.png')
        self.enemies.clear()
        self.enemy_shoots.clear()

    def loop(self):
        """ Loop principal do jogo
        """
        clock = pygame.time.Clock()  # cria o relógio do jogo
        dt = 16  # define a efetiva velocidade do jogo
        self.player = Player([320, 540], 4)
        self.elements['player'] = pygame.sprite.RenderPlain(
            self.player)  # prepara o sprite do Player
        self.start_music("LevelTheme.ogg")
        while self.run:
            clock.tick(1000 / dt)
            event = pygame.event.poll()
            # Handles the user interaction
            self.player.update(dt)
            self.player.shoot(event, self.shoots)
            self.player.explode(event, self.explosions)
            self.handle_events(event, dt)
            self.handle_collision()
            if self.start:
                self.spawn()
                # Handles the position and colision updates
                self.update_elements(dt)

            # Draw the elements on their new positions. Right now only works for the background
            # The elements are drawn on the backbuffer, which is later on flipped to become the frontbuffer
            self.draw_elements()
            self.garbage_collector()
            self.update_interface()
            pygame.display.flip()
        pygame.quit()  # kill the program


class Player(Spaceship):
    def __init__(self, position, lives=3, speed=.5, image=None, new_size=(27, 36)):
        if not image:
            image = "nave1.png"
        super().__init__(position, lives, speed, image, new_size)
        self.direction = (0, 0)
        self.vel = (0, 0)
        self.max_vel = .5
        self.acc = (0, 0)
        self.score = 0
        self.bombs = 50
        self.size = new_size
        self.power_ups = [False, False, False, False]
        self.shield = None
        self.spd_counter = 0
        self.sht_counter = 0
        self.isdead = False

    def update(self, dt):
        new_acc = [0, 0]
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            new_acc[0] -= 1
        if keys[K_RIGHT]:
            new_acc[0] += 1
        if keys[K_UP]:
            new_acc[1] -= 1
        if keys[K_DOWN]:
            new_acc[1] += 1

        new_acc = tuple(new_acc)
        if new_acc != self.acc:
            self.acc = new_acc
            if self.acc[0] == 0:
                self.set_image('nave1.png', self.size)
            elif self.acc[0] == 1:
                self.set_image('nave2.png', self.size)
            elif self.acc[0] == -1:
                self.set_image('nave3.png', self.size)

        self.vel = (self.vel[0]+self.acc[0]*dt/100,
                    self.vel[1]+self.acc[1]*dt/100)
        self.normalize_vel()

        if self.spd_counter > 360:
            self.power_ups[0] = False
            self.spd_counter = 0

        if self.power_ups[0]:
            mtp = 1.3
            self.spd_counter += 1
        else:
            mtp = 1

        pos_x = self.rect.center[0] + self.vel[0]*dt*mtp
        pos_y = self.rect.center[1] + self.vel[1]*dt*mtp

        # Reduce the velocity, as of friction
        self.vel = (self.vel[0]*9/10, self.vel[1]*9/10)
        if abs(self.vel[0]) < 0.01:
            self.vel = (0, self.vel[1])
        if abs(self.vel[1]) < 0.01:
            self.vel = (self.vel[0], 0)

        if pos_x < 0:
            pos_x = 640
        elif pos_x > 640:
            pos_x = 0
        if pos_y < 0:
            pos_y = 0
        elif pos_y > 640:
            pos_y = 640
        self.rect.center = (pos_x, pos_y)

        if self.sht_counter > 360:
            self.power_ups[1] = False
            self.sht_counter = 0

        if self.power_ups[1]:
            self.sht_counter += 1

        if self.shield:
            self.shield[0].update(dt)

    def shoot(self, event, shoots):
        if event.type in (KEYDOWN,):
            key = event.key
            if key == K_LCTRL:
                play_sound("PlayerShoot.ogg")
                if not self.power_ups[1]:
                    laser = Laser((self.rect.center[0], self.rect.top))
                    shoots.append([laser, pygame.sprite.RenderPlain(laser)])
                else:
                    laser1 = Laser((self.rect.center[0], self.rect.top))
                    laser2 = Laser(
                        (self.rect.center[0], self.rect.top), direction=(1, -1), angle=-45)
                    laser3 = Laser(
                        (self.rect.center[0], self.rect.top), direction=(-1, -1), angle=45)
                    lst = [[laser1, pygame.sprite.RenderPlain(laser1)], [laser2, pygame.sprite.RenderPlain(
                        laser2)], [laser3, pygame.sprite.RenderPlain(laser3)]]  # Cria três lasers
                    for laser in lst:
                        shoots.append(laser)

    def explode(self, event, explosions):
        if event.type in (KEYDOWN,):
            key = event.key
            if key == K_SPACE:
                if self.bombs > 0:
                    explosion1 = Explosion(
                        (320, self.rect.center[1]), type='1', color='R', hits=[self])
                    explosion2 = Explosion(
                        (self.rect.center[0], 320), type='2', color='R', hits=[self])
                    explosions.append(
                        [explosion1, pygame.sprite.RenderPlain(explosion1)])
                    explosions.append(
                        [explosion2, pygame.sprite.RenderPlain(explosion2)])
                    self.bombs -= 1

    def normalize_vel(self):  # função usada para lidar com a movimentação
        abs_vel = (self.vel[0]**2+self.vel[1]**2)**.5
        if abs_vel > self.max_vel:
            self.vel = (self.vel[0]/abs_vel*self.max_vel,
                        self.vel[1]/abs_vel*self.max_vel)

    def got_hit(self):
        if self.shield:
            self.power_ups[3] = False
            self.shield = None
        else:
            self.lives -= 1
        if self.lives <= 0:
            print(self.score)
            self.isdead = True

    def get_pos(self):
        return (self.rect.center[0], self.rect.center[1])

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score
        print(self.score)

    def set_power_up(self, power_up):
        if power_up == 1:
            self.spd_counter = 0
        elif power_up == 2:
            self.sht_counter = 0
        elif power_up == 3:
            if self.bombs < 3:
                self.bombs = 3
        elif power_up == 4 and not self.power_ups[3]:
            shield = ShieldPowerUp(
                (self.rect.center[0], self.rect.center[1]), player=self)
            self.shield = [shield, pygame.sprite.RenderPlain(shield)]

        self.power_ups[power_up - 1] = True  # Array começa em 0

    def add_score(self):
        self.score += 1


if __name__ == '__main__':
    G = Game()
