#!/usr/bin/python3
#
#  PROGRAM: solver-001.py
#
#  PURPOSE: This uses a cellular automata style of solver to solve SIMPLE
#           sudoku puzzles.  With this simple style of solver, it fails on
#           most medium or hard puzzles.
#
#  USAGE:   solver-001.py file-name
#
#-------------------------------------------------------------------------------
#
#  BOARD(s):
#
#       .3716.2..   (New York Times, easy, 2025/05/02)
#       .1.3.29.8
#       4....936.
#       1..92..46
#       .4861..2.
#       629.8..3.
#       2....65..
#       .....1.82
#       8....4..3
#
#       9....57.1   (New York Times, easy, 2025/05/08)
#       2.8914...
#       16..8...2
#       ...5.294.
#       .5.1.937.
#       63....2..
#       .16.7..29
#       8.7.51..4
#       ..48...57
#
#	2.65..419   (New York Times, easy, 2025/05/10)
#	9.5..2..8
#	...3946.5
#	.574...6.
#	.1.9.8.4.
#	4...5.38.
#	174......
#	...679...
#	..9.418.3
#
#	.7..51238   (New York Times, easy, 2025/05/11)
#	368...5..
#	1..8..47.
#	..91.28.3
#	816.3..2.
#	...4...6.
#	.53.7...1
#	4..51.3.2
#	....28..5
#
#	.7.3695..   (New York Times, easy, 2025/05/12)
#	2.65....7
#	...2..163
#	.8..25.1.
#	.2579....
#	764...25.
#	417.5...8
#	.5.6.89..
#	..8..34..
#
#	6.4..98.7   (New York Times, easy, 2025/05/13)
#	9..68...3
#	58..1....
#	..7148...
#	4..3..178
#	.1....354
#	.65..724.
#	.9.4.16..
#	2.8.96...
#
#	..18.69.3   (New York Times, easy, 2025/05/14) - req'd 6 loops
#	68379...1
#	.....3.78
#	2....15.9
#	..5.3.2..
#	49..281..
#	.623...9.
#	847.6..1.
#	...48..6.
#
#	This version generally solves an "easy" puzzle from the NYT in four
#	loops, so that's pretty effective.  It gives up on "medium" puzzles
#	in an average of 2-3 loops.
#
#-------------------------------------------------------------------------------
#
#  AUTHOR:  Chris Petersen
#
#  DATE:    May 2, 2025
#
#  LAST:    May 9, 2025
#
#  HISTORY:
#
#  2025/05/09 - cp - Stripped a few unused variables and debugging outputs.
#                    Added the 2nd board to the comments after verification.
#
#               cp - Simplified the change tracking and renamed some functions
#                    to give them more descriptive names.
#
#-------------------------------------------------------------------------------
#
#  NOTES:   Started looking at an old sudoku solver in Python that I was
#           going to post and up-load.  Well, it was Python2.  Oops.  It
#           was also kind of ugly in a number of ways.  So, I started the
#           project over with something a little more ... clever.
#
#           This version uses bit values and masks to encode the triple
#           "neighborhood" calculations (across, down, 3x3) in one pass
#           and then looks for unique solutions (only one un-set bit).
#
#           This solves the "easy" board above in 4 main loops.  Huzzah!
#           It fails to solve the "medium" board from the same day even
#           faster.  Oops!  Because simple "neighborhood" analyses like
#           we'd use for a typical CA simulation don't hold up well to
#           this particular problem space.
#
from sys import argv as g_argv


def load_board(p_filename: str) -> list[list[int]] | None:
    """
    Load a sudoku "board" with "." for an open cell and 1-9 for a full
    cell.  Simple lines of data with no commas, etc. into what's really
    a list[list[bitmaps]] with a single bit on per filled cell.
    """
    l_map: dict[str,int] = {'.': -1, '1': 1, '2': 2, '3': 4, '4': 8, '5': 16, '6': 32, '7': 64, '8': 128, '9': 256}
    l_returns: list[list[int]] = []

    try:
        with open(p_filename, 'r') as l_file:
            for l_line in l_file:
                l_data: str = l_line.strip()
                try:
                    l_returns.append([l_map[x] for x in l_data])
                except ValueError as l_ve:
                    print(f'Invalid data found in a board line: {l_data}')
                    return(None)
    except FileNotFoundError as l_fnfe:
        print(f"Can't open/read {p_filename} for input")
        return(None)

    return(l_returns)


