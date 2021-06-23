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
import math

_sound_library = {}  # biblioteca de efeitos sonoros


def play_sound(path):  # função que toca os efeitos sonoros
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
        self.blocks = []
        self.enemy_shoots = []  # cria a lista com todos os projécteis inimigos
        self.power_ups = []  # cria a lista de power-ups
        self.explosions = []  # cria a lista de explosões
        self.enemy_counter = 45  # contador usado para a lógica de spawn de inimigos
        self.power_up_counter = 0  # contador usado para a lógica de spawn de power-ups
        # timer de colisão para que o jogador não tome dano várias vezes de uma mesma colisão
        self.colcounter = 0
        self.start = False
        self.color = 'G'  # define a cor dos elementos da primeira fase
        # lista ordenada de cores de cada fase
        self.color_list = ['G', 'Y', 'R', 'B', 'P']
        self.color_list.append(random.choice(self.color_list))
        self.level = 0  # define a fase inicial
        self.last_score = 0
        # lista de dicionários para definir a presença dos inimigos nas fases
        self.waves = [{"spider": 1, "shooter": 0, "bomb": 0, "shield": 0}, {"spider": 2, "shooter": 1, "bomb": 0, "shield": 0}, {
            "spider": 2, "shooter": 2, "bomb": 1, "shield": 0}, {"spider": 4, "shooter": 3, "bomb": 1, "shield": 2}, {
            "spider": 2, "shooter": 4, "bomb": 2, "shield": 3}, {"spider": 2, "shooter": 4, "bomb": 2, "shield": 3}, {
            "spider": 2, "shooter": 4, "bomb": 2, "shield": 3}]
        self.set_current_wave()
        self.scoreboss = 0
        self.bosscounter = 0
        self.true_score = 0
        self.temp_score = 0
        pygame.init()  # inicia o módulo pygame

        # seta as flags de renderização
        flags = DOUBLEBUF | FULLSCREEN if fullscreen else DOUBLEBUF

        # cria o display
        self.screen = pygame.display.set_mode(size, flags)

        # cria o plano de fundo
        self.background = Background(f'menu.png')

        # seta o título da janela
        pygame.display.set_caption('PC Virus Shooter')
        pygame.mouse.set_visible(0)  # deixa o cursor do mouse invisível
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
                            self.enemies, lst=self.enemy_shoots)
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
        for enemy in self.enemies:  # desenha inimigos
            enemy[1].draw(self.screen)
        for shoot in self.shoots:  # desenha tiros do player
            shoot[1].draw(self.screen)
        for shoot in self.enemy_shoots:  # desenha tiros dos inimigos
            shoot[1].draw(self.screen)
        for power_up in self.power_ups:  # desenha power ups
            power_up[1].draw(self.screen)
        for block in self.blocks:  # desenha power ups
            block[1].draw(self.screen)
        for element in self.elements.values():
            element.draw(self.screen)
        if self.player.shield:  # desenha shield se houver
            self.player.shield[1].draw(self.screen)

    def summon_boss(self):
        if self.bosscounter == 0:
            enemy = BossSpider((320, 10), color=self.color)
            self.enemies.append([enemy, pygame.sprite.RenderPlain(enemy)])
        elif self.bosscounter == 1:
            enemy = BossShooter((320, 10), color=self.color)
            self.enemies.append([enemy, pygame.sprite.RenderPlain(enemy)])
        elif self.bosscounter == 2:
            enemy = BossBomb((320, 60), color=self.color)
            self.enemies.append([enemy, pygame.sprite.RenderPlain(enemy)])
        elif self.bosscounter == 3:
            enemy = BossShield((320, 10), color=self.color)
            self.enemies.append([enemy, pygame.sprite.RenderPlain(enemy)])

    def handle_events(self, event, dt=1000):
        """ Lida com os eventos na fila de eventos
        Na prática, diz respeito ao controle do Player pelo usuário e pelo quit no jogo
        """
        # lida com a janela de quit ("x" no canto superior direito)
        if event.type == pygame.QUIT:
            self.run = False
        # lida com inputs do teclado com funções do Pygame
        if event.type in (KEYDOWN,):
            key = event.key
            if key == K_ESCAPE:  # lida com a saída do jogo pelo "esc" do teclado
                self.run = False

        #
        if self.true_score >= self.level*100 + 20:
            self.temp_score = self.true_score
            self.summon_boss()
            self.true_score = 0

        if self.scoreboss == 1:
            self.level_changer()
            self.scoreboss = 0
            self.bosscounter += 1
            self.true_score = self.temp_score

    def set_current_wave(self):
        """ Define a presença de cada inimigo nas fases, de acordo com a lista de dicionários definida
        """
        new_current_wave = []
        for enemy in self.waves[self.level]:
            for i in range(self.waves[self.level][enemy]):
                new_current_wave.append(enemy)
        self.current_wave = new_current_wave

    def start_music(self, music):
        """ Inicia a música por comandos próprios do Pygame
        """
        pygame.mixer.init()
        song = os.path.join('songs', music)
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(-1)

    def change_music(self, music):
        """ Muda a música por comandos próprios do Pygame
        """
        pygame.mixer.music.stop()
        song = os.path.join('songs', music)
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(-1)

    def update_interface(self):
        """ Faz o update da interface do jogo
        """
        # atualiza o texto do Score
        if self.player.shield:
            heart_color = (0, 181, 204)
        else:
            heart_color = (0, 0, 0)

        scoretext = self.font.render(
            "Score = "+str(self.player.get_score()), 1, (0, 0, 0))
        self.screen.blit(scoretext, (15, 570))

        bombtext = self.font.render(
            str(self.player.get_bombs()), 1, (0, 0, 0))
        self.screen.blit(bombtext, (500, 570))

        # atualiza o display de vidas
        lifestext = self.font_love.render(
            "@"*self.player.get_lives(), 1, heart_color)
        self.screen.blit(lifestext, (10, 540))

    def spawn(self):
        """ Define a geração dos elementos
        """

        # Geração de inimigos
        if self.enemy_counter > 75:  # tempo para spawn
            pos_x = random.randint(0, 640)  # aleatoriza a posição x do inimigo
            enemy_n = random.randint(0, len(self.current_wave)-1)
            # aleatoriza qual inimigo será gerado de acordo com os possíveis para o nível
            enemy_type = self.current_wave[enemy_n]
            # definição da posições e cor de cada inimigo gerado
            if enemy_type == "spider":
                enemy = Spider([pos_x, -25], color=self.color)
            elif enemy_type == "shooter":
                enemy = Shooter([pos_x, -25], color=self.color)
            elif enemy_type == "bomb":
                enemy = Bomb([pos_x, -25], color=self.color)
            elif enemy_type == "shield":
                enemy = Shield([pos_x, 0], color=self.color)
            # adiciona o inimigo gerado à lista de inimigos
            self.enemies.append([enemy, pygame.sprite.RenderPlain(enemy)])
            self.enemy_counter = 0
        else:
            mult = 1
            if self.bosscounter >= 6:
                mult = math.log(self.truescore + self.bosscounter*100)/8

            self.enemy_counter += 1 * ((self.level/2)+1) * mult

        # Geração de power ups
        if self.power_up_counter > 180:  # tempo para spawn
            pos_x = random.randint(0, 640)  # aleatoriza a posição x do inimigo
            # aleatoriza qual powerup será gerado
            pwup_type = random.randint(1, 4)
            # define posições, tipo do powerup
            power_up = PowerUp([pos_x, -25], power=pwup_type)
            # adiciona o inimigo gerado à lista de inimigos
            self.power_ups.append(
                [power_up, pygame.sprite.RenderPlain(power_up)])
            self.power_up_counter = 0
        else:
            self.power_up_counter += 1

    def handle_collision(self):
        """ Lida com as colisões em geral
        """

        # lida com as colisões dos inimigos contra as explosões, o jogador e os tiros do jogador
        self.handle_enemy_collision()
        # lida com as colisões dos tiros dos inimigos contra o jogador
        self.handle_enemy_shot_collision()
        # lida com as colisões dos power ups contra o jogador
        self.handle_power_up_collision()

        for block in self.blocks:
            plyr_collision = self.player.rect.colliderect(block[0].rect)
            if plyr_collision:
                self.start_game(block[0].value)

        # diminui o contador de colisão do jogador
        if self.colcounter > 0:
            self.colcounter -= 1

    def handle_enemy_collision(self):
        """ Lida com as colisões do player com inimigos
        """
        for enemy in self.enemies:  # roda o bloco de código abaixo para todos o inimigos vivos
            # checa se o jogador colidiu com o inimigo em questão
            plyr_collision = self.player.rect.colliderect(enemy[0].rect)
            if plyr_collision and self.colcounter <= 0:
                print('ui')
                self.player.got_hit()
                enemy[0].got_hit()
                # remove o inimigo caso ele houver colisão
                if enemy[0].get_lives() <= 0:
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                        self.player.add_score()
                        self.true_score += 1
                        # tratamento especial para a bomba, que explode caso haja colisão
                        if enemy[0].get_id() == "boss":
                            self.scoreboss = 1  # define o scoreboss em 1 para possibilitar a passagem de nível
                            self.player.set_score(self.player.get_score() + 70)
                            self.true_score += 70
                        if enemy[0].get_id() == "bomb":
                            self.true_score += 1
                            self.handle_bomb_death(enemy)
                self.colcounter = 60
            for shoot in self.shoots:
                # checa se os tiros do jogador colidiram com o inimigo em questão
                enemy_collision = enemy[0].rect.colliderect(shoot[0].rect)
                if enemy_collision:
                    enemy[0].got_hit()
                    # caso as vidas cheguem a 0, chama funções de morte de cada inimigo e os remove da lista de inimigos ativos
                    if enemy[0].get_lives() <= 0:
                        self.true_score += 1
                        self.player.add_score()
                        if enemy[0].get_id() == "boss":
                            self.scoreboss = 1  # define o scoreboss em 1 para possibilitar a passagem de nível
                            self.player.set_score(self.player.get_score() + 70)
                        if enemy[0].get_id() == "bomb":
                            self.true_score += 1
                            self.handle_bomb_death(enemy)
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                    # remove o tiro da lista de tiros
                    self.shoots.remove(shoot)
            # explosões:
            for explosion in self.explosions:
                # colisão com o inimigo
                enemy_collision = enemy[0].rect.colliderect(
                    explosion[0].rect)
                if enemy_collision and enemy[0] not in explosion[0].hits:
                    enemy[0].got_hit()
                    if enemy[0].get_lives() <= 0:
                        self.player.add_score()
                        if enemy[0].get_id() == "bomb":
                            self.handle_bomb_death(enemy)
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                    explosion[0].hits.append(enemy[0])
                # colisão com o player
                plyr_collision = self.player.rect.colliderect(
                    explosion[0].rect)
                if plyr_collision and self.colcounter <= 0 and self.player not in explosion[0].hits:
                    self.player.got_hit()
                    # remove a explosão após o tempo
                    self.colcounter = 60
                if explosion[0].count > explosion[0].duration:
                    self.explosions.remove(explosion)

    def handle_enemy_shot_collision(self):
        """ Lida com a colisão do player com os tiros inimigos
        """
        for shoot in self.enemy_shoots:
            plyr_collision = self.player.rect.colliderect(shoot[0].rect)
            if plyr_collision and self.colcounter <= 0:
                self.player.got_hit()
                self.enemy_shoots.remove(shoot)
                self.colcounter = 60

    def handle_power_up_collision(self):
        """ Lida com a colisão do player com os power ups e implementa o poder
        """
        # define a colisão
        for power_up in self.power_ups:
            plyr_collision = self.player.rect.colliderect(power_up[0].rect)
            if plyr_collision:  # se ocorrer, implementa o power up
                print(power_up[0].get_power())
                self.player.set_power_up(power_up[0].get_power())
                power_up[0].kill()
                self.power_ups.remove(power_up)

    def handle_bomb_death(self, enemy):
        """ Lida com a colisão do player com os power ups e implementa o poder
        """

        explosion1 = Explosion(  # centraliza a explosão horizontal
            (320, enemy[0].rect.center[1]), type='1', color=self.color)
        explosion2 = Explosion(  # centraliza a explosão vertical
            (enemy[0].rect.center[0], 320), type='2', color=self.color)
        self.explosions.append([explosion1, pygame.sprite.RenderPlain(
            explosion1)])
        self.explosions.append([explosion2, pygame.sprite.RenderPlain(
            explosion2)])

    def garbage_collector(self):
        """ Remove da lista de inimigos vivos os que saíram da tela do jogo
        """
        for lst in (self.enemies, self.shoots, self.enemy_shoots):
            for entity in lst:
                if entity[0].check_borders():
                    lst.remove(entity)

    def level_changer(self):
        """ Define a mudança de nível
        """
        self.level += 1
        self.color = self.color_list[self.level]  # muda a cor padrão
        self.set_current_wave()  # chama a lista de inimigos do nível
        self.background = Background(
            f'fundo{self.color}.png')  # define o background
        self.enemies.clear()  # limpa a lista de inimigos vivos
        self.enemy_shoots.clear()  # limpa a lista de inimigos vivos

    def menu(self):
        """ Define a função de acesso às fases através dos sprites do menu interativo
        """
        # define os sprites das fases, suas imagens de fundo e valor para índice
        self.start_music("MenuTheme.ogg")
        self.player.set_pos([305, 536])
        self.background = Background(f'menu.png')
        level_1 = Block((79, 78), image="fase1.png", value=0)
        level_2 = Block((79, 196), image="fase2.png", value=1)
        level_3 = Block((79, 315), image="fase3.png", value=2)
        level_4 = Block((79, 434), image="fase4.png", value=3)
        level_5 = Block((403.5, 148), image="fase5.png", value=4)
        zen = Block((81, 553), image="zen.png", value=5)
        credits = Block((558, 523), image="creditos.png",
                        value='credits', size=(82, 102))
        quit = Block((590, 45), image="sair.png", value='quit',
                     size=(72, 72))  # sprite para sair do jogo
        self.blocks.append([level_1, pygame.sprite.RenderPlain(
            level_1)])
        self.blocks.append([level_2, pygame.sprite.RenderPlain(
            level_2)])
        self.blocks.append([level_3, pygame.sprite.RenderPlain(
            level_3)])
        self.blocks.append([level_4, pygame.sprite.RenderPlain(
            level_4)])
        self.blocks.append([level_5, pygame.sprite.RenderPlain(
            level_5)])
        self.blocks.append([zen, pygame.sprite.RenderPlain(
            zen)])
        self.blocks.append([quit, pygame.sprite.RenderPlain(
            quit)])
        self.blocks.append([credits, pygame.sprite.RenderPlain(
            credits)])

    def credits(self):
        self.player.set_pos([305, 536])
        self.blocks.clear()
        self.background = Background('nomes.png')
        return_b = Block((575, 552), image="voltar.png",
                         value="menu", size=(89, 99))
        self.blocks.append([return_b, pygame.sprite.RenderPlain(
            return_b)])

    def start_game(self, value):
        """ Inicia o jogo
        """
        self.blocks.clear()
        self.player.set_pos([305, 536])
        if value == 'quit':
            self.run = False
            return 0
        if value == 'credits':
            self.credits()
            return 0
        if value == 'menu':
            self.blocks.clear()
            self.player.set_pos([305, 536])
            self.menu()
            return 0
        self.level = value
        self.color = self.color_list[self.level]  # muda a cor padrão
        scores = [0, 90, 190, 290, 390, 500]
        bosscounters = [0, 1, 2, 3, 4, 5]
        self.bosscounter = bosscounters[self.level]
        self.true_score = scores[self.level]
        self.set_current_wave()  # chama a lista de inimigos do nível
        self.background = Background(
            f'fundo{self.color}.png')  # define o background
        self.change_music("LevelTheme.ogg")
        self.enemies.clear()  # limpa a lista de inimigos vivos
        self.enemy_shoots.clear()  # limpa a lista de disparos de inimigos vivos
        self.start = True

    def loop(self):
        """ Loop principal do jogo
        """
        clock = pygame.time.Clock()  # cria o relógio do jogo
        dt = 16  # define a efetiva velocidade do jogo
        self.player = Player([305, 536], 3)  # posição inicial do player
        self.elements['player'] = pygame.sprite.RenderPlain(
            self.player)  # prepara o sprite do Player
        self.start_music("MenuTheme.ogg")  # escolhe a música inicial
        self.menu()  # inicia o jogo
        while self.run:
            clock.tick(1000 / dt)
            event = pygame.event.poll()

            # funções de todos os eventos do jogo.
            self.player.update(dt)  # update do player
            self.handle_events(event, dt)  # eventos
            self.handle_collision()  # colisões
            if self.start:
                self.player.shoot(event, self.shoots)
                self.player.explode(event, self.explosions)
                self.spawn()
                # Update dos elementos
                self.update_elements(dt)
            self.draw_elements()  # desenha os elementos
            self.garbage_collector()
            if self.start:
                self.update_interface()  # chama atualizações de interface
            if self.player.isdead:
                self.start = False
                self.player = Player([305, 536], 3)
                self.elements['player'] = pygame.sprite.RenderPlain(
                    self.player)
                self.enemies.clear()  # limpa a lista de inimigos vivos
                self.enemy_shoots.clear()
                self.explosions.clear()
                self.power_ups.clear()
                self.shoots.clear()
                self.menu()
            pygame.display.flip()
        pygame.quit()  # sai do jogo


