import types

import pygame as pg

MAXSTAMINA = 100


class UI(pg.sprite.Group):
    def __init__(self, surface: pg.Surface):
        super().__init__()

        self.bonus_counter = BonusCounter(surface.get_size(), self)
        self.stamina_bar = StaminaBar(surface.get_size(), self)

        self.surface = surface

    def draw(self):
        super().draw(self.surface)


class BonusCounter(pg.sprite.Sprite):
    def __init__(self, surf_size, group):
        super().__init__(group)

        w, h = surf_size[0] * 0.3, surf_size[1] * 0.1
        self.image = pg.Surface((w, h), pg.SRCALPHA)

        self.text = 'Bonus: {}'
        self.count = 0

        font = pg.font.Font(None, self.image.get_height())
        text = font.render(self.text.format(self.count), True, (199, 159, 14), (61, 51, 13))

        self.image.blit(text, (0, 0))

        self.rect = self.image.get_rect()

        self.collected_rects = []

    def count_bonus(self, rect: pg.Rect, c):
        if rect in self.collected_rects:
            return False

        self.count += c
        self.collected_rects.append(rect)

        return True

    def update(self, *args, **kwargs):
        self.image.fill((0, 0, 0, 0))

        font = pg.font.Font(None, self.image.get_height())
        text = font.render(self.text.format(self.count), True, (199, 159, 14), (61, 51, 13))

        self.image.blit(text, (0, 0))

        self.rect = self.image.get_rect()


class StaminaBar(pg.sprite.Sprite):
    def __init__(self, surf_size, group):
        super().__init__(group)

        self.stamina = MAXSTAMINA

        w, h = surf_size[0] * 0.03, surf_size[1] * 0.4
        self.image = pg.Surface((w, h), pg.SRCALPHA)
        self.rect = self.image.get_rect().move(0, surf_size[1] - h)

    def update(self, *args, **kwargs):
        self.image.fill((0, 0, 0, 0))
        self.image.fill((255, 153, 0, 200), ((0, 0),
                                             (self.image.get_width(), self.image.get_height() / 100 * self.stamina)))


class Button(pg.sprite.Sprite):
    def __init__(self, x, y, w, h, color, text):
        super().__init__()
        self.color = color
        font = pg.font.Font(None, h)
        self.text = font.render(text, True, color)

        self.image = pg.Surface((w, h), pg.SRCALPHA)
        self.image.fill((50, 100, 50, 170))

        self.rect = self.image.get_rect().move(x, y)

        self.pressed = False

    def update(self, *args, **kwargs):
        mouse_pos = pg.mouse.get_pos()
        mousecollide = self.rect.collidepoint(mouse_pos)

        if mousecollide and pg.mouse.get_pressed()[0]:
            self.image.fill((50, 255, 50))
            self.pressed = True
            return
        elif mousecollide:
            self.image.fill((50, 150, 50, 170))
            return

        self.image.fill((50, 100, 50, 170))
        self.pressed = False

    def draw(self, surf):
        x = self.image.get_width() / 2 - self.text.get_width() / 2
        y = self.image.get_height() / 2 - self.text.get_height() / 2
        self.image.blit(self.text, (x, y))
        surf.blit(self.image, self.rect)
