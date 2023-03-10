import pygame
import os
from math import ceil

# Módulo utilizado integralmente do Curso Pygame original


class Background:
    """ Cria o background do jogo
    """

    def __init__(self, image="space.png"):
        """ Construtor do background 
        :param image: a imagem do fundo
        :type image: string
        """

        # faz upload da imagem
        image = os.path.join('images', image)
        # .convert() é relacionado à performance do Pygame
        image = pygame.image.load(image).convert()

        # crimos as variáveis iniciais
        self.imagesize = image.get_size()
        self.pos = [0, -1 * self.imagesize[1]]
        screen = pygame.display.get_surface()
        screen_size = screen.get_size()

        # setamos w = largura(width) e h = altura(height)
        w = (ceil(float(screen_size[0]) / self.imagesize[0]) + 1) * \
            self.imagesize[0]
        h = (ceil(float(screen_size[1]) / self.imagesize[1]) + 1) * \
            self.imagesize[1]
        back = pygame.Surface((w, h))

        # blit de várias cópias do background para preencher a tela
        for i in range((back.get_size()[0] // self.imagesize[0])):
            for j in range((back.get_size()[1] // self.imagesize[1])):
                back.blit(
                    image, (i * self.imagesize[0], j * self.imagesize[1]))

        self.image = back

    def update(self, dt):
        """ Move o background
        :param dt: variação do tempo
        :type dt: int
        """
        self.pos[1] += 1
        if self.pos[1] > 0:
            self.pos[1] -= self.imagesize[1]

    def draw(self, screen):
        """ Desenha a imagem na tela definida
        :param screen: tela em que será colocada a imagem
        :type screen: pygame.screen
        """
        screen.blit(self.image, self.pos)
