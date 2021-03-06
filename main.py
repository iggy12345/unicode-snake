from game import SnakeGame
import pygame
import time
import threading

pygame.init()


class BoardLogic:
    def __init__(self, g: SnakeGame):
        self.g = g
        self.input_buff = []
        self.lock = threading.Lock()
        self.running = False
        self.clk = pygame.time.Clock()

    def _loop(self):
        self.running = True
        while self.running:
            self.clk.tick(60)
            if len(self.input_buff) > 0:
                with self.lock:
                    kp = self.input_buff.pop(0).key

                if kp == pygame.K_a:
                    g.direction = 3
                elif kp == pygame.K_s:
                    g.direction = 2
                elif kp == pygame.K_d:
                    g.direction = 1
                elif kp == pygame.K_w:
                    g.direction = 0
                elif kp == pygame.K_ESCAPE:
                    self.running = False

            if g.tick():
                time.sleep(1 / ((int(g.score / 10 + 1)) * 10))
            else:
                self.running = False

    def start_loop(self):
        t = threading.Thread(target=self._loop,
                             args=(),
                             daemon=True)
        t.start()
        return t


if __name__ == '__main__':
    size = [800, 600]
    screen = pygame.display.set_mode(size)
    g = SnakeGame(size[1] // 10, size[0] // 10)

    rrunning = True
    while rrunning:
        g.initialize()
        g.place_food()
        game_surf = pygame.Surface(size)
        font = pygame.font.SysFont('roboto', 16)

        gt = BoardLogic(g)
        gt.start_loop()

        running = True
        while running:
            if not gt.running:
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    rrunning = False
                    with gt.lock:
                        gt.running = False
                elif event.type == pygame.KEYDOWN:
                    with gt.lock:
                        gt.input_buff.append(event)

            game_surf.fill((255, 255, 255))

            for ri, r in enumerate(g.buff):
                for ci, c in enumerate(r):
                    if c == '\u25cb':
                        # print("Drawing a snake at {}, {}".format(ri * 10, ci * 10))
                        with g.lock:
                            pygame.draw.circle(game_surf,
                                               (0, 0, 255),
                                               ((ci * 10) + 5, (ri * 10) + 5),
                                               5)
                    elif c == '\u25c9':
                        # wprint("Placing food at {}, {}".format(ci, ri))
                        with g.lock:
                            pygame.draw.circle(game_surf,
                                               (0, 127, 255),
                                               ((ci * 10) + 5, (ri * 10) + 5),
                                               5)

            timg = font.render("Score: {}, Level: {}".format(g.score, g.score // 10 + 1), True, (0, 0, 0))

            screen.blit(game_surf, (0, 0))
            screen.blit(timg, (0, 0))
            pygame.display.flip()

        timg = font.render("Game Over! Would you like to try again?", True, (0, 0, 0))
        screen.blit(timg, ((size[0] >> 1) - 150, size[1] >> 1))
        timg = font.render("Yes", True, (0, 0, 0))
        btn_pos = ((size[0] >> 1) - 25, (size[1] >> 1) + 20)
        screen.blit(timg, btn_pos)
        pygame.display.flip()

        while rrunning:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                rrunning = False
                break
            elif event.type == pygame.MOUSEBUTTONUP:
                mx, my = pygame.mouse.get_pos()
                if btn_pos[0] - 5 <= mx <= btn_pos[0] + 30 and btn_pos[1] - 5 <= my <= btn_pos[1] + 20:
                    g.initialize()
                    g.place_food()
                    g.score = 0
                    break

    pygame.quit()