def validate_board(p_board: list[list[str]]) -> bool:
    """
    Trivial validator for the bounds of rows and columns in the board as well
    as the values in the individual cells.  It does NOT completely validate
    by neighborhood (row, column, 3x3) yet.
    """
    l_valid_values: list[int] = [-1, 1, 2, 4, 8, 16, 32, 64, 128, 256]
    l_returns: bool = True

    if (len(p_board) != 9):
        l_returns = False
    else:
        for l_board_line in p_board:
            if (len(l_board_line) != 9):
                l_returns = False
                break
        #  If we're still in good shape, validate the individual cell values
        if (l_returns):
            for l_row in range(0,len(p_board)):
                for l_column in range(0,len(p_board[l_row])):
                    if (p_board[l_row][l_column] not in l_valid_values):
                        l_returns = False
                        #  No double break here, and we're not returning yet

    return(l_returns)


def print_board(p_board: list[list[int]], p_header: str) -> None:
    """
    Simply print the board contents in the same format as they came in after a header.
    """
    l_map: dict[int,str] = {-1: '.', 1: '1', 2: '2', 4: '3', 8: '4', 16: '5', 32: '6', 64: '7', 128: '8', 256: '9'}

    print(f'\n{p_header}')
    for l_board_line in p_board:
        l_output_line: str = ''
        for l_cell in l_board_line:
            l_output_line += l_map[l_cell]
        print(f'{l_output_line}')

    return


def compute_filled_values_bitmask(p_board: list[list[int]], p_row: int, p_column: int) -> int:
    """
    Compute a bit mask of all the new values this cell CAN'T take because they're
    already taken either in the row, the column, or in the 3x3 area.
    """
    l_returns: int = 0

    #  Add in the bit values across the current row (neighborhood 1)
    for l_column in range(0,len(p_board[p_row])):
        if (p_board[p_row][l_column] != -1):
            l_returns |= p_board[p_row][l_column]
    #  Add in the bit values down the current column (neighborhood 2)
    for l_row in range(0,len(p_board)):
        if (p_board[l_row][p_column] != -1):
            l_returns |= p_board[l_row][p_column]
    #  Add in the bit values for the 3x3 area around us (neighborhood 3)
    l_base_row: int = p_row // 3
    l_base_column: int = p_column // 3
    for l_row in range(l_base_row*3,l_base_row*3+3):
        for l_column in range(l_base_column*3,l_base_column*3+3):
            if (p_board[l_row][l_column] != -1):
                l_returns |= p_board[l_row][l_column]

    return(l_returns)


def return_unique_cell_solution(p_mask: int) -> int:
    """
    Use the bit mask computed above.  If there's exactly one zero bit (a unique
    solution for this cell), then return it.  Otherwise, return -1 (empty) since we
    have no unique solution for this cell yet.

    0.0.1 - Initial version w/ int | None returns
    0.0.2 - Simplify to leave -1s alone if no unique solution
    """
    l_count_of_zeroes: int = 0
    l_returns: int = -1

    for l_bit_value in [1 << x for x in range(0,9)]:
        if ((p_mask & l_bit_value) == 0):
            l_count_of_zeroes += 1
            l_returns = l_bit_value
    if (l_count_of_zeroes != 1):
        l_returns = -1

    return(l_returns)


def loop_until_no_changes(p_board: list[list[int]]) -> None:
    """
    A basic, cellular automata-style solver that loops over the board
    contents until it stops making changes.  For each main loop, we visit
    each cell.  For each empty cell, we use the triple neighborhood to
    see if there's a unique solution for this cell.  This will usually 
    ONLY solve simple/easy level sudoku puzzles.

    0.0.1 - Used the l_new_value and interim test with int | None from above
    0.0.2 - Simplified to leave -1s alone and check them instead of None
    """
    l_changes: int = 0
    l_loops: int = 0

    print_board(p_board, f'Loop # {l_loops}')
    while ((l_loops == 0) or (l_changes != 0)):
        l_changes = 0
        for l_row in range(0,9):
            for l_column in range(0,9):
                if (p_board[l_row][l_column] == -1):
                    l_mask: int = compute_filled_values_bitmask(p_board, l_row, l_column)
                    p_board[l_row][l_column] = return_unique_cell_solution(l_mask)
                    if (p_board[l_row][l_column] != -1):
                        l_changes += 1
        l_loops += 1
        print_board(p_board, f'Loop # {l_loops}')

    return


def main(p_argv: list[str]) -> None:
    """
    The usual main() to keep us out of trouble if someone decides to import
    this file as a module.
    """
    l_board: list[list[int]] = load_board(p_argv[1])
    if l_board:
        if validate_board(l_board):
            loop_until_no_changes(l_board)
        else:
            print('Invalid board data received!')

    return


#  This is what keeps us out of trouble if someone imports this file
if (__name__ == "__main__"):
    main(g_argv)
