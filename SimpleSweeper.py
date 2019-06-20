import numpy as np
from PIL import ImageGrab
import pyautogui as pag


pag.PAUSE = 0.001

FRAME = 427, 152, 907, 408  # x_left, y_top, x_right, y_down
SQUARE_SIZE = 16  # pixels
FIELD_SIZE = 16, 30  # mines


def script():
    minefield = [[None for _ in range(FIELD_SIZE[1])] for _ in range(FIELD_SIZE[0])]

    run_script = True
    check = 0

    while run_script and check < 500:
        img = ImageGrab.grab(bbox=FRAME)
        board = np.array(img)

        for i in range(0, len(board) - 1, SQUARE_SIZE):
            for j in range(0, len(board[0]) - 1, SQUARE_SIZE):
                top_left = board[i+1][j+1]
                if top_left[0] >= 200 and top_left[1] <= 50 and top_left[2] <= 50:  # If a bomb was clicked
                    run_script = False
                if top_left[0] >= 200 and top_left[1] >= 200 and top_left[2] >= 200:  # Unopened
                    continue
                else:
                    check_pixel_color(minefield, board[i+8][j+8], i // SQUARE_SIZE, j // SQUARE_SIZE)

        for x, row in enumerate(minefield):
            for y, cell in enumerate(row):
                if cell is not None and cell != 0:
                    ai(minefield, cell, x, y)

        check += 1


def check_pixel_color(minefield, pixel, x, y):
    if pixel[0] <= 50 and pixel[1] <= 50 and pixel[2] >= 200:  # Blue
        minefield[x][y] = 1
    elif pixel[0] <= 50 and pixel[1] >= 100 and pixel[2] <= 50:  # Green
        minefield[x][y] = 2
    elif pixel[0] >= 200 and pixel[1] <= 50 and pixel[2] <= 50:  # Red
        minefield[x][y] = 3
    elif pixel[0] <= 50 and pixel[1] <= 50 and pixel[2] >= 100:  # Blue
        minefield[x][y] = 4
    elif pixel[0] >= 100 and pixel[1] <= 50 and pixel[2] <= 50:  # Red
        minefield[x][y] = 5
    else:
        minefield[x][y] = 0  # Grey (empty)


def is_inside_table(x, y):  # Checks if coordinates in inside board
    return 0 <= x <= 15 and 0 <= y <= 29


def get_valid_adjacent_tiles(x, y):  # Checks and return adjacent tiles
    neighbours = [[1, 1], [1, 0], [1, -1], [0, 1], [0, -1], [-1, 1], [-1, 0], [-1, -1]]
    adjacent_tiles = []
    for coordinate in neighbours:
        if is_inside_table(x + coordinate[0], y + coordinate[1]):
            adjacent_tiles.append([x + coordinate[0], y + coordinate[1]])
    return adjacent_tiles


def ai(minefield, cell, x, y):  # Rule based AI

    adjacent_tiles = get_valid_adjacent_tiles(x, y)
    adjacent_mines = cell
    adjacent_unopened_squares = 0
    adjacent_flags = 0

    for tile in adjacent_tiles:
        if minefield[tile[0]][tile[1]] is None:
            adjacent_unopened_squares += 1
        elif minefield[tile[0]][tile[1]] == 9:
            adjacent_flags += 1

    # First Rule: If adjacent unopened squares and adjacent mines minus flags are same, then flag unopened squares
    if adjacent_mines - adjacent_flags == adjacent_unopened_squares:
        for tile in adjacent_tiles:
            if minefield[tile[0]][tile[1]] is None:
                minefield[tile[0]][tile[1]] = 9
                pag.click(FRAME[0] + tile[1] * SQUARE_SIZE + 8, FRAME[1] + tile[0] * SQUARE_SIZE + 8, button='right')

    # Second Rule: If adjacent flags and mines are same, then open all adjacent unopened squares
    if adjacent_mines == adjacent_flags:
        for tile in adjacent_tiles:
            if minefield[tile[0]][tile[1]] is None:
                pag.click(FRAME[0] + tile[1] * SQUARE_SIZE + 8, FRAME[1] + tile[0] * SQUARE_SIZE + 8)

    return


if __name__ == '__main__':
    script()
