# Générer des GIF animés avec Pillow

Guide précis basé sur la documentation officielle **Pillow 12.3.0**  
Sources principales :

- [Image file formats — GIF](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif)
- [Image.save()](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save)
- [ImageSequence](https://pillow.readthedocs.io/en/stable/reference/ImageSequence.html)
- [ImageDraw](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html) / [ImageFilter](https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html)

Implémentation dans ce skill : `scripts/gif_utils.py` + `scripts/create_gif.py` (`toss` = logo qui monte → tourne → redescend).

---

## 1. Installation

```bash
pip install pillow
# ou
python3 -m pip install pillow
```

Via Meta-Skills (venv partagé) :

```bash
cd ~/.meta-skills/skills/gif-creator
~/.meta-skills/install.sh pip init .
```

Vérifier la version :

```python
import PIL
print(PIL.__version__)  # ex. 12.3.0
```

---

## 2. Ce qu’est un GIF pour Pillow

D’après la doc officielle :

| Point | Détail |
|---|---|
| Versions lues | GIF87a et GIF89a |
| Écriture | GIF87a par défaut ; GIF89a si des features GIF89a sont utilisées |
| Compression | LZW |
| Mode à l’ouverture | `L` (niveaux de gris) ou `P` (palette, max **256 couleurs**) |
| Frames suivantes | Un frame `P` peut passer en `RGB` / `RGBA` (chaque frame peut avoir sa palette) |
| Transparence | **1 index de palette** transparent (pas d’alpha 0–255 comme le PNG) |

Conséquence importante : **pas de vraie semi-transparence** dans un GIF.  
Pour une ombre “à 30 % / 70 %”, il faut tricher (taille, gris, ou dither) — le format ne stocke pas d’alpha partiel.

---

## 3. Minimal : créer un GIF animé

Pattern officiel :

```python
from PIL import Image

# frames : liste d'images PIL (même taille recommandée)
frames = [...]  # Image.Image en mode P, RGB, RGBA, etc.

frames[0].save(
    "out.gif",
    save_all=True,
    append_images=frames[1:],
    duration=40,   # ms par frame
    loop=0,        # 0 = boucle infinie
)
```

- Appeler `save()` sur **la première frame**
- Passer le reste dans `append_images`
- Ne pas faire `append_images=frames` sinon la frame 0 est dupliquée

---

## 4. Options `save()` spécifiques au GIF (doc officielle)

### Options d’animation / multi-frame

| Option | Type | Description |
|---|---|---|
| `save_all` | `bool` | Si `True` (ou si `append_images` non vide), sauve **toutes** les frames. Sinon, seulement la première. |
| `append_images` | `list[Image]` | Frames supplémentaires. Chaque élément peut être mono ou multi-frame. |
| `duration` | `int` \| `list` \| `tuple` | Durée d’affichage en **millisecondes**. Une valeur = constante ; une liste = une durée par frame. |
| `loop` | `int` \| `None` | Nombre de boucles. **`0` = infini**. Si omis / `None` → **ne boucle pas**. |
| `disposal` | `int` \| `list` \| `tuple` | Que faire de la frame après affichage (voir ci-dessous). |
| `transparency` | `int` | Index de couleur transparent dans la palette. |
| `optimize` | `bool` | Compresse la palette + marque les pixels inchangés comme transparents (défaut souvent `True`). |
| `palette` | `bytes` \| `bytearray` \| `ImagePalette` | Palette RGBRGB… (≤ 768 bytes) ou objet `ImagePalette`. |
| `include_color_table` | `bool` | Inclure une table de couleurs locale. |
| `interlace` | `bool` | Entrelacement. Défaut : oui, sauf si largeur ou hauteur < 16. |
| `comment` | `str` / bytes | Commentaire GIF. |

### `disposal` (valeurs officielles)

| Valeur | Signification |
|---|---|
| `0` | Non spécifié |
| `1` | Ne pas disposer (laisser la frame) |
| `2` | **Restaurer la couleur de fond** (recommandé pour animations transparentes) |
| `3` | Restaurer le contenu précédent |

Pour un logo animé sur fond transparent, utilise presque toujours :

```python
disposal=2,
optimize=False,   # évite des bugs de transparence / pixels “mangés”
```

---

## 5. Lire un GIF existant

### Infos (`im.info`) à l’ouverture

| Clé | Contenu |
|---|---|
| `background` | Index couleur de fond |
| `transparency` | Index transparent (absent si opaque) |
| `version` | `"GIF87a"` ou `"GIF89a"` |
| `duration` | ms de la frame courante (peut être absent) |
| `loop` | `0` = infini (peut être absent) |
| `comment` | Commentaire |
| `extension` | Infos applicatives |

### Parcourir les frames

**Méthode A — `seek` / `tell` :**

```python
from PIL import Image

with Image.open("anim.gif") as im:
    print(im.n_frames, im.info)
    im.seek(0)
    while True:
        im.save(f"frame_{im.tell():03d}.png")
        try:
            im.seek(im.tell() + 1)
        except EOFError:
            break
```

**Méthode B — `ImageSequence.Iterator` (recommandé) :**

```python
from PIL import Image, ImageSequence

with Image.open("anim.gif") as im:
    for i, frame in enumerate(ImageSequence.Iterator(im)):
        frame.save(f"frame_{i:03d}.png")
```

**Méthode C — `ImageSequence.all_frames` :**

```python
from PIL import Image, ImageSequence

with Image.open("anim.gif") as im:
    frames = ImageSequence.all_frames(im)  # list[Image]
    # ou avec transform :
    frames = ImageSequence.all_frames(im, func=lambda f: f.convert("RGBA"))
```

### Stratégie de chargement des palettes

```python
from PIL import GifImagePlugin

# Défaut : P → RGB/RGBA seulement après la 1re frame
GifImagePlugin.LOADING_STRATEGY = (
    GifImagePlugin.LoadingStrategy.RGB_AFTER_FIRST
)

# Toujours convertir en RGB/RGBA
GifImagePlugin.LOADING_STRATEGY = (
    GifImagePlugin.LoadingStrategy.RGB_ALWAYS
)

# Rester en P tant que la palette globale le permet
GifImagePlugin.LOADING_STRATEGY = (
    GifImagePlugin.LoadingStrategy.RGB_AFTER_DIFFERENT_PALETTE_ONLY
)
```

---

## 6. Pipeline recommandé pour **générer** un GIF

### Étape A — Produire des frames RGBA

Travaille en `RGBA` pour composer (rotation, ombre, etc.) :

```python
from PIL import Image, ImageDraw, ImageFilter

canvas = Image.new("RGBA", (400, 400), (0, 0, 0, 0))  # fond transparent
logo = Image.open("logo.png").convert("RGBA")
rotated = logo.rotate(45, resample=Image.Resampling.BICUBIC, expand=True)
canvas.alpha_composite(rotated, (x, y))
```

API utiles :

| API | Usage |
|---|---|
| `Image.open(...).convert("RGBA")` | Charger en RGBA |
| `Image.new("RGBA", size, color)` | Canvas |
| `Image.rotate(angle, expand=True, resample=...)` | Rotation |
| `Image.resize((w, h), Image.Resampling.LANCZOS)` | Scale |
| `Image.alpha_composite(a, b)` | Composer avec alpha |
| `Image.paste(im, box, mask)` | Coller avec masque |
| `ImageDraw.Draw(im).ellipse(...)` | Dessiner ombre / formes |
| `ImageFilter.GaussianBlur(radius=...)` | Flou |

### Étape B — Convertir RGBA → mode `P` + transparence

Le GIF veut une **palette**. Pattern robuste (implémenté dans `scripts/gif_utils.py` → `rgba_to_gif_frame`) :

```python
def rgba_to_gif_frame(im: Image.Image, transparent_index: int = 255) -> Image.Image:
    """RGBA → P avec 1 index transparent (doc: transparency = color index)."""
    im = im.convert("RGBA")
    alpha = im.getchannel("A")

    # Seuil : en dessous = transparent (GIF = binaire)
    mask = alpha.point(lambda a: 255 if a >= 8 else 0)

    # Image opaque pour la quantification
    solid = Image.new("RGBA", im.size, (0, 0, 0, 0))
    solid.paste(im, mask=mask)

    # Palette ≤ 255 couleurs (garde l'index 255 pour la transparence)
    quantized = solid.convert("RGB").quantize(
        colors=255,
        method=Image.Quantize.FASTOCTREE,  # ou MEDIANCUT
    )

    # Remapper les pixels transparents vers transparent_index
    q_pixels = list(quantized.getdata())
    a_pixels = list(mask.getdata())
    mapped = [
        transparent_index if a < 8 else (idx if idx < transparent_index else transparent_index - 1)
        for idx, a in zip(q_pixels, a_pixels)
    ]

    palette = quantized.getpalette() or []
    palette = palette[: transparent_index * 3]
    while len(palette) < transparent_index * 3:
        palette.extend([0, 0, 0])
    palette.extend([0, 0, 0])  # entrée pour l'index transparent

    out = Image.new("P", im.size)
    out.putpalette(palette)
    out.putdata(mapped)
    out.info["transparency"] = transparent_index
    return out
```

### Étape C — Sauver

```python
gif_frames = [rgba_to_gif_frame(f) for f in frames_rgba]

gif_frames[0].save(
    "out.gif",
    format="GIF",
    save_all=True,
    append_images=gif_frames[1:],
    duration=1000 // 24,  # ~24 fps
    loop=0,
    disposal=2,
    transparency=255,
    optimize=False,
)
```

---

## 7. Durée, FPS, boucle

```text
duration_ms = 1000 / fps
```

Exemples :

| FPS | `duration` |
|---|---|
| 10 | 100 |
| 20 | 50 |
| 24 | ≈ 41 |
| 30 | ≈ 33 |

Durées variables par frame :

```python
duration=[40, 40, 40, 200, 40, 40]  # une frame “pause”
```

`loop` :

| Valeur | Effet |
|---|---|
| `0` | Boucle infinie |
| `1` | Joue 1 fois puis s’arrête (selon lecteurs) |
| omis / `None` | **Ne boucle pas** (doc Pillow) |

---

## 8. Transparence : pièges (très important)

1. **Pas d’alpha partiel** — seulement un index 100 % transparent.
2. **`disposal=2`** — sinon les frames se superposent (fantômes).
3. **`optimize=False`** — l’optimiseur peut rendre transparents des pixels “inchangés” et casser l’anim.
4. **Ne pas utiliser du gris clair pour une ombre “transparente”** sur fond sombre : ça devient une ombre blanche. Préférer un **bloc noir** + taille variable, ou un dither noir.
5. Toutes les frames devraient avoir **la même taille** (logical screen).

### Ombre “plus / moins transparente”

Comme le GIF ne peut pas, options :

| Technique | Rendu | Quand l’utiliser |
|---|---|---|
| Ellipse **noire solide**, taille variable | Propre | Ombre au sol (recommandé) |
| Gris | Ressemble à du blanc sur fond sombre | À éviter pour une ombre |
| Dither (Bayer, etc.) | Points noirs | Si tu acceptes le grain |

---

## 9. Recette complète : anim “monte → tourne → descend”

Voir `scripts/gif_utils.py` → `make_toss_gif` / CLI :

```bash
python scripts/create_gif.py toss logo.png out.gif --fps 24 --duration 3
```

```python
from PIL import Image, ImageDraw
import math
from pathlib import Path

def ease_in_out(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * t)

def make_toss_gif(
    src: Path,
    dest: Path,
    *,
    max_width: int = 220,
    lift: int = 48,
    fps: int = 24,
    duration_s: float = 3.0,
) -> None:
    logo = Image.open(src).convert("RGBA")
    if logo.width > max_width:
        r = max_width / logo.width
        logo = logo.resize((max_width, int(logo.height * r)), Image.Resampling.LANCZOS)

    pad = 28
    canvas_w = logo.width + pad * 2
    canvas_h = logo.height + lift + pad * 2
    n = int(fps * duration_s)
    duration_ms = 1000 // fps

    frames_rgba = []
    for i in range(n):
        t = i / (n - 1)

        # 0–30% monte, 30–60% tourne en haut, 60–100% descend
        if t <= 0.30:
            p = ease_in_out(t / 0.30)
            y, angle = -lift * p, 0.0
        elif t <= 0.60:
            p = (t - 0.30) / 0.30
            y, angle = -lift, 360.0 * ease_in_out(p)
        else:
            p = ease_in_out((t - 0.60) / 0.40)
            y, angle = -lift * (1.0 - p), 360.0

        height = min(1.0, max(0.0, abs(y) / lift))
        # ombre plus petite en haut (simule plus de transparence)
        scale = 1.0 - 0.55 * height

        rotated = logo.rotate(-angle, resample=Image.Resampling.BICUBIC, expand=True)
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

        # Ombre noire solide (pas de gris, pas de dither)
        sw = max(12, int(logo.width * 0.55 * scale))
        sh = max(4, int(10 * scale))
        shadow = Image.new("RGBA", (sw + 6, sh + 6), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse((3, 3, 3 + sw - 1, 3 + sh - 1), fill=(0, 0, 0, 255))
        floor_y = pad + lift + logo.height - 10
        canvas.alpha_composite(shadow, ((canvas_w - shadow.width) // 2, floor_y - shadow.height // 2))

        x = (canvas_w - rotated.width) // 2
        y_pos = int(pad + lift + y - (rotated.height - logo.height) / 2)
        canvas.alpha_composite(rotated, (x, y_pos))
        frames_rgba.append(canvas)

    # Conversion P + save (voir section 6)
    gif_frames = [rgba_to_gif_frame(f) for f in frames_rgba]  # fonction de la section 6
    gif_frames[0].save(
        dest,
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
        transparency=255,
        optimize=False,
    )
```

---

## 10. Checklist anti-bugs

- [ ] `save_all=True` + `append_images=frames[1:]`
- [ ] `loop=0` si tu veux une boucle infinie
- [ ] `duration` en **ms**, pas en secondes
- [ ] `disposal=2` pour fond transparent
- [ ] `optimize=False` si transparences bizarres
- [ ] Frames en mode `P` avec `transparency=<index>`
- [ ] Même taille pour toutes les frames
- [ ] Ombre = **noir**, pas gris (sinon “ombre blanche”)
- [ ] Pas d’attente d’alpha partiel dans le GIF

---

## 11. Alternatives si le GIF te limite

| Besoin | Format |
|---|---|
| Vraie transparence partielle + anim | **APNG** (`save_all=True` sur PNG) ou **WebP** animé |
| Meilleure qualité / taille | WebP / MP4 + `ffmpeg` |
| Simple partage | GIF reste le plus compatible |

WebP animé (si support compilé) :

```python
frames[0].save(
    "out.webp",
    save_all=True,
    append_images=frames[1:],
    duration=40,
    loop=0,
    lossless=True,
)
```

---

## 12. Liens doc officielle (à garder)

1. GIF format : https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif  
2. `Image.save` : https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save  
3. `ImageSequence` : https://pillow.readthedocs.io/en/stable/reference/ImageSequence.html  
4. Concepts (modes `P`, `RGBA`, etc.) : https://pillow.readthedocs.io/en/stable/handbook/concepts.html  
5. `ImageDraw` : https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html  
6. `ImageFilter` : https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html  
7. `ImagePalette` : https://pillow.readthedocs.io/en/stable/reference/ImagePalette.html  

---

## 13. Référence rapide `save()` GIF

```python
im.save(
    "out.gif",
    format="GIF",          # optionnel si extension .gif
    save_all=True,         # obligatoire pour multi-frame
    append_images=[...],   # frames 1..n
    duration=40,           # ms (int ou list)
    loop=0,                # 0 = forever
    disposal=2,            # clear to background
    transparency=255,      # index palette transparent
    optimize=False,        # plus sûr avec transparence
    palette=None,          # optionnel
    interlace=False,       # optionnel
    comment="meta-skills", # optionnel
)
```

Document basé sur Pillow **12.3.0** (handbook *Image file formats → GIF*).  
Si tu changes de version majeure, revérifie la page officielle : les options GIF évoluent peu, mais les détails d’`optimize` / transparence peuvent bouger.
