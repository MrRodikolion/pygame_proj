import pygame as pg
import sys
import sqlite3 as sql
from time import time

from game_components.Map import MapLoader, Camera, Dark
from game_components.Player import Player, collider_w
from game_components.UI import Button


def terminate():
    pg.quit()
    sys.exit()


def start_screen():
    sart_btn = Button(screen.get_width() / 2 - 125,
                      screen.get_height() * 0.1,
                      250, 50, (255, 255, 255), 'start')

    data = cur.execute('''SELECT * FROM stats''').fetchall()
    is_stats = len(data) > 0

    if is_stats:
        last = data[:5]
        best = max(data, key=lambda x: (x[1], x[2]))

        font = pg.font.Font(None, int(screen.get_height() * 0.1))
        gettext = lambda text: font.render(text, True, (255, 255, 255))

        stats_texts = [[gettext(str(t[0])), gettext(str(t[1])), gettext(f'{t[2] // 60}:{t[2] % 60}')] for t in last]
        best_texts = [gettext(str(best[0])), gettext(str(best[1])), gettext(f'{best[2] // 60}:{best[2] % 60}')]

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or pg.key.get_pressed()[pg.K_ESCAPE]:
                running = False
                terminate()
            if event.type == pg.KEYDOWN:
                key = pg.key.get_pressed()
                if key[pg.K_f]:
                    pg.display.toggle_fullscreen()
        if sart_btn.pressed:
            running = False
        clock.tick(60)

        sart_btn.update()

        screen.fill((0, 0, 0))

        if is_stats:
            stat_w = max(sum(t.get_width() * 3 for t in stat) for stat in stats_texts)

            for i, stat in enumerate(stats_texts):
                tx = 0
                for j, t in enumerate(stat):
                    t_w = t.get_width()
                    tx += t_w

                    screen.blit(t, (screen_w / 2 - stat_w / 2 + tx, sart_btn.rect.bottom + 125 + t.get_height() * i))

                    tx += t_w * 2

            pg.draw.rect(screen, (255, 255, 255),
                         (screen_w / 2 - stat_w / 2, sart_btn.rect.bottom + 125,
                          stat_w, screen_h), 2)

            tx = 0
            for j, t in enumerate(best_texts):
                t_w = t.get_width()
                tx += t_w

                screen.blit(t, (screen_w / 2 - stat_w / 2 + tx,
                                sart_btn.rect.bottom + 125 - best_texts[0].get_height()))

                tx += t_w * 2

            pg.draw.rect(screen, (255, 170, 0),
                         (screen_w / 2 - stat_w / 2, sart_btn.rect.bottom + 125 - best_texts[0].get_height(),
                          stat_w, best_texts[0].get_height()), 4)

        sart_btn.draw(screen)
        pg.draw.circle(screen, (255, 255, 255), pg.mouse.get_pos(), 5, 2)

        pg.display.flip()


def level_screen():
    start_t = time()

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or pg.key.get_pressed()[pg.K_ESCAPE]:
                running = False
                terminate()
            if event.type == pg.KEYDOWN:
                key = pg.key.get_pressed()
                if key[pg.K_f]:
                    pg.display.toggle_fullscreen()
        clock.tick(60)

        if player.finished or player.ui.hp_bar.hp < 0:
            cur.execute('''INSERT INTO stats (bonuses, timesecs)
                        VALUES({}, {})'''.format(player.ui.bonus_counter.count, int(time() - start_t)))
            con.commit()

            running = False
            break

        player.update(level_map, screen)

        camera.update(player.rect, size)
        camera.apply(player.rect)
        level_map.update_pos((camera.dx, camera.dy))

        level_map.set_visible_chunks(player.rect.center)

        dark.update_lamps(level_map)
        dark.add_light(player.light_image, player.rect)

        dark.overlap_dark()

        screen.fill((113, 112, 125))

        level_map.draw(screen)
        blg.draw(screen)
        player.draw(screen)

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
            if event.type == pg.QUIT or pg.key.get_pressed()[pg.K_ESCAPE]:
                running = False
                terminate()
            if event.type == pg.KEYDOWN:
                key = pg.key.get_pressed()
                if key[pg.K_f]:
                    pg.display.toggle_fullscreen()
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
            if event.type == pg.QUIT or pg.key.get_pressed()[pg.K_ESCAPE]:
                running = False
                terminate()
            if event.type == pg.KEYDOWN:
                key = pg.key.get_pressed()
                if key[pg.K_f]:
                    pg.display.toggle_fullscreen()
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

    con = sql.Connection('./stats.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY,
                    bonuses INTEGER,
                    timesecs INTEGER)''')

    size = screen_w, screen_h = 16 * 80, 9 * 80
    screen = pg.display.set_mode(size)
    pg.mouse.set_visible(False)

    clock = pg.time.Clock()

    blg = pg.sprite.Group()
    dark = Dark(screen_w, screen_h, blg)

    start_screen()

    while True:
        level_map = MapLoader('./data/map/level1.tmx', screen_w // collider_w - 2, 5, screen)

        player = Player(screen,
                        4 * level_map.tilesize + level_map.tilesize // 2,
                        4 * level_map.tilesize + level_map.tilesize // 2)

        camera = Camera()

        level_screen()
        if player.ui.hp_bar.hp < 0 and dead_screen():
            break
        if end_screen():
            break

    con.close()
