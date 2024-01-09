import pygame as pg
from math import pi, atan2

try:
    from Map import (MapLoader,
                     GROUND_TILES, BOX_TILES, BONUS1_TILE, LEADER_TILES, FINISH_TILE)
    from UI import UI, MAXSTAMINA
    from Player import Player
except ImportError:
    from game_components.Map import (MapLoader,
                                     GROUND_TILES, BOX_TILES, BONUS1_TILE, LEADER_TILES, FINISH_TILE)
    from game_components.UI import UI, MAXSTAMINA
    from game_components.Player import Player

ENEMYSPEED = 5

light_area_kw, light_area_kh = 3, 1.6
collider_w = 40
collider_h = 2 * collider_w


class Enemy(pg.sprite.Sprite):
    def __init__(self, surface, x, y):
        super().__init__()

        self.light_image = pg.Surface((collider_w * 2, collider_h * 2), pg.SRCALPHA)

        self.image = pg.Surface((collider_w * 2, collider_h * 2), pg.SRCALPHA)

        self.mask = pg.mask.from_surface(self.light_image)

        self.rect = self.light_image.get_rect()
        self.rect.x += x - self.rect.w / 2
        self.rect.y += y - self.rect.h / 2 - collider_h

        self.collider_rect = pg.Rect(self.rect.w / 2 - collider_w / 2, self.rect.h / 2 - collider_h / 2,
                                     collider_w, collider_h)

        pg.draw.ellipse(self.light_image, (0, 0, 0), self.collider_rect.scale_by(light_area_kw, light_area_kh))

        # debug lines
        # pg.draw.rect(self.image, (0, 255, 0), self.image.get_rect(), 1)
        pg.draw.rect(self.image, (50, 50, 50), self.collider_rect, 50)

        self.angle = 0

        self.speed = ENEMYSPEED
        self.vgf = 10

        self.grounded = False

    def gravity_force(self):
        if not (self.grounded and not self.vgf < 10):
            self.rect = self.rect.move(0, self.vgf)

    def collision(self, collision_map: MapLoader, player: Player, surf):
        to_collide_rect = self.collider_rect.move((self.rect.x, self.rect.y - 10))
        to_collide_rect.h += 10

        collision, types = collision_map.collide_rect(to_collide_rect)

        self.grounded = False
        if collision:
            # for colis_rect in collision:
            #     pg.draw.rect(surf, (255, 0, 0), colis_rect, 2)

            ground_collision_types = list(filter(lambda x: x[1] in GROUND_TILES + BOX_TILES, enumerate(types)))

            if ground_collision_types:
                ground_collision = tuple(map(lambda x: collision[x[0]], ground_collision_types))
                # for colis_rect in ground_collision:
                #     pg.draw.rect(surf, (255, 0, 0), colis_rect, 10)

                down_ground_collision = list(filter(lambda x: x.y - self.collider_rect.bottom - self.rect.y >= -10,
                                                    ground_collision))

                if down_ground_collision:
                    if not self.grounded:
                        self.rect.y = min(map(lambda x: x.y, down_ground_collision)) - (
                                self.rect.h - self.collider_rect.h) / 2 - self.collider_rect.h + 1

                    self.grounded = True

                center_ground_collision = list(
                    filter(lambda x: -self.collider_rect.h < x.y - self.collider_rect.bottom - self.rect.y < -10,
                           ground_collision))

                if center_ground_collision:
                    nearest_collision = min(center_ground_collision,
                                            key=lambda x: abs(x.centerx - self.rect.x - self.collider_rect.centerx))
                    if nearest_collision.centerx - self.rect.x - self.collider_rect.centerx >= 0:
                        self.rect.x = center_ground_collision[0].left - self.collider_rect.right
                    else:
                        self.rect.x = center_ground_collision[0].right - self.collider_rect.left

                # upper_ground_collision = tuple(
                #     filter(lambda x: -self.collider_rect.h >= x.y - self.collider_rect.bottom - self.rect.y and
                #                      abs(x.centerx - self.collider_rect.centerx - self.rect.x) <= self.collider_rect.w,
                #            ground_collision))
                #
                # if upper_ground_collision:
                #     lowes_rect = max(upper_ground_collision, key=lambda x: x.bottom)
                #     # self.rect.y = lowes_rect.bottom - (self.rect.h - self.collider_rect.h) / 2 + 1
                #     self.vgf = 10

        player_collision = to_collide_rect.colliderect(player.collider_rect.move(player.rect.topleft))

        if player_collision:
            player.ui.hp_bar.hp -= 10

        self.gravity_force()

    def update(self, collision_map: MapLoader, surf, player: Player):
        self.collision(collision_map, player, surf)

    def draw(self, surface: pg.Surface):
        surface.blit(self.image, self.rect)
