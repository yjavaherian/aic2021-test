# This is a repository for IUT AICUP 2021 that I made public

## Instructions

1. write your AI code in `Controller` class in `dummy.py`.
2. change `N` in `./local.py` to set the number of rounds that the game is going to be played.
3. run `python3 ./local.py` to run the code locally for `N` rounds.
4. run `python3 ./main.py -p1 ./dummy.py -p2 ./dummy.py` to run the code with the original kernel.

## Notes

- in the local run, the kernel, client communication is by kernel calling the `communicate()` method of `Controller` class in `dummy.py`.

- in the `main` run, kernel, client communication is via standard I/O.
