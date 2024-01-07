import pygame as pg
from math import pi, atan2

try:
    from Map import (MapLoader,
                     GROUND_TILES, BOX_TILES, BONUS1_TILE, LEADER_TILES, FINISH_TILE)
    from UI import UI, MAXSTAMINA
except ImportError:
    from game_components.Map import (MapLoader,
                                     GROUND_TILES, BOX_TILES, BONUS1_TILE, LEADER_TILES, FINISH_TILE)
    from game_components.UI import UI, MAXSTAMINA

PLAYERSPEED = 5

flashlight_w, flashlight_h = 200, 200
flashlight_angle = 40
light_area_kw, light_area_kh = 3, 1.6
collider_w = 40
collider_h = 2 * collider_w


class Player(pg.sprite.Sprite):
    def __init__(self, surface, x, y):
        super().__init__()

        self.flashlight_points = (
            pg.math.Vector2(0, -15),
            *(pg.Vector2(flashlight_w, 0).rotate(-flashlight_angle / 2).rotate(a) for a in range(flashlight_angle)),
            pg.math.Vector2(0, 15))
        self.s_flashlight_image = pg.Surface((flashlight_w * 2, flashlight_h * 2)).convert_alpha()
        self.s_flashlight_image.fill((255, 255, 255, 0))

        self.flashlight_vcentr = pg.Vector2(10, flashlight_h / 2)
        pg.draw.polygon(self.s_flashlight_image, (0, 0, 0),
                        [self.flashlight_vcentr + fp for fp in self.flashlight_points])

        self.glob_image_size = (
            self.flashlight_vcentr.distance_to(self.flashlight_points[1] + self.flashlight_vcentr) * 2,
            self.flashlight_vcentr.distance_to(self.flashlight_points[2] + self.flashlight_vcentr) * 2)
        self.light_image = pg.Surface(self.glob_image_size, pg.SRCALPHA)

        self.image = pg.Surface(self.glob_image_size, pg.SRCALPHA)

        self.mask = pg.mask.from_surface(self.light_image)

        self.rect = self.light_image.get_rect()
        self.rect.x += x - self.rect.w / 2
        self.rect.y += y - self.rect.h / 2 - collider_h

        self.collider_rect = pg.Rect(self.rect.w / 2 - collider_w / 2, self.rect.h / 2 - collider_h / 2,
                                     collider_w, collider_h)

        self.flashlight_pos = pg.Vector2(self.collider_rect.center)
        self.light_image.blit(self.s_flashlight_image, self.flashlight_pos - self.flashlight_vcentr)
        pg.draw.ellipse(self.light_image, (0, 0, 0), self.collider_rect.scale_by(light_area_kw, light_area_kh))

        # debug lines
        # pg.draw.rect(self.image, (0, 255, 0), self.image.get_rect(), 1)
        pg.draw.rect(self.image, (255, 0, 0), self.collider_rect, 1)

        self.angle = 0

        self.speed = PLAYERSPEED
        self.vgf = 10

        self.grounded = False

        self.ui = UI(surface)

        self.finished = False

        self.on_leader = False

        self.up = True

    def rotate_light(self, angle):
        pos = self.flashlight_pos
        originPos = self.flashlight_vcentr
        image_rect = self.s_flashlight_image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
        offset_center_to_pivot = pg.math.Vector2(pos.xy) - image_rect.center

        rotated_offset = offset_center_to_pivot.rotate(-angle)

        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

        rotated_image = pg.transform.rotate(self.s_flashlight_image, angle)
        rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

        self.light_image = pg.Surface(self.glob_image_size, pg.SRCALPHA)
        pg.draw.ellipse(self.light_image, (0, 0, 0), self.collider_rect.scale_by(light_area_kw, light_area_kh))
        self.light_image.blit(rotated_image, rotated_image_rect)
        self.mask = pg.mask.from_surface(self.light_image)

    def handle_keys(self):
        key = pg.key.get_pressed()
        if key[pg.K_LSHIFT] and self.ui.stamina_bar.stamina > 0:
            self.speed = PLAYERSPEED * 2.5
            self.ui.stamina_bar.stamina -= 1
        elif key[pg.K_LSHIFT]:
            self.speed = PLAYERSPEED
        else:
            if self.ui.stamina_bar.stamina < MAXSTAMINA:
                self.ui.stamina_bar.stamina += 0.5
            self.speed = PLAYERSPEED

        k = 10

        if key[pg.K_a]:
            self.rect = self.rect.move(-self.speed, 0)

            if self.up and self.flashlight_vcentr.y - flashlight_h / 2 > -5:
                self.flashlight_vcentr.y -= self.speed / k
            elif self.up and self.flashlight_vcentr.y - flashlight_h / 2 <= -5:
                self.up = False
            if not self.up and self.flashlight_vcentr.y - flashlight_h / 2 < 5:
                self.flashlight_vcentr.y += self.speed / k
            elif not self.up and self.flashlight_vcentr.y - flashlight_h / 2 >= 5:
                self.up = True

        elif key[pg.K_d]:
            self.rect = self.rect.move(self.speed, 0)

            if self.up and self.flashlight_vcentr.y - flashlight_h / 2 > -5:
                self.flashlight_vcentr.y -= self.speed / k
            elif self.up and self.flashlight_vcentr.y - flashlight_h / 2 <= -5:
                self.up = False
            if not self.up and self.flashlight_vcentr.y - flashlight_h / 2 < 5:
                self.flashlight_vcentr.y += self.speed / k
            elif not self.up and self.flashlight_vcentr.y - flashlight_h / 2 >= 5:
                self.up = True

        if self.on_leader:
            if key[pg.K_w]:
                self.rect = self.rect.move(0, -self.speed)
            elif key[pg.K_s] and not self.grounded:
                self.rect = self.rect.move(0, self.speed)

        if key[pg.K_SPACE]:
            self.jump()

    def gravity_force(self):
        if self.on_leader:
            self.vgf = 10
            return
        if self.vgf < 10:
            self.vgf += 1

        if not (self.grounded and not self.vgf < 10):
            self.rect = self.rect.move(0, self.vgf)

    def jump(self):
        if self.grounded and self.ui.stamina_bar.stamina >= 10 and self.vgf == 10:
            self.ui.stamina_bar.stamina -= 10
            self.vgf = -20

    def collision(self, collision_map: MapLoader, surf):
        to_collide_rect = self.collider_rect.move((self.rect.x, self.rect.y - 10))
        to_collide_rect.h += 10

        collision, types = collision_map.collide_rect(to_collide_rect)

        self.grounded = False
        if collision:
            if FINISH_TILE in types:
                self.finished = True
                return

            self.on_leader = False
            if any((type in types for type in LEADER_TILES)):
                self.on_leader = True

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
                    if not self.on_leader and not self.grounded:
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

                upper_ground_collision = tuple(
                    filter(lambda x: -self.collider_rect.h >= x.y - self.collider_rect.bottom - self.rect.y and
                                     abs(x.centerx - self.collider_rect.centerx - self.rect.x) <= self.collider_rect.w,
                           ground_collision))

                if upper_ground_collision:
                    lowes_rect = max(upper_ground_collision, key=lambda x: x.bottom)
                    # self.rect.y = lowes_rect.bottom - (self.rect.h - self.collider_rect.h) / 2 + 1
                    self.vgf = 10

            bonus_collision = map(lambda x: collision[x[0]],
                                  filter(lambda x: x[1] in (BONUS1_TILE,), enumerate(types)))

            for bonus_rect in bonus_collision:
                self.ui.bonus_counter.count_bonus(bonus_rect.move(-collision_map.pos), 1)

        self.gravity_force()

    def update(self, collision_map: MapLoader, surf):
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        rel_x, rel_y = mouse_pos - self.rect.center
        angle = (- 180 / pi) * atan2(rel_y, rel_x)
        self.angle += angle
        self.rotate_light(angle)

        self.handle_keys()

        self.collision(collision_map, surf)

        self.ui.update()

    def draw(self, surface: pg.Surface):
        surface.blit(self.image, self.rect)
        self.ui.draw()

