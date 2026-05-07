"""Classic Snake game built with Python's turtle graphics library.

Run with: python snake_game.py
"""

from __future__ import annotations

import json
import random
import time
import turtle
from pathlib import Path
from typing import List

# --- Configuration -----------------------------------------------------------

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
PLAY_AREA = 290  # half-extent of the playfield from origin (px)
GRID = 20  # snake/food cell size (px)

INITIAL_DELAY = 0.1
SPEEDUP_PER_FOOD = 0.001
MIN_DELAY = 0.02

POINTS_PER_FOOD = 10
RESPAWN_PAUSE = 1.0  # seconds to pause after a death

BG_COLOR = "#0d1b2a"
HEAD_COLOR = "#ffd166"
BODY_COLOR = "#06d6a0"
FOOD_COLOR = "#ef476f"
TEXT_COLOR = "#f1faee"

HIGH_SCORE_FILE = Path.home() / ".snake_high_score.json"

OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}


# --- Helpers -----------------------------------------------------------------

def load_high_score() -> int:
    """Read the persisted high score, returning 0 if unavailable or corrupt."""
    try:
        return int(json.loads(HIGH_SCORE_FILE.read_text()).get("high_score", 0))
    except (FileNotFoundError, ValueError, OSError):
        return 0


def save_high_score(score: int) -> None:
    try:
        HIGH_SCORE_FILE.write_text(json.dumps({"high_score": score}))
    except OSError:
        pass


def random_grid_position() -> tuple[int, int]:
    """Pick a random cell-aligned coordinate inside the play area."""
    cells = PLAY_AREA // GRID
    x = random.randint(-cells, cells) * GRID
    y = random.randint(-cells, cells) * GRID
    return x, y


# --- Game objects ------------------------------------------------------------

class Snake:
    """Player-controlled snake: a head turtle plus a list of body segments."""

    def __init__(self) -> None:
        self.head = turtle.Turtle()
        self.head.speed(0)
        self.head.shape("square")
        self.head.color(HEAD_COLOR)
        self.head.penup()
        self.head.goto(0, 0)
        self.direction: str = "stop"
        self.segments: List[turtle.Turtle] = []

    def set_direction(self, new_direction: str) -> None:
        if OPPOSITE.get(self.direction) != new_direction:
            self.direction = new_direction

    def move(self) -> None:
        # Body follows head: shift each segment to the position of the one ahead.
        for i in range(len(self.segments) - 1, 0, -1):
            ahead = self.segments[i - 1]
            self.segments[i].goto(ahead.xcor(), ahead.ycor())
        if self.segments:
            self.segments[0].goto(self.head.xcor(), self.head.ycor())

        if self.direction == "up":
            self.head.sety(self.head.ycor() + GRID)
        elif self.direction == "down":
            self.head.sety(self.head.ycor() - GRID)
        elif self.direction == "left":
            self.head.setx(self.head.xcor() - GRID)
        elif self.direction == "right":
            self.head.setx(self.head.xcor() + GRID)

    def grow(self) -> None:
        segment = turtle.Turtle()
        segment.speed(0)
        segment.shape("square")
        segment.color(BODY_COLOR)
        segment.penup()
        self.segments.append(segment)

    def reset(self) -> None:
        for segment in self.segments:
            segment.goto(1000, 1000)  # offscreen; turtle has no destroy()
            segment.hideturtle()
        self.segments.clear()
        self.head.goto(0, 0)
        self.direction = "stop"

    def hit_wall(self) -> bool:
        return (
            abs(self.head.xcor()) > PLAY_AREA
            or abs(self.head.ycor()) > PLAY_AREA
        )

    def hit_self(self) -> bool:
        return any(seg.distance(self.head) < GRID for seg in self.segments)


class Food:
    """A piece of food the snake can eat to grow."""

    def __init__(self) -> None:
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.shape("circle")
        self.turtle.color(FOOD_COLOR)
        self.turtle.penup()
        self.respawn()

    def respawn(self, avoid: List[turtle.Turtle] | None = None) -> None:
        avoid = avoid or []
        for _ in range(50):
            x, y = random_grid_position()
            if all(abs(t.xcor() - x) > GRID or abs(t.ycor() - y) > GRID for t in avoid):
                self.turtle.goto(x, y)
                return
        self.turtle.goto(*random_grid_position())


class Scoreboard:
    """Heads-up display for current score and high score."""

    def __init__(self, high_score: int) -> None:
        self.score = 0
        self.high_score = high_score
        self.pen = turtle.Turtle()
        self.pen.speed(0)
        self.pen.color(TEXT_COLOR)
        self.pen.penup()
        self.pen.hideturtle()
        self.pen.goto(0, 260)
        self.render()

    def render(self, message: str | None = None) -> None:
        self.pen.clear()
        text = message or f"Score: {self.score}   High Score: {self.high_score}"
        self.pen.write(text, align="center", font=("Courier", 20, "bold"))

    def add_food(self) -> None:
        self.score += POINTS_PER_FOOD
        if self.score > self.high_score:
            self.high_score = self.score
        self.render()

    def reset(self) -> None:
        self.score = 0
        self.render()


# --- Game --------------------------------------------------------------------

class Game:
    def __init__(self) -> None:
        self.window = turtle.Screen()
        self.window.title("Snake")
        self.window.bgcolor(BG_COLOR)
        self.window.setup(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.window.tracer(0)

        self.snake = Snake()
        self.food = Food()
        self.scoreboard = Scoreboard(load_high_score())
        self.delay = INITIAL_DELAY
        self.paused = False
        self.running = True

        self._bind_keys()

    def _bind_keys(self) -> None:
        self.window.listen()
        self.window.onkeypress(lambda: self.snake.set_direction("up"), "w")
        self.window.onkeypress(lambda: self.snake.set_direction("down"), "s")
        self.window.onkeypress(lambda: self.snake.set_direction("left"), "a")
        self.window.onkeypress(lambda: self.snake.set_direction("right"), "d")
        self.window.onkeypress(lambda: self.snake.set_direction("up"), "Up")
        self.window.onkeypress(lambda: self.snake.set_direction("down"), "Down")
        self.window.onkeypress(lambda: self.snake.set_direction("left"), "Left")
        self.window.onkeypress(lambda: self.snake.set_direction("right"), "Right")
        self.window.onkeypress(self.toggle_pause, "p")
        self.window.onkeypress(self.quit, "q")

    def toggle_pause(self) -> None:
        self.paused = not self.paused
        if self.paused:
            self.scoreboard.render("Paused — press P to resume")

    def quit(self) -> None:
        self.running = False

    def handle_death(self) -> None:
        save_high_score(self.scoreboard.high_score)
        self.scoreboard.render("Game Over")
        self.window.update()
        time.sleep(RESPAWN_PAUSE)
        self.snake.reset()
        self.scoreboard.reset()
        self.delay = INITIAL_DELAY

    def step(self) -> None:
        self.window.update()

        if self.paused:
            return

        if self.snake.hit_wall() or self.snake.hit_self():
            self.handle_death()
            return

        if self.snake.head.distance(self.food.turtle) < GRID:
            self.food.respawn(avoid=[self.snake.head, *self.snake.segments])
            self.snake.grow()
            self.delay = max(MIN_DELAY, self.delay - SPEEDUP_PER_FOOD)
            self.scoreboard.add_food()

        self.snake.move()

    def run(self) -> None:
        try:
            while self.running:
                self.step()
                time.sleep(self.delay)
        except turtle.Terminator:
            pass  # window closed
        finally:
            save_high_score(self.scoreboard.high_score)


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
