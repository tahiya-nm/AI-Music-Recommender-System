# Scoring Rule Design for AI Music Recommender

## Core Idea: Weighted Feature Scoring

The total score for a song is a **weighted sum of per-feature scores**, each normalized to [0, 1]:

```
score(song, user) =
    w_genre    * genre_score(song, user)
  + w_mood     * mood_score(song, user)
  + w_energy   * energy_score(song, user)
  + w_acoustic * acoustic_score(song, user)
```

All weights sum to 1.0, so the final score lives in [0, 1].

---

## Scoring Numerical Features: Gaussian Proximity

For a feature like `energy`, you do NOT want to reward higher values blindly. You want to reward **closeness to the user's target**. The cleanest formula is a **Gaussian (bell curve)**:

```
energy_score = exp( -( (song.energy - user.target_energy)² ) / (2 * σ²) )
```

- Returns **1.0** when `song.energy == user.target_energy` (perfect match)
- Decays symmetrically as the difference grows — no directional bias
- σ (sigma) controls how strict the matching is:
  - σ = 0.15 → tight (only songs within ~0.15 of target score above 0.5)
  - σ = 0.25 → forgiving (songs within ~0.25 still score above 0.5)
- Recommended **σ = 0.20** for the [0, 1] energy scale

This is strictly better than `1 - |diff|` because the curve stays high near the target and falls off more gracefully.

---

## Scoring Categorical Features: Binary Match

For `genre` and `mood`, which are strings:

```
genre_score = 1.0 if song.genre == user.favorite_genre else 0.0
mood_score  = 1.0 if song.mood  == user.favorite_mood  else 0.0
```

Simple binary — no partial credit needed at this scale. If partial credit were wanted later (e.g. "rock is closer to indie pop than to ambient"), a similarity lookup table could replace the binary.

---

## Scoring the Boolean Feature: `likes_acoustic`

`acousticness` is a float [0, 1]. Map the user's boolean preference directly:

```
acoustic_score = song.acousticness        if user.likes_acoustic is True
               = 1.0 - song.acousticness   if user.likes_acoustic is False
```

This rewards high acousticness for acoustic fans and low acousticness for non-acoustic fans.

---

## Weight Hierarchy: Why Genre > Mood

| Feature        | Weight | Rationale |
|----------------|--------|-----------|
| `genre`        | 0.35   | Broadest categorical dimension — defines fundamental sound character (jazz vs rock vs lofi). A mismatch here is almost always a dealbreaker. |
| `mood`         | 0.25   | Second most categorical. Important, but can vary within a genre (e.g. chill rock and intense rock both exist). |
| `energy`       | 0.25   | Strongest *contextual* signal — people listen by energy state (working out vs studying). High value even without a genre/mood match. |
| `acousticness` | 0.15   | Direct binary preference, but less universally decisive than the above three. |

**Key insight on genre vs mood:** Genre encodes timbre, instrumentation, and production style — changes that are hard to overlook. Mood is a softer label that often emerges from energy + valence anyway, so it is partially redundant with the numerical features and gets a smaller weight. Genre carries more independent information.

---

## Full Score Formula

```python
import math

SIGMA = 0.20
WEIGHTS = {"genre": 0.35, "mood": 0.25, "energy": 0.25, "acoustic": 0.15}

def gaussian(song_val: float, target: float, sigma: float = SIGMA) -> float:
    return math.exp(-((song_val - target) ** 2) / (2 * sigma ** 2))

def score_song(song: Song, user: UserProfile) -> float:
    genre_s    = 1.0 if song.genre == user.favorite_genre else 0.0
    mood_s     = 1.0 if song.mood  == user.favorite_mood  else 0.0
    energy_s   = gaussian(song.energy, user.target_energy)
    acoustic_s = song.acousticness if user.likes_acoustic else (1.0 - song.acousticness)

    return (
        WEIGHTS["genre"]    * genre_s +
        WEIGHTS["mood"]     * mood_s +
        WEIGHTS["energy"]   * energy_s +
        WEIGHTS["acoustic"] * acoustic_s
    )
```

`recommend()` then calls `score_song` for every song, sorts descending, and returns top-k.

---

## Why You Need Both a Scoring Rule and a Ranking Rule

These two rules are distinct because they operate at different scopes and carry different responsibilities.

**Scoring Rule** — answers the question *"How good is this one song for this user?"*
- Takes a single `(song, user)` pair, returns a scalar in [0, 1]
- It is **stateless across songs**: it only needs one song at a time and knows nothing about the rest of the catalog
- This means scores can be computed independently (and in parallel) for every song

**Ranking Rule** — answers the question *"Given all the scores, which songs surface to the top?"*
- Takes the full list of `(song, score)` pairs and produces a final ordered list
- It is **stateful across songs**: it must see all candidates together to decide the ordering
- The simplest version is `sort descending by score, take top-k`

**Why the split matters:**

1. **Separation of concerns.** The scoring function doesn't need to know about other songs. The ranking function doesn't need to know about the user or the feature weights. Each does one job.

2. **Ranking can enforce constraints that scoring cannot.** For example: "no more than 2 songs from the same artist in the top 5" or "guarantee genre diversity." These rules require seeing the whole list — you can't enforce them one song at a time.

3. **Swappable components.** You can change the scoring formula (e.g., adjust weights or switch from Gaussian to linear decay) without touching the ranking step. Or you can swap simple sort-by-score for probabilistic sampling (weighted random draw proportional to scores, for freshness) without touching `score_song`.

**Concrete analogy:** A rubric for grading job applications (scoring rule) rates each candidate on fixed criteria independently. The hiring panel (ranking rule) then looks at all scores together and picks the top candidates — possibly with additional constraints like "at least one candidate per department."

For this recommender:
- `score_song(song, user) → float` is the Scoring Rule
- `sorted(scored_songs, key=lambda x: x[1], reverse=True)[:k]` is the simplest Ranking Rule — and the right place to add any future diversity or constraint logic
