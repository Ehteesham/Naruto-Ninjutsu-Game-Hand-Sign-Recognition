import multiprocessing

import pygame

from mechanism.fighter import Fighter
from mechanism.naruto_detection import NarutoDetection

# function for drawing a text
def drwa_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x, y))


# function for drawing background
def draw_bg():
    scaled_bg = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))


# function for drawing fighters health bar
def health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))


class NarutoDetectionProcess(multiprocessing.Process):
    def __init__(self, result_queue):
        super().__init__()
        self.result_queue = result_queue

    def run(self):
        naruto_detector = NarutoDetection(self.result_queue)
        naruto_detector.capture_frames()


if __name__ == "__main__":
    result_queue = multiprocessing.Queue()
    naruto_detection_process = NarutoDetectionProcess(result_queue)
    naruto_detection_process.start()

    pygame.init()

    # create a game window
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Naruto Game")

    # set frame rate
    clock = pygame.time.Clock()
    FPS = 60

    # define colours
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)

    # define game variable
    intro_count = 5
    last_count_update = pygame.time.get_ticks()

    # define fighter variables
    NARUTO_SIZE = 160
    NARUTO_SCALE = 1
    NARUTO_OFFSET = [45, 55]
    NARUTO_DATA = [NARUTO_SIZE, NARUTO_SCALE, NARUTO_OFFSET]
    SASUKE_SIZE = 160
    SASUKE_SCALE = 1
    SASUKE_OFFSET = [35, 55]
    SASUKE_DATA = [SASUKE_SIZE, SASUKE_SCALE, SASUKE_OFFSET]

    #  load background image
    bg_img = pygame.image.load(
        "assets/images/background/background - 2.jpg"
    ).convert_alpha()

    # load spritesheets
    naruto_sheet = pygame.image.load(
        "assets/images/naruto/naruto-sperits-2.png"
    ).convert_alpha()
    sasuke_sheet = pygame.image.load(
        "assets/images/sasuke/Untitled-Sasuke.png"
    ).convert_alpha()

    # define number of step in each animation
    NARUTO_ANIMATION_STEPS = [4, 6, 5, 13, 9, 10]
    SASUKE_ANIMATION_STEPS = [4]

    # define font
    count_font = pygame.font.Font("assets/fonts/Turok.ttf", 80)
    score_font = pygame.font.Font("assets/fonts/Turok.ttf", 30)

    # create two instances for fighter
    fighter_1 = Fighter(
        200, 400, False, NARUTO_DATA, naruto_sheet, NARUTO_ANIMATION_STEPS
    )
    fighter_2 = Fighter(
        700, 400, True, SASUKE_DATA, sasuke_sheet, SASUKE_ANIMATION_STEPS
    )
    run = True
    while run:
        result = None
        if not result_queue.empty():
            result = result_queue.get_nowait()
        clock.tick(FPS)

        # draw background
        draw_bg()

        # show player stats
        health_bar(fighter_1.health, 20, 20)
        health_bar(fighter_2.health, 580, 20)

        # update countdown
        if intro_count <= 0:
            # Move fighters
            fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, result)
        else:
            # display the count timer
            drwa_text(str(intro_count), count_font, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
            # update count timer
            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        # update fighters
        fighter_1.update()
        fighter_2.update()

        # darw fighters
        fighter_1.draw(screen)
        fighter_2.draw(screen)

        # event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                naruto_detection_process.terminate()

        # update display
        pygame.display.update()

    naruto_detection_process.join()
    pygame.quit()
