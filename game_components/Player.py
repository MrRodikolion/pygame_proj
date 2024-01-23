import pygame as pg
from math import pi, atan2, radians, degrees, cos, sin

try:
    from Map import (MapLoader,
                     GROUND_TILES, BOX_TILES, BONUS1_TILE, LEADER_TILES, FINISH_TILE, DANGER_TILES)
    from UI import UI, MAXSTAMINA
except ImportError:
    from game_components.Map import (MapLoader,
                                     GROUND_TILES, BOX_TILES, BONUS1_TILE, LEADER_TILES, FINISH_TILE, DANGER_TILES)
    from game_components.UI import UI, MAXSTAMINA

PLAYERSPEED = 5

flashlight_w, flashlight_h = 200, 200
flashlight_angle = 40
light_area_kw, light_area_kh = 3, 1.6
collider_w = 40
collider_h = 2 * collider_w


def load_anim_sprites(filename):
    img = pg.image.load(filename)
    sheet_size = (16, 32)

    walk_anim_sprites = []
    for y in range(1):
        for x in range(8):
            sheet = img.subsurface((sheet_size[0] * x, sheet_size[1] * y), sheet_size)
            walk_anim_sprites.append(pg.transform.scale(sheet, (collider_w, collider_h)))

    stand_sprite = img.subsurface((sheet_size[0] * 1, sheet_size[1] * 3), sheet_size)
    stand_sprite = pg.transform.scale(stand_sprite, (collider_w, collider_h))

    jump_sprite = img.subsurface((sheet_size[0] * 2, sheet_size[1] * 1), sheet_size)
    jump_sprite = pg.transform.scale(jump_sprite, (collider_w, collider_h))

    return walk_anim_sprites, stand_sprite, jump_sprite


