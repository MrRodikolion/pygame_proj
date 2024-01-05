import pygame as pg
from math import pi, atan2

try:
    from Map import MapLoader, GROUND_TILES, BOX_TILES, BONUS1_TILE, LEADER_TILES
except ImportError:
    from game_components.Map import MapLoader, GROUND_TILES, BOX_TILES, BONUS1_TILE, LEADER_TILES

PLAYERSPEED = 5


class Player(pg.sprite.Sprite):
    def __init__(self, x, y, group):
        super().__init__(group)
        flashlight_w, flashlight_h = 200, 200
        self.s_flashlight_image = pg.Surface((flashlight_w, flashlight_h)).convert_alpha()
        self.s_flashlight_image.fill((255, 255, 255, 0))
        self.flashlight_points = (
            pg.math.Vector2(0, -5), pg.math.Vector2(flashlight_w, -flashlight_h / 2),
            pg.math.Vector2(flashlight_w, flashlight_h / 2), pg.math.Vector2(0, 5))

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
        self.rect.y += y - self.rect.h

        self.collider_rect = pg.Rect(self.rect.w / 2 - 40, self.rect.h / 2 - 80, 80, 160)

        self.flashlight_pos = pg.Vector2(self.collider_rect.center)
        self.light_image.blit(self.s_flashlight_image, self.flashlight_pos - self.flashlight_vcentr)
        pg.draw.ellipse(self.light_image, (0, 0, 0), self.collider_rect.scale_by(1.9, 1.6))

        # debug lines
        # pg.draw.rect(self.image, (0, 255, 0), self.image.get_rect(), 1)
        pg.draw.rect(self.image, (255, 0, 0), self.collider_rect, 1)

        self.angle = 0

        self.speed = PLAYERSPEED
        self.vgf = 10

        self.grounded = False

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
        pg.draw.ellipse(self.light_image, (0, 0, 0), self.collider_rect.scale_by(3, 1.6))
        self.light_image.blit(rotated_image, rotated_image_rect)
        self.mask = pg.mask.from_surface(self.light_image)

    def handle_keys(self):
        key = pg.key.get_pressed()
        if key[pg.K_LSHIFT]:
            self.speed = PLAYERSPEED * 2.5
        else:
            self.speed = PLAYERSPEED

        if key[pg.K_a]:
            self.rect = self.rect.move(-self.speed, 0)
        elif key[pg.K_d]:
            self.rect = self.rect.move(self.speed, 0)

        if key[pg.K_SPACE]:
            self.jump()

    def gravity_force(self):
        if self.vgf < 10:
            self.vgf += 1

        self.rect = self.rect.move(0, self.vgf)

    def jump(self):
        if self.grounded:
            self.vgf = -20

    def collision(self, collision_map: MapLoader, surf):
        collision, types = collision_map.collide_rect(
            self.collider_rect.move((self.rect.x, self.rect.y + 10)))

        self.grounded = False
        if collision:

            for colis_rect in collision:
                pg.draw.rect(surf, (255, 0, 0), colis_rect, 2)

            ground_collision = list(filter(lambda x: x[1] in GROUND_TILES + BOX_TILES, enumerate(types)))

            if ground_collision:

                down_ground_collision = list(filter(lambda x: x.y - self.collider_rect.bottom - self.rect.y >= -10,
                                                    map(lambda x: collision[x[0]], ground_collision)))

                if down_ground_collision:
                    self.grounded = True
                    self.rect.y = min(map(lambda x: x.y, down_ground_collision)) - (
                            self.rect.h - self.collider_rect.h) / 2 - self.collider_rect.h - 9

                upper_ground_collision = list(filter(lambda x: x.y - self.collider_rect.bottom - self.rect.y < -10,
                                                     map(lambda x: collision[x[0]], ground_collision)))
                if upper_ground_collision:
                    upper_ground_collision.sort(key=lambda x: x.x - self.rect.x - self.collider_rect.x)
                    # self.rect.x = upper_ground_collision[0] - (
                    #         self.rect.h - self.collider_rect.h) / 2 - self.collider_rect.h - 9
                    print(upper_ground_collision)

        self.gravity_force()

    def update(self, collision_map: MapLoader, surf):
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        rel_x, rel_y = mouse_pos - self.rect.center
        angle = (- 180 / pi) * atan2(rel_y, rel_x)
        self.angle += angle
        self.rotate_light(angle)

        self.handle_keys()

        self.collision(collision_map, surf)


class Dark(pg.sprite.Sprite):
    def __init__(self, w, h, group):
        super().__init__(group)
        self.image = pg.Surface((w, h)).convert_alpha()
        self.image.fill((0, 0, 0, 250))
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

    def overlap_dark(self, light_mask: pg.mask.Mask, mask_pos):
        offset = mask_pos
        if self.mask.overlap(light_mask, offset):
            new_mask = self.mask.overlap_mask(light_mask, offset)
            new_surf = new_mask.to_surface().convert_alpha()
            new_surf.set_colorkey((0, 0, 0))
            fillclr = pg.Surface(new_surf.get_size(), pg.SRCALPHA)
            fillclr.fill((0, 0, 0, 250))
            fillclr.blit(new_surf, (0, 0))
            fillclr.set_colorkey((255, 255, 255))

            self.image = fillclr
