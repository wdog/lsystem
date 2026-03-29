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

DEFAULT_PALETTE = (
    "white",
    "cyan",
    "lime",
    "yellow",
    "orange",
    "deepskyblue",
    "violet",
    "hotpink",
)

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # pip install tomli
    except ImportError:
        sys.exit("Richiede Python 3.11+ oppure: pip install tomli")


# ── config loader ──────────────────────────────────────────────────────────────


def load_config(path: str) -> dict:
    """Legge il file TOML e restituisce il dizionario grezzo."""
    with open(path, "rb") as f:
        return tomllib.load(f)


def parse_config(cfg: dict) -> dict:
    """Normalizza il dizionario TOML applicando i valori di default."""
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
        "start_x": float(cfg.get("start_x", 0)),
        "start_y": float(cfg.get("start_y", 0)),
        "start_heading": float(cfg.get("start_heading", 0)),
        "title": str(cfg.get("title", "L-System")),
        "colors": list(cfg.get("colors", [])),
    }


# ── L-System ───────────────────────────────────────────────────────────────────


def expand_one(s: str, rules: dict) -> str:
    """Espande una singola iterazione dalla stringa precedente."""
    return "".join(rules.get(c, c) for c in s)

    # result = []
    # for c in s:
    #     result.append(rules.get(c, c))
    # return "".join(result)


# ── Model ──────────────────────────────────────────────────────────────────────

HELP_LINES = [
    "  ←  / →   prev / next",
    "  p        play / pause",
    "  r        reload",
    "  h        toggle help",
    "  q        quit",
]


class LSystemModel:
    """Gestisce l'assioma, le regole e la cache lazy delle iterazioni."""

    def __init__(self, axiom: str, rules: dict, max_iter: int) -> None:
        self._rules = rules
        self.max_iter = max_iter
        self._cache = [axiom]
        print(f"Iter  0 | len {len(axiom):>8}")
        print(axiom)

    def get(self, n: int) -> str:
        """Restituisce la stringa dell'iterazione n, espandendo la cache se necessario."""
        while len(self._cache) <= n:
            i = len(self._cache)
            s = expand_one(self._cache[-1], self._rules)
            self._cache.append(s)
            print(f"Iter {i:>2} | len {len(s):>8}")
            print(s)
        return self._cache[n]


# ── Renderer ───────────────────────────────────────────────────────────────────


