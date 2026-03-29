#!/usr/bin/env python3

"""
L-System GUI — carica configurazione da file TOML.

Uso: python gui3.py config.toml

Tasti:
  p          play/pause (avanza automaticamente)
  Right      iterazione successiva
  Left       iterazione precedente
  r          reset (torna all'iterazione iniziale)
  h          mostra/nascondi help a schermo
  q          esci
"""

import sys

import turtle

# ── window defaults ────────────────────────────────────────────────────────────
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
HELP_FONT_WIDTH = 260  # pixel reserved for help text alignment

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # pip install tomli
    except ImportError:
        sys.exit("Richiede Python 3.11+ oppure: pip install tomli")


# ── config loader ──────────────────────────────────────────────────────────────


def load_config(path: str) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def parse_config(cfg: dict) -> dict:
    return {
        "axiom": str(cfg.get("axiom", "F")),
        "rules": dict(cfg.get("rules", {})),
        "angle": float(cfg.get("angle", 90)),
        "distance": float(cfg.get("distance", 5)),
        "start_iter": int(cfg.get("start_iter", 0)),
        "max_iter": int(cfg.get("max_iter", 8)),
        "play_interval": int(cfg.get("play_interval", 800)),
        "bg_color": str(cfg.get("bg_color", "black")),
        "fg_color": str(cfg.get("fg_color", "white")),
        "start_x": float(cfg.get("start_x", -200)),
        "start_y": float(cfg.get("start_y", 0)),
        "start_heading": float(cfg.get("start_heading", 0)),
        "title": str(cfg.get("title", "L-System")),
    }


# ── L-System ───────────────────────────────────────────────────────────────────


def build_l_system(axiom: str, rules: dict, n: int) -> str:
    """
    Costruisce la n-esima iterazione di un sistema L:
    1) parte da `axiom`
    2) per n cicli, sostituisce ogni carattere `c` con `rules[c]` se presente,
       altrimenti mantiene `c`
    3) restituisce la stringa finale per il disegno Turtle
    """
    current = axiom
    print(f"{''.join(current)}")
    for _ in range(n):
        # Expand one generation: replace each symbol using rules,
        # keep unchanged if missing.
        current = "".join(rules.get(c, c) for c in current)
        print(f"Iter {_+1:>2} | len {len(current):>8}")
        print(f"{''.join(current)}")

    return current


# ── App ────────────────────────────────────────────────────────────────────────

HELP_LINES = [
    "  ←  / →   prev / next",
    "  p        play / pause",
    "  r        reset",
    "  h        toggle help",
    "  q        quit",
]


class LSystemApp:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.iteration = cfg["start_iter"]
        self.playing = False
        self.show_help = True

        # turtle setup
        self.screen = turtle.Screen()
        self.screen.setup(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.screen.title(cfg["title"])
        self.screen.bgcolor(cfg["bg_color"])
        self.screen.tracer(0, 0)

        self.t = turtle.Turtle()
        self.t.speed(0)
        self.t.hideturtle()
        self.t.color(cfg["fg_color"])

        # dedicated turtle for the help overlay (always on top)
        self.ht = turtle.Turtle()
        self.ht.speed(0)
        self.ht.hideturtle()
        self.ht.penup()

        self._bind_keys()
        self.render()

    # ── rendering ──────────────────────────────────────────────────────────────

    def render(self):
        self.t.reset()
        self.t.hideturtle()
        self.t.speed(0)
        self.t.color(self.cfg["fg_color"])
        self.t.penup()
        self.t.goto(self.cfg["start_x"], self.cfg["start_y"])
        self.t.setheading(self.cfg["start_heading"])
        self.t.pendown()

        instructions = build_l_system(
            self.cfg["axiom"], self.cfg["rules"], self.iteration
        )
        self._draw(instructions)
        self._draw_help()
        self.screen.update()
        self.screen.title(
            f"{self.cfg['title']} — iter {self.iteration}"
            + (" ▶" if self.playing else "")
        )

    def _draw_help(self):
        self.ht.clear()
        if not self.show_help:
            return
        w = self.screen.window_width() // 2
        h = self.screen.window_height() // 2
        x = w - HELP_FONT_WIDTH
        y = -h + 10 + len(HELP_LINES) * 18
        for line in HELP_LINES:
            self.ht.goto(x, y)
            self.ht.color("yellow")
            self.ht.write(line, font=("Courier New", 12, "normal"))
            y -= 18

    def _draw(self, instructions: str):
        stack = []
        forward = self.t.forward
        right = self.t.right
        left = self.t.left
        dist = self.cfg["distance"]
        angle = self.cfg["angle"]

        for cmd in instructions:
            if cmd in ("F", "G"):
                forward(dist)
            elif cmd == "+":
                right(angle)
            elif cmd == "-":
                left(angle)
            elif cmd == "[":
                stack.append((self.t.position(), self.t.heading()))
            elif cmd == "]":
                pos, heading = stack.pop()
                self.t.penup()
                self.t.goto(pos)
                self.t.setheading(heading)
                self.t.pendown()

    # ── controls ───────────────────────────────────────────────────────────────

    def next_iter(self):
        if self.iteration < self.cfg["max_iter"]:
            self.iteration += 1
            self.render()

    def prev_iter(self):
        if self.iteration > 0:
            self.iteration -= 1
            self.render()

    def reset(self):
        self._stop_play()
        self.iteration = self.cfg["start_iter"]
        self.render()

    def toggle_play(self):
        if self.playing:
            self._stop_play()
        else:
            self._start_play()

    def _start_play(self):
        self.playing = True
        self.render()
        self._schedule_next()

    def toggle_help(self):
        self.show_help = not self.show_help
        self._draw_help()
        self.screen.update()

    def _stop_play(self):
        self.playing = False
        self.render()

    def _schedule_next(self):

        def step():
            if not self.playing:
                return
            if self.iteration < self.cfg["max_iter"]:
                self.iteration += 1
                self.render()
                self.screen.ontimer(step, self.cfg["play_interval"])
            else:
                self._stop_play()

        self.screen.ontimer(step, self.cfg["play_interval"])

    def quit(self):
        self.screen.bye()

    # ── key bindings ───────────────────────────────────────────────────────────

    def _bind_keys(self):
        s = self.screen
        s.listen()
        s.onkey(self.next_iter, "Right")
        s.onkey(self.prev_iter, "Left")
        s.onkey(self.reset, "r")
        s.onkey(self.toggle_play, "p")
        s.onkey(self.toggle_help, "h")
        s.onkey(self.quit, "q")

    # ── run ────────────────────────────────────────────────────────────────────

    def run(self):
        turtle.mainloop()


# ── entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw = load_config(sys.argv[1])
    cfg = parse_config(raw)
    app = LSystemApp(cfg)
    app.run()
