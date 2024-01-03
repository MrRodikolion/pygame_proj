import pygame as pg
import pytmx

GROUND_TILES = (3, 14)


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
    def __init__(self, map_file, tiles_on_surf, chunk_size):
        self.map = pytmx.load_pygame(map_file)
        self.tiles_on_surf = tiles_on_surf

        self.pos = pg.Vector2(0, 0)

        self.k = self.map.tilewidth

        self.chunks = []

        for ychnk in range(self.map.height // chunk_size):
            self.chunks.append([])
            for xchnk in range(self.map.width // chunk_size):
                chunk = Chunk((xchnk * chunk_size, ychnk * chunk_size), chunk_size, self.map.tilewidth)
                for y in range(chunk_size):
                    for x in range(chunk_size):
                        img = self.map.get_tile_image(x, y, 0)
                        if img:
                            chunk.add_image(img, (x, y))

                self.chunks[-1].append(chunk)

        print(self.chunks)

    def collide_rect(self, rect: pg.Rect):

        # colis = [(c % self.map.height, c // self.map.height, c) for c in rect.collidelistall(self.tiles_rect)]
        # colis = rect.collidelist(self.tiles_rect)
        # if colis != -1:
        #     collider = self.tiles_rect[colis]
        #     gid = self.map.get_tile_gid(colis % self.map.height, colis // self.map.height, 0) + 1
        #     collider_type = self.map.tiledgidmap[gid]
        #     return {'rect': collider,
        #             'type': collider_type}
        return False

    def update_pos(self, dpos):
        pass
        # self.pos += pg.Vector2(dpos)
        # self.tiles_rect = []
        #
        # for y in range(self.map.height):
        #     for x in range(self.map.width):
        #         img = self.map.get_tile_image(x, y, 0)
        #         if img:
        #             self.tiles_rect.append(pg.Rect(self.pos + (x * self.k, y * self.k), (self.k + 1, self.k + 1)))

    def draw(self, surface: pg.Surface, pl_pos: [int, int]):
        # self.tiles_rect = []
        #
        # pl_pos = (-self.pos + pg.Vector2(surface.get_size()) // 2) // self.map.tilewidth
        # print(range(self.map.width)[int(pl_pos[0] - self.tiles_on_surf): int(pl_pos[0] + self.tiles_on_surf)],
        #       range(self.map.width)[int(pl_pos[0] - self.tiles_on_surf): int(pl_pos[0] + self.tiles_on_surf)])

        self.k = surface.get_width() / self.tiles_on_surf
        for row in self.chunks:
            for chunk in row:
                chunk.draw(surface, (0,0))



class Chunk(pg.sprite.Sprite):
    def __init__(self, pos, size, tilesize):
        super().__init__()
        self.image = pg.Surface((size * tilesize, size * tilesize))
        self.rects = []
        self.pos = pg.Vector2(0, 0)
        self.local_pos = pg.Vector2(pos)

        self.size = size
        self.tilesize = tilesize

    def add_image(self, img: pg.Surface, pos: [int, int]):
        self.image.blit(img, (pos[0] * self.tilesize, pos[1] * self.tilesize))

        self.rects.append(img.get_rect().move((pos[0] * self.tilesize, pos[1] * self.tilesize)))

    def update(self, direction):
        self.pos += direction

        self.rects = [rect.move(direction) for rect in self.rects]

    def draw(self, surf: pg.Surface, pos: [int, int]):
        surf.blit(self.image, pos + self.local_pos)