class Player(Spaceship):
    """ Classe Player - define tudo relacionado ao jogador
    Tem herança de Spaceship
    """

    def __init__(self, position, lives=3, speed=.5, image=None, new_size=(27, 36)):
        """Player construtor
        :param position: a posição inicial do Player.
        :type position: list
        :param lives: quantas vezes o Player pode ser atingido antes de morrer.
        :type lives: int
        :param speed: a velocidade inicial do Player em ambos os eixos
        :type speed: float
        :param image: a imagem do Player. Default None
        :type image: string
        :param nesize: o tamanho do Player
        :type newsize: tuple
        """

        # define a imagem padrão
        if not image:
            image = "nave1.png"

        # chama ElementSprite.__init__() e define valores iniciais de objetos lógicos
        super().__init__(position, lives, speed, image, new_size)
        self.direction = (0, 0)
        self.vel = (0, 0)
        self.max_vel = .5
        self.acc = (0, 0)
        self.score = 0
        self.bombs = 0
        self.size = new_size
        self.power_ups = [False, False, False, False]
        self.shield = None
        self.spd_counter = 0
        self.sht_counter = 0
        self.isdead = False

    def update(self, dt):
        """ Atualiza o Player
        :param dt: variação de tempo
        :type dt: int
        """

        # movimento
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

        # variação da imagem do sprite do Player quando ele se movimenta para esquerda e direita
        new_acc = tuple(new_acc)
        if new_acc != self.acc:
            self.acc = new_acc
            if self.acc[0] == 0:
                self.set_image('nave1.png', self.size)
            elif self.acc[0] == 1:
                self.set_image('nave2.png', self.size)
            elif self.acc[0] == -1:
                self.set_image('nave3.png', self.size)

        # velocidade do Player
        self.vel = (self.vel[0]+self.acc[0]*dt/100,
                    self.vel[1]+self.acc[1]*dt/100)
        self.normalize_vel()

        # Contagem de tempo do power up speed
        if self.spd_counter > 360:
            self.power_ups[0] = False
            self.spd_counter = 0

        # acelerador~de velocidade do power up [0]
        if self.power_ups[0]:
            mtp = 1.3
            self.spd_counter += 1
        else:
            mtp = 1

        # posição
        pos_x = self.rect.center[0] + self.vel[0]*dt*mtp
        pos_y = self.rect.center[1] + self.vel[1]*dt*mtp

        # Reduz a velocidade simulando fricção
        self.vel = (self.vel[0]*9/10, self.vel[1]*9/10)
        if abs(self.vel[0]) < 0.01:
            self.vel = (0, self.vel[1])
        if abs(self.vel[1]) < 0.01:
            self.vel = (self.vel[0], 0)

        # define posições x limítrofes como "atravessar a tela" e limites de y como "paredes"
        if pos_x < 0:
            pos_x = 640
        elif pos_x > 640:
            pos_x = 0
        if pos_y < 0:
            pos_y = 0
        elif pos_y > 640:
            pos_y = 640
        self.rect.center = (pos_x, pos_y)

        # Contagem de tempo do power up que aumenta o número de tiros
        if self.sht_counter > 360:
            self.power_ups[1] = False
            self.sht_counter = 0

        if self.power_ups[1]:
            self.sht_counter += 1

        # power up shield
        if self.shield:
            self.shield[0].update(dt)

    def shoot(self, event, shoots):
        """ Função de atirar do player
        :param event: tecla pressionada
        :type event: KEYDOWN
        :param shoots: lista de tiros do player
        :type shoots: list
        """
        if event.type in (KEYDOWN,):
            key = event.key
            if key == K_LCTRL:  # define a tecla "ctrl" como de atirar
                play_sound("PlayerShoot.ogg")  # efeito sonoro de tiro
                if not self.power_ups[1]:  # tiro neutro
                    laser = Laser((self.rect.center[0], self.rect.top))
                    shoots.append([laser, pygame.sprite.RenderPlain(laser)])
                else:  # tiros com power up
                    laser1 = Laser((self.rect.center[0], self.rect.top))
                    laser2 = Laser(
                        (self.rect.center[0], self.rect.top), direction=(1, -1), angle=-45)
                    laser3 = Laser(
                        (self.rect.center[0], self.rect.top), direction=(-1, -1), angle=45)
                    lst = [[laser1, pygame.sprite.RenderPlain(laser1)], [laser2, pygame.sprite.RenderPlain(
                        laser2)], [laser3, pygame.sprite.RenderPlain(laser3)]]  # cria três lasers
                    for laser in lst:
                        shoots.append(laser)
                self.shot_cooldown = 2  # tempo de cooldown para atirar novamente

    def explode(self, event, explosions):
        """ Power up de explosão do player
        :param event: tecla pressionada
        :type event: KEYDOWN
        :param explosions: lista de explosões ativas
        :type shoots: list
        """
        if event.type in (KEYDOWN,):
            key = event.key
            if key == K_SPACE:  # define a tecla "space" como de atirar
                if self.bombs > 0:
                    # criamos os sprites e os adicionamos na lista de explosões ativas
                    explosion1 = Explosion(
                        (320, self.rect.center[1]), type='1', color='R', hits=[self])
                    explosion2 = Explosion(
                        (self.rect.center[0], 320), type='2', color='R', hits=[self])
                    explosions.append(
                        [explosion1, pygame.sprite.RenderPlain(explosion1)])
                    explosions.append(
                        [explosion2, pygame.sprite.RenderPlain(explosion2)])
                    self.bombs -= 1

    def normalize_vel(self):
        """ Função usada para lidar com a movimentação, tornando-a mais fluida
        """
        abs_vel = (self.vel[0]**2+self.vel[1]**2)**.5
        if abs_vel > self.max_vel:
            self.vel = (self.vel[0]/abs_vel*self.max_vel,
                        self.vel[1]/abs_vel*self.max_vel)

    def got_hit(self):
        """ Define os reflexos do dano tomado pelo Player
        """
        if self.shield:  # se tiver shield
            self.power_ups[3] = False
            self.shield = None
        else:  # se não tiver shield
            self.lives -= 1
        if self.lives <= 0:  # se for a última vida
            print(self.score)
            self.isdead = True

    def get_pos(self):
        """ Retorna a posição do Player
        """
        return (self.rect.center[0], self.rect.center[1])

    def get_score(self):
        """ Retorna o score do Player
        """
        return self.score

    def set_score(self, score):
        """ Define o score do Player
        :param score: placar
        :type score: int
        """
        self.score = score
        print(self.score)

    def set_power_up(self, power_up):
        """ Define os power ups do Player
        :param power_up: número ligado ao power up
        :type power_up: int
        """
        if power_up == 1:  # mais velocidade
            self.spd_counter = 0
        elif power_up == 2:  # mais tiros
            self.sht_counter = 0
        elif power_up == 3:  # explosão
            if self.bombs < 3:
                self.bombs = 3
        elif power_up == 4 and not self.power_ups[3]:  # shield
            shield = ShieldPowerUp(
                (self.rect.center[0], self.rect.center[1]), player=self)
            self.shield = [shield, pygame.sprite.RenderPlain(shield)]

        self.power_ups[power_up - 1] = True  # Array começa em 0

    def add_score(self):
        """ Aumenta o placar
        """
        self.score += 1

    def get_bombs(self):
        return self.bombs


if __name__ == '__main__':
    G = Game()
