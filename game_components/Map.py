import pygame as pg
import pytmx

GROUND_TILES = (3, 14, 25)
LEADER_TILES = (2, 13, 24)
BOX_TILES = (17, 27, 28)

BONUS1_TILE = 46


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj: pg.Rect):
        obj.x += self.dx
        obj.y += self.dy

    def update(self, target: pg.Rect, screen_size):
        screen_w, screen_h = screen_size
        self.dx = -(target.x + target.w // 2 - screen_w // 2)
        self.dy = -(target.y + target.h // 2 - screen_h // 2)


class MapLoader:
    def __init__(self, map_file, tiles_on_surf, chunk_size, surf: pg.Surface):
        self.map = pytmx.load_pygame(map_file)
        self.tiles_on_surf = tiles_on_surf

        self.pos = pg.Vector2(0, 0)

        self.k = surf.get_width() / self.tiles_on_surf

        self.chunks = []
        self.chunk_size = chunk_size

        for ychnk in range(self.map.height // chunk_size):
            self.chunks.append([])
            for xchnk in range(self.map.width // chunk_size):
                chunk = Chunk((xchnk, ychnk), chunk_size, self.map.tilewidth, self.k)
                for y in range(chunk_size):
                    for x in range(chunk_size):
                        img = self.map.get_tile_image(chunk_size * xchnk + x, chunk_size * ychnk + y, 0)
                        if img:
                            chunk.add_image(img, (x, y))

                self.chunks[-1].append(chunk)

    def collide_rect(self, rect: pg.Rect):
        collisions = []
        collider_types = []
        for row in self.chunks:
            for chunk in row:
                colis = rect.collidelistall(chunk.rects)
                collisions += [chunk.rects[c] for c in colis]
                collider_types += [self.map.tiledgidmap[
                                       self.map.get_tile_gid(chunk.localpos[0] * self.chunk_size + c % self.chunk_size,
                                                             chunk.localpos[1] * self.chunk_size + c // self.chunk_size,
                                                             0)] for c in colis]

        return tuple(collisions), tuple(collider_types)

    def update_pos(self, dpos):
        self.pos += pg.Vector2(dpos)
        for row in self.chunks:
            for chunk in row:
                chunk.update(dpos)

    def draw(self, surface: pg.Surface):
        # self.tiles_rect = []
        #
        # pl_pos = (-self.pos + pg.Vector2(surface.get_size()) // 2) // self.map.tilewidth
        # print(range(self.map.width)[int(pl_pos[0] - self.tiles_on_surf): int(pl_pos[0] + self.tiles_on_surf)],
        #       range(self.map.width)[int(pl_pos[0] - self.tiles_on_surf): int(pl_pos[0] + self.tiles_on_surf)])

        self.k = surface.get_width() / self.tiles_on_surf
        for y, row in enumerate(self.chunks):
            for x, chunk in enumerate(row):
                img = pg.transform.scale(chunk.image,
                                         (chunk.image.get_width() * self.k + 1, chunk.image.get_height() * self.k + 1))
                surface.blit(img, self.pos + (
                    x * self.chunk_size * self.map.tilewidth * self.k,
                    y * self.chunk_size * self.map.tilewidth * self.k))


class Chunk(pg.sprite.Sprite):
    def __init__(self, pos, size, tilesize, k):
        super().__init__()
        self.image = pg.Surface((size * tilesize, size * tilesize))
        self.rects = []
        self.pos = pg.Vector2(0, 0)
        self.localpos = pos

        self.k = k

        self.size = size
        self.tilesize = tilesize

    def add_image(self, img: pg.Surface, pos: [int, int]):
        self.image.blit(img, (pos[0] * self.tilesize, pos[1] * self.tilesize))

        rect = img.get_rect().move((pos[0] * self.tilesize * self.k + self.localpos[
            0] * self.size * self.tilesize * self.k + self.tilesize * self.k // 2.5,
                                    pos[1] * self.tilesize * self.k + self.localpos[
                                        1] * self.size * self.tilesize * self.k + self.tilesize * self.k // 2.5))
        self.rects.append(rect.scale_by(self.k, self.k))

    def update(self, direction):
        self.rects = [rect.move(direction) for rect in self.rects]

    def draw(self, surf: pg.Surface, pos: [int, int]):
        surf.blit(self.image, pos)
