# Feature Effectiveness for Content-Based Recommendation

## Data Overview

**File:** `data/songs.csv` — 10 songs, no missing values

| Feature | Type | Range / Values |
|---|---|---|
| genre | categorical | pop, lofi, rock, ambient, jazz, synthwave, indie pop (7 distinct) |
| mood | categorical | happy, chill, intense, relaxed, moody, focused (6 distinct) |
| energy | float | 0.28 – 0.93 |
| acousticness | float | 0.05 – 0.92 |
| valence | float | 0.48 – 0.84 |
| danceability | float | 0.41 – 0.88 |
| tempo_bpm | float | 60 – 152 BPM |
| artist | categorical | 10 unique artists |
| title | string | unique identifiers |
| id | int | row index |

**UserProfile attributes:**
- `favorite_genre` (str)
- `favorite_mood` (str)
- `target_energy` (float)
- `likes_acoustic` (bool)

---

## Tier 1 — High Impact

### genre
- 7 distinct genres — strong discriminative power
- Binary match signal (1 or 0) is simple and interpretable
- Direct 1:1 mapping to `favorite_genre` in UserProfile

### mood
- 6 distinct moods; users naturally think in these terms (e.g., "I want chill music")
- Strong proxy for emotional context and listening situation
- Direct 1:1 mapping to `favorite_mood` in UserProfile

### energy
- Widest variance of all numerics (0.28–0.93) — highly discriminating
- Score with: `1 - abs(song.energy - user.target_energy)`
- Direct 1:1 mapping to `target_energy` in UserProfile

### acousticness
- Very high variance (0.05–0.92); near-bimodal split between acoustic and electronic
- Score with: `song.acousticness` if `likes_acoustic` else `1 - song.acousticness`
- Direct 1:1 mapping to `likes_acoustic` in UserProfile

### valence
- Correlated with mood but not redundant — two songs can share a mood label while differing in valence (e.g., lofi "chill" vs ambient "chill")
- Breaks ties within the mid-energy cluster where genre and mood are both 0
- Score with: `1 - abs(song.valence - user.target_valence)`
- Direct 1:1 mapping to `target_valence` in UserProfile

---

## Tier 2 — Supplementary

### danceability
- Captures a distinct axis from energy, though correlated
- Useful if a "wants to dance" preference is added to UserProfile

### tempo_bpm
- Meaningful for workout or focus contexts
- Normalize before scoring: `tempo / 200`
- No current UserProfile field maps to it

---

## Tier 3 — Skip

| Feature | Reason |
|---|---|
| artist | Only 1–2 songs per artist — no generalizable signal, adds noise |
| title | Pure metadata, no content value |
| id | Row index only |

---

## Recommended Scoring Formula

A weighted sum with all components normalized to [0, 1]:

```
score = (0.35 × genre_match)
      + (0.20 × mood_match)
      + (0.25 × (1 - |song.energy - user.target_energy|))
      + (0.10 × (1 - |song.valence - user.target_valence|))
      + (0.10 × acousticness_score)
```

Where:
- `genre_match` = 1 if `song.genre == user.favorite_genre` else 0
- `mood_match` = 1 if `song.mood == user.favorite_mood` else 0
- `acousticness_score` = `song.acousticness` if `user.likes_acoustic` else `1 - song.acousticness`

**Weight rationale:** Genre is the strongest stated preference, energy is the most discriminating numeric feature, mood is a direct label match, and valence + acousticness act as continuous tie-breakers. Mood drops slightly from 0.25 to 0.20 since valence now covers part of its signal for songs where mood labels don't match.