class LSystemRenderer:
    """Possiede lo schermo e le tre turtle; espone metodi di disegno puri."""

    def __init__(self, cfg: dict) -> None:
        self._cfg = cfg
        self._colors = cfg["colors"]

        self.screen = turtle.Screen()
        self.screen.setup(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.screen.title(cfg["title"])
        self.screen.bgcolor(cfg["bg_color"])
        self.screen.tracer(0, 0)

        # turtle principale per il disegno del frattale
        self.t = turtle.Turtle()
        self.t.speed(0)
        self.t.hideturtle()
        self.t.color(cfg["fg_color"])

        # turtle dedicata all'overlay di aiuto (sempre sopra)
        self.ht = turtle.Turtle()
        self.ht.speed(0)
        self.ht.hideturtle()
        self.ht.penup()

        # turtle dedicata alle etichette info (iter/len, nome file)
        self.it = turtle.Turtle()
        self.it.speed(0)
        self.it.hideturtle()
        self.it.penup()

    def resolve_color(self, iteration: int) -> str:
        """Restituisce il colore per l'iterazione data, ciclando sulla palette."""
        palette = self._colors or list(DEFAULT_PALETTE)
        return palette[iteration % len(palette)]

    def reset_drawing_turtle(self, color: str) -> None:
        """Cancella il disegno, resetta la turtle e la posiziona al punto di partenza."""
        self.t.reset()
        self.t.hideturtle()
        self.t.speed(0)
        self.t.color(color)
        self.t.penup()
        self.t.goto(self._cfg["start_x"], self._cfg["start_y"])
        self.t.setheading(self._cfg["start_heading"])
        self.t.pendown()

    def position_drawing_turtle(self, color: str) -> None:
        """Riposiziona la turtle al punto di partenza con il nuovo colore, senza cancellare."""
        self.t.penup()
        self.t.goto(self._cfg["start_x"], self._cfg["start_y"])
        self.t.setheading(self._cfg["start_heading"])
        self.t.color(color)
        self.t.pendown()

    def draw(self, instructions: str) -> None:
        """Interpreta la stringa L-System e disegna con la turtle.

        Simboli supportati:
          F, G  avanza di `distance`
          +     ruota a destra di `angle`
          -     ruota a sinistra di `angle`
          [     salva posizione e direzione nello stack
          ]     ripristina posizione e direzione dallo stack
        """
        stack = []
        forward = self.t.forward
        right = self.t.right
        left = self.t.left
        dist = self._cfg["distance"]
        angle = self._cfg["angle"]

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

    def draw_info(self, iteration: int, length: int, name: str) -> None:
        """Disegna in alto a sinistra iter/len e in basso a sinistra il nome del file."""
        self.it.clear()
        w = self.screen.window_width() // 2
        h = self.screen.window_height() // 2
        self.it.goto(-w + 10, h - 24)
        self.it.color("yellow")
        self.it.write(
            f"ITER {iteration}   LEN {length}",
            font=("Courier New", 13, "bold"),
        )
        self.it.goto(-w + 10, -h + 10)
        self.it.color("cyan")
        self.it.write(
            name,
            font=("Courier New", 13, "bold"),
        )

    def draw_help(self, show: bool) -> None:
        """Disegna (o cancella) l'overlay con i tasti di scelta rapida."""
        self.ht.clear()
        if not show:
            return
        w = self.screen.window_width() // 2
        h = self.screen.window_height() // 2
        x = w - HELP_FONT_WIDTH
        y = -h + 10 + len(HELP_LINES) * 18
        for line in HELP_LINES:
            self.ht.goto(x, y)
            self.ht.color("lime")
            self.ht.write(line, font=("Courier New", 12, "normal"))
            y -= 18

    def update(self) -> None:
        """Aggiorna la finestra (flush del double buffer)."""
        self.screen.update()

    def set_title(self, text: str) -> None:
        """Imposta il titolo della finestra."""
        self.screen.title(text)

    def bind_keys(self, bindings: dict) -> None:
        """Registra i tasti di scelta rapida dalla mappa {tasto: callback}."""
        self.screen.listen()
        for key, fn in bindings.items():
            self.screen.onkey(fn, key)

    def ontimer(self, fn, delay_ms: int) -> None:
        """Pianifica la chiamata di fn dopo delay_ms millisecondi."""
        self.screen.ontimer(fn, delay_ms)

    def bye(self) -> None:
        """Chiude la finestra turtle."""
        self.screen.bye()


# ── App ────────────────────────────────────────────────────────────────────────


class LSystemApp:
    """Orchestratore: collega model e renderer, gestisce stato e playback."""

    def __init__(self, cfg: dict, cfg_path: str) -> None:
        self.cfg = cfg
        self._cfg_path = cfg_path
        self.iteration = cfg["start_iter"]
        self.playing = False
        self.show_help = True

        self.model = LSystemModel(cfg["axiom"], cfg["rules"], cfg["max_iter"])
        self.renderer = LSystemRenderer(cfg)
        self._drawn_iter = -1  # ultimo layer disegnato sullo schermo (-1 = nulla)

        self.renderer.bind_keys({
            "Right": self.next_iter,
            "Left":  self.prev_iter,
            "r":     self.reload,
            "p":     self.toggle_play,
            "h":     self.toggle_help,
            "q":     self.quit,
        })
        self.render()

    # ── rendering ──────────────────────────────────────────────────────────────

    def render(self) -> None:
        """Disegno cumulativo: aggiunge layer andando avanti, ridisegna tutto andando indietro."""
        if self._drawn_iter < 0 or self.iteration < self._drawn_iter:
            self._full_redraw()
        elif self.iteration > self._drawn_iter:
            for i in range(self._drawn_iter + 1, self.iteration + 1):
                self._draw_layer(i)
            self._drawn_iter = self.iteration

        instructions = self.model.get(self.iteration)
        self.renderer.draw_info(self.iteration, len(instructions), self.cfg["name"])
        self.renderer.draw_help(self.show_help)
        self.renderer.update()
        self.renderer.set_title(
            f"{self.cfg['title']} — iter {self.iteration}"
            + (" ▶" if self.playing else "")
        )

    def _full_redraw(self) -> None:
        """Cancella lo schermo e ridisegna tutti i layer da 0 all'iterazione corrente."""
        self.renderer.reset_drawing_turtle(self.renderer.resolve_color(0))
        self.renderer.draw(self.model.get(0))
        for i in range(1, self.iteration + 1):
            self._draw_layer(i)
        self._drawn_iter = self.iteration

    def _draw_layer(self, i: int) -> None:
        """Aggiunge il layer i sopra i layer già disegnati."""
        self.renderer.position_drawing_turtle(self.renderer.resolve_color(i))
        self.renderer.draw(self.model.get(i))

    # ── controls ───────────────────────────────────────────────────────────────

    def next_iter(self) -> None:
        """Avanza di un'iterazione (tasto →)."""
        if self.iteration < self.cfg["max_iter"]:
            self.iteration += 1
            self.render()

    def prev_iter(self) -> None:
        """Torna all'iterazione precedente (tasto ←)."""
        if self.iteration > 0:
            self.iteration -= 1
            self.render()

    def reload(self) -> None:
        """Rilegge il file TOML, reinizializza il model e torna all'iterazione iniziale (tasto r)."""
        self.playing = False
        import os
        raw = load_config(self._cfg_path)
        cfg = parse_config(raw)
        cfg["name"] = os.path.splitext(os.path.basename(self._cfg_path))[0]
        self.cfg = cfg
        self.renderer._cfg = cfg
        self.renderer._colors = cfg["colors"]
        self.renderer.screen.bgcolor(cfg["bg_color"])
        self.model = LSystemModel(cfg["axiom"], cfg["rules"], cfg["max_iter"])
        self.iteration = cfg["start_iter"]
        self._drawn_iter = -1
        self.render()

    def toggle_play(self) -> None:
        """Avvia o ferma la riproduzione automatica (tasto p)."""
        if self.playing:
            self._stop_play()
        else:
            self._start_play()

    def _start_play(self) -> None:
        """Imposta il flag playing e avvia il timer ricorsivo."""
        self.playing = True
        self.render()
        self._schedule_next()

    def toggle_help(self) -> None:
        """Mostra o nasconde l'overlay di aiuto (tasto h)."""
        self.show_help = not self.show_help
        self.renderer.draw_help(self.show_help)
        self.renderer.update()

    def _stop_play(self) -> None:
        """Ferma la riproduzione automatica."""
        self.playing = False
        self.render()

    def _schedule_next(self) -> None:
        """Pianifica il prossimo step di play tramite ontimer (non blocca la UI)."""

        def step():
            if not self.playing:
                return
            if self.iteration < self.cfg["max_iter"]:
                self.iteration += 1
                self.render()
                self.renderer.ontimer(step, self.cfg["play_interval"])
            else:
                self._stop_play()

        self.renderer.ontimer(step, self.cfg["play_interval"])

    def quit(self) -> None:
        """Chiude la finestra (tasto q)."""
        self.renderer.bye()

    # ── run ────────────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Avvia il loop principale della GUI."""
        turtle.mainloop()


# ── entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    import os
    cfg_path = sys.argv[1]
    cfg_name = os.path.splitext(os.path.basename(cfg_path))[0]
    raw = load_config(cfg_path)
    cfg = parse_config(raw)
    cfg["name"] = cfg_name
    app = LSystemApp(cfg, cfg_path)
    app.run()
