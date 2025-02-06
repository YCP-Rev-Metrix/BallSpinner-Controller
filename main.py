from BallSpinnerController.BallSpinnerController import BallSpinnerController
import sys

if len(sys.argv) > 1:
    if sys.argv[1] == "1":
        BallSpinnerController(debug="1")
else:
    BallSpinnerController()