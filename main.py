import pygame as pg

from game_components.Map import MapLoader, Camera
from game_components.Player import Player, Dark

if __name__ == '__main__':
    pg.init()

    size = screen_w, screen_h = 16 * 80, 9 * 80
    screen = pg.display.set_mode(size)
    clock = pg.time.Clock()

    level_map = MapLoader('./data/map/level0.tmx', 10, 25)

    plg = pg.sprite.Group()
    player = Player(0 * (screen.get_width() / level_map.tiles_on_surf + 1),
                    0 * (screen.get_height() / level_map.tiles_on_surf + 1), plg)

    camera = Camera()

    blg = pg.sprite.Group()
    dark = Dark(screen_w, screen_h, blg)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                break
        clock.tick()

        dark.overlap_dark(player.mask, player.rect[:2])

        plg.update(level_map)

        camera.update(player.rect, size)
        camera.apply(player.rect)
        level_map.update_pos((camera.dx, camera.dy))

        screen.fill((50, 50, 50))

        level_map.draw(screen, player.rect.center)
        blg.draw(screen)
        plg.draw(screen)

        pg.display.flip()
