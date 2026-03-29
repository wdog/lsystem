# L-System Visualizer

Visualizzatore interattivo di sistemi-L (Lindenmayer Systems) con GUI turtle e configurazione TOML.

## Avvio

```bash
python gui3.py examples/fern.toml
```

## Tasti

| Tasto | Azione |
|-------|--------|
| `→` | iterazione successiva |
| `←` | iterazione precedente |
| `p` | play / pause automatico |
| `r` | reload: rilegge il file TOML e ricomincia |
| `h` | mostra / nascondi help |
| `q` | esci |

---

## Come funziona un sistema-L

Un sistema-L è una grammatica formale che riscrive una stringa di simboli ad ogni iterazione applicando delle **regole di produzione**.

### Esempio minimo — Curva di Koch

```
Assioma:  F
Regola:   F → F+F-F-F+F
Angolo:   90°
```

| Iterazione | Stringa |
|-----------|---------|
| 0 | `F` |
| 1 | `F+F-F-F+F` |
| 2 | `F+F-F-F+F + F+F-F-F+F - F+F-F-F+F - F+F-F-F+F + F+F-F-F+F` |
| … | … |

Ad ogni passo ogni `F` viene sostituito dalla stringa della regola. I simboli senza regola rimangono invariati.

---

## Significato dei simboli (turtle graphics)

| Simbolo | Significato |
|---------|-------------|
| `F` | avanza di `distance` pixel disegnando |
| `G` | avanza di `distance` pixel disegnando (alias di F, usato in alcune grammatiche per distinguere due tipi di linea) |
| `+` | ruota a **destra** di `angle` gradi |
| `-` | ruota a **sinistra** di `angle` gradi |
| `[` | **salva** posizione e direzione nello stack |
| `]` | **ripristina** posizione e direzione dallo stack (crea i rami) |
| `X`, `Y`, `A`, `B`, … | simboli ausiliari: partecipano alle riscritture ma non producono alcun disegno |

### Stack e ramificazioni

`[` e `]` implementano le ramificazioni: la turtle "ricorda" un punto, disegna un ramo, poi torna esattamente dove era. Questo è ciò che permette di generare alberi e felci.

```
F [ + F ] F [ - F ] F
│   └─ ramo destro    │
│              └─ ramo sinistro
└─ tronco
```

---

## Formato file TOML

```toml
title    = "Nome del diagramma"   # titolo della finestra
axiom    = "F"                    # stringa di partenza (iterazione 0)
angle    = 90                     # gradi di rotazione per + e -
distance = 10                     # pixel percorsi da F e G
max_iter = 6                      # iterazione massima raggiungibile con →
start_iter = 0                    # iterazione mostrata all'avvio

start_x       = -300              # posizione X di partenza della turtle
start_y       = 0                 # posizione Y di partenza della turtle
start_heading = 0                 # direzione iniziale in gradi (0 = destra)

bg_color = "black"                # colore sfondo
fg_color = "white"                # colore disegno (usato se colors = [] )
play_interval = 800               # millisecondi tra un'iterazione e la successiva in play

colors = ["white", "cyan", "lime", "yellow"]  # palette per-iterazione (opzionale)

[rules]
F = "F+F-F-F+F"                   # regola di produzione: simbolo = stringa sostituta
```

Tutti i campi sono opzionali tranne `axiom` e `[rules]`. Se `colors` è assente viene usata la palette integrata.

### Palette di default

Ogni iterazione viene disegnata con un colore diverso, ciclando su:

```
0: white   1: cyan   2: lime     3: yellow
4: orange  5: deepskyblue        6: violet  7: hotpink
```

---

## Esempi inclusi

| File | Diagramma | Note |
|------|-----------|------|
| `fern.toml` | Felce di Barnsley | rami ricorsivi con `[` `]` |
| `plant.toml` | Pianta ramificata | variante della felce |
| `tree.toml` | Albero binario | biforcazione simmetrica |
| `dragon_curve.toml` | Curva del drago | curva frattale senza rami |
| `koch_curve.toml` | Curva di Koch | fiocco di neve quadrato |
| `snowflake.toml` | Fiocco di neve di Koch | assioma triangolare |
| `hilbert_curve.toml` | Curva di Hilbert | curva che riempie il piano |
| `gosper_curve.toml` | Curva di Gosper | isola frattale esagonale |
| `sierpinski_triangle.toml` | Triangolo di Sierpiński | frattale triangolare |
| `sierpinski_carpet.toml` | Tappeto di Sierpiński | frattale quadrato |
| `square_spiral.toml` | Spirale quadrata | pattern geometrico |
