import pygame as pg
import sys

from game_components.Map import MapLoader, Camera, Dark
from game_components.Player import Player, collider_w
from game_components.UI import Button
from game_components.Enemy import Enemy


def terminate():
    pg.quit()
    sys.exit()


def start_screen():
    sart_btn = Button(screen.get_width() / 2 - 125,
                      screen.get_height() * 0.1,
                      250, 50, (255, 255, 255), 'start')

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                terminate()
        if sart_btn.pressed:
            running = False
        clock.tick(60)

        sart_btn.update()

        screen.fill((0, 0, 0))

        sart_btn.draw(screen)
        pg.draw.circle(screen, (255, 255, 255), pg.mouse.get_pos(), 5, 2)

        pg.display.flip()


def level_screen():
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                terminate()
        clock.tick(60)

        if player.finished or player.ui.hp_bar.hp < 0:
            running = False
            break

        player.update(level_map, screen)

        enemy.update(level_map, screen, player)

        camera.update(player.rect, size)
        camera.apply(player.rect)
        camera.apply(enemy.rect)
        level_map.update_pos((camera.dx, camera.dy))

        level_map.set_visible_chunks(player.rect.center)

        dark.update_lamps(level_map)
        dark.add_light(player.light_image, player.rect)

        dark.overlap_dark()

        screen.fill((113, 112, 125))

        level_map.draw(screen)
        enemy.draw(screen)
        blg.draw(screen)
        player.draw(screen)

        # for row in level_map.chunks:
        #     for chunk in row:
        #         for rct in chunk.rects:
        #             pg.draw.rect(screen, (0, 255, 0), rct, 1)

        pg.draw.circle(screen, (255, 255, 255), pg.mouse.get_pos(), 5, 2)

        pg.display.flip()


def end_screen():
    exit_btn = Button(screen.get_width() / 2 - 125,
                      screen.get_height() * 0.9, 250, 50, (255, 0, 0), 'exit')
    restart_btn = Button(screen.get_width() / 2 - 125,
                         screen.get_height() * 0.8, 250, 50, (255, 0, 0), 'restart')

    font = pg.font.Font(None, int(screen.get_height() * 0.1))
    stats_text = font.render(f'Bonuses: {player.ui.bonus_counter.count}', True, (255, 255, 255), (100, 100, 100))

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                terminate()
        if exit_btn.pressed:
            running = False
            return True
        if restart_btn.pressed:
            running = False
            return False

        clock.tick(60)

        exit_btn.update()
        restart_btn.update()

        screen.fill((0, 0, 0))

        screen.blit(stats_text, (screen.get_width() / 3 - stats_text.get_width() / 2,
                                 screen.get_height() * 0.1))

        exit_btn.draw(screen)
        restart_btn.draw(screen)
        pg.draw.circle(screen, (255, 255, 255), pg.mouse.get_pos(), 5, 2)

        pg.display.flip()


def dead_screen():
    exit_btn = Button(screen.get_width() / 2 - 125,
                      screen.get_height() * 0.9, 250, 50, (255, 0, 0), 'exit')
    restart_btn = Button(screen.get_width() / 2 - 125,
                         screen.get_height() * 0.8, 250, 50, (255, 0, 0), 'restart')

    font = pg.font.Font(None, int(screen.get_height() * 0.1))
    stats_text = font.render(f'Bonuses: {player.ui.bonus_counter.count}', True, (255, 255, 255), (100, 100, 100))
    dead_text = font.render('You Dead', True, (255, 0, 0), (100, 0, 0))

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                terminate()
        if exit_btn.pressed:
            running = False
            return True
        if restart_btn.pressed:
            running = False
            return False

        clock.tick(60)

        exit_btn.update()
        restart_btn.update()

        screen.fill((0, 0, 0))

        screen.blit(stats_text, (screen.get_width() / 3 - stats_text.get_width() / 2,
                                 screen.get_height() * 0.1))
        screen.blit(dead_text, (screen_w / 2 - dead_text.get_width() / 2,
                                screen_h * 0.01))

        exit_btn.draw(screen)
        restart_btn.draw(screen)
        pg.draw.circle(screen, (255, 255, 255), pg.mouse.get_pos(), 5, 2)

        pg.display.flip()


if __name__ == '__main__':
    pg.init()

    size = screen_w, screen_h = 16 * 80, 9 * 80
    screen = pg.display.set_mode(size)
    pg.mouse.set_visible(False)

    clock = pg.time.Clock()

    blg = pg.sprite.Group()
    dark = Dark(screen_w, screen_h, blg)

    start_screen()

    while True:
        level_map = MapLoader('./data/map/level0.tmx', screen_w // collider_w - 2, 5, screen)

        player = Player(screen,
                        1 * level_map.tilesize + level_map.tilesize // 2,
                        0 * level_map.tilesize + level_map.tilesize // 2)

        enemy = Enemy(screen,
                      5 * level_map.tilesize + level_map.tilesize // 2,
                      0 * level_map.tilesize + level_map.tilesize // 2)

        camera = Camera()

        level_screen()
        if player.ui.hp_bar.hp < 0 and dead_screen():
            break
        if end_screen():
            break
