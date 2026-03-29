# L-System Visualizer

Visualizzatore interattivo di sistemi-L (Lindenmayer Systems) con GUI turtle e configurazione TOML.

## Installazione con `venv` e `pip`

Requisiti:

- Python 3.11+ consigliato
- Su Linux potrebbe essere necessario avere `tkinter`/Tk installato a livello di sistema per usare `turtle`

Creazione ambiente virtuale e installazione dipendenze:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Se usi Python 3.11 o superiore, il parser TOML è già incluso nella standard library.
Con Python 3.10 o inferiore verrà installato `tomli` da `requirements.txt`.

## Avvio rapido

```bash
python gui3.py examples/fern.toml
```

Altri esempi:

```bash
python gui3.py examples/koch_curve.toml
python gui3.py examples/sierpinski_triangle.toml
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

## Struttura del progetto

| Percorso | Descrizione |
|----------|-------------|
| `gui3.py` | applicazione principale con GUI `turtle` e caricamento configurazioni TOML |
| `examples/` | raccolta di sistemi-L pronti da eseguire |
| `requirements.txt` | dipendenze Python minime del progetto |

---

## Come funziona un sistema-L

Un sistema-L è un sistema di riscrittura: parte da una stringa iniziale e, ad ogni iterazione, sostituisce i simboli secondo regole fisse.

In pratica funziona cosi:

1. si parte da un **assioma**, cioe la stringa iniziale
2. si applicano le **regole di produzione** a ogni simbolo della stringa corrente
3. si ottiene una nuova stringa
4. quella nuova stringa viene usata per l'iterazione successiva

La stringa risultante non e ancora un disegno: e una sequenza di istruzioni.
Nel progetto queste istruzioni vengono lette dalla `turtle`, che trasforma simboli come `F`, `+`, `-`, `[` e `]` in linee, rotazioni e ramificazioni.

### I tre elementi fondamentali

- **Assioma**: il punto di partenza
- **Regole**: dicono come si espande ogni simbolo
- **Interpretazione grafica**: dice cosa deve fare la turtle quando incontra un simbolo

Questo e il motivo per cui i sistemi-L sono potenti: con poche regole locali si possono ottenere strutture molto ricche e ripetitive.

### Riscrittura simultanea

Un dettaglio importante e che la riscrittura avviene in modo simultaneo sull'intera stringa.
Non si modifica la stringa "mentre la si legge"; si costruisce una nuova stringa completa a partire dalla precedente.

Esempio:

```text
Stringa corrente:  F-G
Regole:            F -> FF
                   G -> G+F

Nuova stringa:     FF-G+F
```

Prima si legge `F-G`, poi si genera tutta la nuova stringa `FF-G+F`.
Questo rende il comportamento regolare e ripetibile ad ogni iterazione.

### Esempio minimo — Curva di Koch

```
Assioma:  F
Regola:   F → F+F-F-F+F
Angolo:   90°
```

Interpretazione intuitiva dei simboli:

- `F` = vai avanti disegnando
- `+` = ruota a destra
- `-` = ruota a sinistra

| Iterazione | Stringa |
|-----------|---------|
| 0 | `F` |
| 1 | `F+F-F-F+F` |
| 2 | `F+F-F-F+F + F+F-F-F+F - F+F-F-F+F - F+F-F-F+F + F+F-F-F+F` |
| … | … |

Ad ogni passo ogni `F` viene sostituito dalla stringa della regola.
I simboli che non hanno una regola, come `+` e `-`, restano invariati.

Quindi:

- la parte "grammaticale" decide come cresce la stringa
- la parte "grafica" decide come quella stringa viene disegnata

### Simboli visibili e simboli ausiliari

Non tutti i simboli devono per forza disegnare qualcosa.

- `F` e `G` di solito producono linee
- `+` e `-` cambiano solo orientamento
- `[` e `]` servono per salvare e ripristinare posizione e direzione
- `X`, `Y`, `A`, `B` possono essere usati solo per controllare la crescita della stringa

Questo permette di costruire grammatiche molto espressive: alcuni simboli servono al disegno, altri servono solo alla logica di espansione.

### Perche generano frattali e forme naturali

I sistemi-L ripetono la stessa logica molte volte su strutture sempre piu grandi.
Per questo producono facilmente:

- autosimilarita
- curve frattali
- ramificazioni
- forme che ricordano alberi, felci e piante

In altre parole, una regola semplice applicata tante volte puo creare forme che sembrano complesse o organiche.

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
