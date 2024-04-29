import pygame

NUM_SQUARES = 9
SQUARE_SIZE = 50
TOTAL_SIZE = NUM_SQUARES * SQUARE_SIZE

WHITE = (255,255,255)
GRAY  = (200,200,200)
BLACK = (0,0,0)
RED = (255,0,0)

def draw_board(screen, board, highlights):
    screen.fill(WHITE)
    for y in range(NUM_SQUARES):
        for x in range(NUM_SQUARES):
            value = board[y][x] if board[y][x] != -1 else None
            if value:
                font = pygame.font.Font(size=36)
                text = font.render(str(value), True, RED if (y,x) in highlights else BLACK)
                text_rect = text.get_rect(center=((x+.5)*SQUARE_SIZE, (y+.5)*SQUARE_SIZE))
                screen.blit(text, text_rect)

    for i in range(1, NUM_SQUARES):
        pygame.draw.line(screen, GRAY, (i*SQUARE_SIZE, 0), (i*SQUARE_SIZE, TOTAL_SIZE), 2)
        pygame.draw.line(screen, GRAY, (0, i*SQUARE_SIZE), (TOTAL_SIZE, i*SQUARE_SIZE), 2)

    for i in range(1,3):
        offset = 3 * i
        pygame.draw.line(screen, BLACK, (offset*SQUARE_SIZE, 0), (offset*SQUARE_SIZE, TOTAL_SIZE), 4)
        pygame.draw.line(screen, BLACK, (0, offset*SQUARE_SIZE), (TOTAL_SIZE, offset*SQUARE_SIZE), 4)


def main(board, highlights = []):
    if board is None:
        return
    pygame.init()
    screen = pygame.display.set_mode((TOTAL_SIZE, TOTAL_SIZE))
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_board(screen, board, highlights)

        pygame.display.flip()
        clock.tick(50)

    pygame.quit()




