import pygame

SQUARE_SIZE = 50

WHITE = (255,255,255)
GRAY  = (200,200,200)
BLACK = (0,0,0)
RED = (255,0,0)

def draw_board(screen, board, highlights):
    n = len(board)
    total_size = n * SQUARE_SIZE
    section_size = int(n ** (1/2))
    screen.fill(WHITE)
    for y in range(n):
        for x in range(n):
            value = board[y][x] if board[y][x] != -1 else None
            if value:
                font = pygame.font.Font(size=36)
                text = font.render(str(value), True, RED if (y,x) in highlights else BLACK)
                text_rect = text.get_rect(center=((x+.5)*SQUARE_SIZE, (y+.5)*SQUARE_SIZE))
                screen.blit(text, text_rect)

    for i in range(1, n):
        pygame.draw.line(screen, GRAY, (i*SQUARE_SIZE, 0), (i*SQUARE_SIZE, total_size), 2)
        pygame.draw.line(screen, GRAY, (0, i*SQUARE_SIZE), (total_size, i*SQUARE_SIZE), 2)

    for i in range(1, section_size):
        offset = section_size * i
        pygame.draw.line(screen, BLACK, (offset*SQUARE_SIZE, 0), (offset*SQUARE_SIZE, total_size), 4)
        pygame.draw.line(screen, BLACK, (0, offset*SQUARE_SIZE), (total_size, offset*SQUARE_SIZE), 4)

def visualize(board, highlights = []):
    if board is None:
        return
    pygame.init()
    total_size = len(board) * SQUARE_SIZE
    screen = pygame.display.set_mode((total_size, total_size))
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