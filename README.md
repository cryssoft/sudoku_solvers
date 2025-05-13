USAGE:

	solver-001.py file-name

BOARD FORMAT:

	....623..
	.3...1.6.
	.5..3.8..
	19.......
	3...8.5.2
	.4..7.6..
	.7.......
	.....6..3
	....2...9

NOTES:

	For solver-001.py, it has tested out very well for "easy" puzzles from the
	New York Times.  It has, as suspected, failed on every "medium" puzzle from
	the New York Times on those same days.

	This solver uses bitmaps (not really a requirement for this simple a solver)
	to figure out which numbers a particular, empty cell can take on.  The bitmaps
	could become much more interesting in later solvers when we may be doing more
	of a "set of possibles vs. set of impossibles" match.

	This uses a "triple neighborhood" definition for the CA solver with one
	neighborhood being the row, one being the column, and one being the 3x3
	sub-puzzle.  As noted, this approach works well for "easy" puzzles (solves in
	4-6 loops) but fails very quickly (usually 2 loops) on even "medium" puzzles.