class Player(pg.sprite.Sprite):
    def __init__(self, surface, x, y):
        super().__init__()
        self.walk_anim, self.stand_sprite, self.jump_sprite = load_anim_sprites('./data/player/player.png')

        self.flashlight_maxdist = 400
        self.count_rays = 50

        self.glob_image_size = ((self.flashlight_maxdist + 10) * 2,
                                (self.flashlight_maxdist + 10) * 2)
        self.light_image = pg.Surface(self.glob_image_size, pg.SRCALPHA)

        self.image = pg.Surface(self.glob_image_size, pg.SRCALPHA)

        self.mask = pg.mask.from_surface(self.light_image)

        self.rect = self.light_image.get_rect()
        self.rect.x += x - self.rect.w / 2
        self.rect.y += y - self.rect.h / 2 - collider_h

        self.collider_rect = pg.Rect(self.rect.w / 2 - collider_w / 2, self.rect.h / 2 - collider_h / 2,
                                     collider_w, collider_h)

        self.flashlight_pos = pg.Vector2(self.collider_rect.center)

        pg.draw.ellipse(self.light_image, (0, 0, 0), self.collider_rect.scale_by(light_area_kw, light_area_kh))

        # debug lines
        # pg.draw.rect(self.image, (0, 255, 0), self.image.get_rect(), 1)
        # pg.draw.rect(self.image, (255, 0, 0), self.collider_rect, 1)

        self.image.blit(self.stand_sprite, self.collider_rect.topleft)

        self.angle = 0

        self.dir = True

        self.speed = PLAYERSPEED
        self.vgf = 10

        self.grounded = False

        self.ui = UI(surface)

        self.finished = False

        self.on_leader = False

        self.up = True

        self.walking = False
        self.walk_sprite = 0

    def raycast_flashlight(self, level_map: MapLoader):
        self.light_image = pg.Surface(self.glob_image_size, pg.SRCALPHA)
        pg.draw.ellipse(self.light_image, (0, 0, 0), self.collider_rect.scale_by(light_area_kw, light_area_kh))

        angle0 = self.angle
        pts = [self.collider_rect.center]
        ang_step = 70 / self.count_rays
        for ray in range(self.count_rays):
            ftarget_x = - sin(radians(angle0)) * (self.flashlight_maxdist + 10) - level_map.pos.x + self.rect.centerx
            ftarget_y = + cos(radians(angle0)) * (self.flashlight_maxdist + 10) - level_map.pos.y + self.rect.centery
            for d in range(1, self.flashlight_maxdist, 2):
                target_x = - sin(radians(angle0)) * d - level_map.pos.x + self.rect.centerx
                target_y = + cos(radians(angle0)) * d - level_map.pos.y + self.rect.centery

                x = int(target_x / level_map.tilesize)
                y = int(target_y / level_map.tilesize)

                try:
                    type = level_map.map.tiledgidmap[level_map.map.get_tile_gid(x, y, 0)]
                except:
                    continue

                if type in GROUND_TILES:
                    ftarget_x = - sin(radians(angle0)) * (d + 10) - level_map.pos.x + self.rect.centerx
                    ftarget_y = + cos(radians(angle0)) * (d + 10) - level_map.pos.y + self.rect.centery
                    break

            pts.append((ftarget_x + level_map.pos.x - self.rect.x, ftarget_y + level_map.pos.y - self.rect.y))

            angle0 += ang_step

        pg.draw.polygon(self.light_image, (0, 0, 0), pts)

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

        k = 2
        self.walking = False
        if key[pg.K_a]:
            self.rect = self.rect.move(-self.speed, 0)
            self.dir = False
            self.walking = True

            if self.up and self.flashlight_pos.y - self.collider_rect.centery > -5:
                self.flashlight_pos.y -= self.speed / k
            elif self.up and self.flashlight_pos.y - self.collider_rect.centery <= -5:
                self.up = False
            if not self.up and self.flashlight_pos.y - self.collider_rect.centery < 5:
                self.flashlight_pos.y += self.speed / k
            elif not self.up and self.flashlight_pos.y - self.collider_rect.centery >= 5:
                self.up = True

        elif key[pg.K_d]:
            self.rect = self.rect.move(self.speed, 0)
            self.dir = True
            self.walking = True

            if self.up and self.flashlight_pos.y - self.collider_rect.centery > -5:
                self.flashlight_pos.y -= self.speed / k
            elif self.up and self.flashlight_pos.y - self.collider_rect.centery <= -5:
                self.up = False
            if not self.up and self.flashlight_pos.y - self.collider_rect.centery < 5:
                self.flashlight_pos.y += self.speed / k
            elif not self.up and self.flashlight_pos.y - self.collider_rect.centery >= 5:
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

            if any((tile in types for tile in DANGER_TILES)):
                self.ui.hp_bar.hp -= 10

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

    def redraw(self):
        self.image.fill((0, 0, 0, 0))

        if self.walking and self.grounded:
            if self.dir:
                img = pg.transform.flip(self.walk_anim[self.walk_sprite], True, False)
            else:
                img = self.walk_anim[self.walk_sprite]

            self.image.blit(img, self.collider_rect.topleft)

            self.walk_sprite = self.walk_sprite + 1 if self.walk_sprite + 1 < len(self.walk_anim) else 0
        elif not self.grounded:
            if self.dir:
                img = pg.transform.flip(self.jump_sprite, True, False)
            else:
                img = self.jump_sprite

            self.image.blit(img, self.collider_rect.topleft)
        else:
            if self.dir:
                img = pg.transform.flip(self.stand_sprite, True, False)
            else:
                img = self.stand_sprite

            self.image.blit(img, self.collider_rect.topleft)

    def update(self, collision_map: MapLoader, surf):
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        rel_x, rel_y = mouse_pos - self.rect.center - (0, self.flashlight_pos.y - self.collider_rect.centery)
        angle = (180 / pi) * atan2(rel_y, rel_x) - 90 - 35
        self.angle = angle
        # self.rotate_light(angle)

        self.handle_keys()

        self.collision(collision_map, surf)

        self.ui.update()

        self.redraw()
        self.raycast_flashlight(collision_map)

    def draw(self, surface: pg.Surface):
        surface.blit(self.image, self.rect)
        self.ui.draw()
