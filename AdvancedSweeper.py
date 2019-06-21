from PIL import ImageGrab
import numpy as np
import pyautogui as pag
import itertools


pag.PAUSE = 0.001


DIFFICULTY = 'hard'
SQUARE_SIZE = 16  # Pixels

if DIFFICULTY == 'easy':
    FRAME = 444, 152, 588, 296  # x_left, y_top, x_right, y_down
    FIELD_SIZE = 9, 9  # Height, Width
    MINE_NUM = 10  # Mines

elif DIFFICULTY == 'medium':
    FRAME = 436, 152, 692, 408  # x_left, y_top, x_right, y_down
    FIELD_SIZE = 16, 16  # Height, Width
    MINE_NUM = 40  # Mines

else:
    FRAME = 427, 152, 907, 408  # x_left, y_top, x_right, y_down
    FIELD_SIZE = 16, 30  # Height, Width
    MINE_NUM = 99  # Mines


def script():
    pag.click((FRAME[0] + FRAME[2]) // 2, (FRAME[1] + FRAME[3]) // 2)

    minefield = [[None for _ in range(FIELD_SIZE[1])] for _ in range(FIELD_SIZE[0])]

    mines_flagged = 0

    run_script = True
    check = 0

    while run_script and check < 150:
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

        # Checks if all mines are already flagged, then opens remaining unopened squares
        if mines_flagged == MINE_NUM:
            for x in range(len(minefield)):
                for y in range(len(minefield[0])):
                    if minefield[x][y] is None:
                        pag.click(FRAME[0] + y * SQUARE_SIZE + 8, FRAME[1] + x * SQUARE_SIZE + 8)

        rule_ai_check = False  # checks if rule AI did something this iteration

        # See if rule based AI can solve current position (computationally faster)
        for x, row in enumerate(minefield):
            for y, cell in enumerate(row):
                if cell is not None and cell != 0:
                    if rule_ai(minefield, cell, x, y, mines_flagged):
                        rule_ai_check = True

        # If rule based AI couldn't solve then use probabilistic AI
        if not rule_ai_check:

            unopened_cells_coord_group = []
            unopened_neighbours_coord_group = []

            unopened_cells_coord = []
            unopened_neighbours_coord = []

            for x, row in enumerate(minefield):
                for y, cell in enumerate(row):
                    if cell is not None and cell != 0 and cell != 9:

                        adjacent_tiles = get_valid_adjacent_tiles(x, y)

                        for tile in adjacent_tiles:
                            if minefield[tile[0]][tile[1]] is None:
                                if [tile[0], tile[1]] not in unopened_cells_coord:
                                    unopened_cells_coord.append([tile[0], tile[1]])
                                if [x, y] not in unopened_neighbours_coord:
                                    unopened_neighbours_coord.append([x, y])

                        if len(unopened_cells_coord) >= 15:
                            unopened_cells_coord_group.append(unopened_cells_coord)
                            unopened_neighbours_coord_group.append(unopened_neighbours_coord)
                            unopened_cells_coord = []
                            unopened_neighbours_coord = []

            if len(unopened_cells_coord) != 0:
                unopened_cells_coord_group.append(unopened_cells_coord)
                unopened_neighbours_coord_group.append(unopened_neighbours_coord)

            for i in range(len(unopened_cells_coord_group)):
                probabilistic_ai(minefield, unopened_cells_coord_group[i],
                                 unopened_neighbours_coord_group[i], mines_flagged)

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
    return 0 <= x <= FIELD_SIZE[0] - 1 and 0 <= y <= FIELD_SIZE[1] - 1


def get_valid_adjacent_tiles(x, y):  # Checks and return adjacent tiles
    neighbours = [[1, 1], [1, 0], [1, -1], [0, 1], [0, -1], [-1, 1], [-1, 0], [-1, -1]]
    adjacent_tiles = []
    for coordinate in neighbours:
        if is_inside_table(x + coordinate[0], y + coordinate[1]):
            adjacent_tiles.append([x + coordinate[0], y + coordinate[1]])
    return adjacent_tiles


def rule_ai(minefield, cell, x, y, mines_flagged):  # Rule based AI

    adjacent_tiles = get_valid_adjacent_tiles(x, y)
    adjacent_mines = cell
    adjacent_unopened_squares = 0
    adjacent_flags = 0

    ai_check = False

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
                ai_check = True
                mines_flagged += 1

    # Second Rule: If adjacent flags and mines are same, then open all adjacent unopened squares
    if adjacent_mines == adjacent_flags:
        for tile in adjacent_tiles:
            if minefield[tile[0]][tile[1]] is None:
                pag.click(FRAME[0] + tile[1] * SQUARE_SIZE + 8, FRAME[1] + tile[0] * SQUARE_SIZE + 8)
                ai_check = True

    if ai_check:
        return True
    else:
        return False


def probabilistic_ai(minefield, unopened_cells_coordinates, unopened_neighbours_coordinates, mines_flagged):

    possible_states = list(itertools.product([None, 9], repeat=len(unopened_cells_coordinates)))
    valid_possible_states = []

    for state in possible_states[1:-1]:

        check_if_valid = True

        check_for_mine_overflow = 0

        for i, cell in enumerate(unopened_cells_coordinates):
            minefield[cell[0]][cell[1]] = state[i]
            if possible_states[i] == 9:
                check_for_mine_overflow += 1

        if check_for_mine_overflow > MINE_NUM - mines_flagged:
            check_if_valid = False

        for i, neighbour in enumerate(unopened_neighbours_coordinates):
            adjacent_tiles = get_valid_adjacent_tiles(neighbour[0], neighbour[1])
            adjacent_mines = 0

            for tile in adjacent_tiles:
                if minefield[tile[0]][tile[1]] == 9:
                    adjacent_mines += 1

            if adjacent_mines != minefield[neighbour[0]][neighbour[1]]:
                check_if_valid = False
                break

        if check_if_valid:
            valid_possible_states.append(state)

    for i, cell in enumerate(unopened_cells_coordinates):
        minefield[cell[0]][cell[1]] = None

    if len(valid_possible_states) == 1:

        for i, value in enumerate(valid_possible_states[0]):
            if value is None:
                pag.click(FRAME[0] + unopened_cells_coordinates[i][1] * SQUARE_SIZE + 8,
                          FRAME[1] + unopened_cells_coordinates[i][0] * SQUARE_SIZE + 8)
            elif value == 9:
                pag.click(FRAME[0] + unopened_cells_coordinates[i][1] * SQUARE_SIZE + 8,
                          FRAME[1] + unopened_cells_coordinates[i][0] * SQUARE_SIZE + 8, button='right')

    else:
        if len(valid_possible_states) is not 0:
            lowest_change_of_mine_list = [0 for _ in range(len(valid_possible_states[0]))]
            lowest_change_of_mine_cell = 0, len(valid_possible_states)

            for state in valid_possible_states:
                for i, value in enumerate(state):
                    if value == 9:
                        lowest_change_of_mine_list[i] += 1

            for i, chance in enumerate(lowest_change_of_mine_list):
                if chance == 0:
                    pag.click(FRAME[0] + unopened_cells_coordinates[i][1] * SQUARE_SIZE + 8,
                              FRAME[1] + unopened_cells_coordinates[i][0] * SQUARE_SIZE + 8)
                    print("0%: " + str([unopened_cells_coordinates[i][1], unopened_cells_coordinates[i][0]]))

                if chance == len(valid_possible_states):
                    pag.click(FRAME[0] + unopened_cells_coordinates[i][1] * SQUARE_SIZE + 8,
                              FRAME[1] + unopened_cells_coordinates[i][0] * SQUARE_SIZE + 8, button='right')
                    minefield[unopened_cells_coordinates[i][0]][unopened_cells_coordinates[i][1]] = 9
                    mines_flagged += 1
                    print("100%: " + str([unopened_cells_coordinates[i][1], unopened_cells_coordinates[i][0]]))

                if chance < lowest_change_of_mine_cell[1]:
                    lowest_change_of_mine_cell = (i, chance)

            if 0 in lowest_change_of_mine_list or len(valid_possible_states) in lowest_change_of_mine_list:
                return

            else:
                pag.click(FRAME[0] + unopened_cells_coordinates[lowest_change_of_mine_cell[0]][1] * SQUARE_SIZE + 8,
                          FRAME[1] + unopened_cells_coordinates[lowest_change_of_mine_cell[0]][0] * SQUARE_SIZE + 8)
                print(str(lowest_change_of_mine_cell[1] * 100 / len(valid_possible_states)) + "%: " + str(
                    [unopened_cells_coordinates[lowest_change_of_mine_cell[0]][0],
                     unopened_cells_coordinates[lowest_change_of_mine_cell[0]][1]]))
                return


if __name__ == '__main__':
    script()
