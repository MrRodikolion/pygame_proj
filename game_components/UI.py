import pygame as pg


class UI(pg.sprite.Group):
    def __init__(self, surface: pg.Surface):
        super().__init__()

        self.bonus_counter = BonusCounter(surface.get_size(), self)

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
