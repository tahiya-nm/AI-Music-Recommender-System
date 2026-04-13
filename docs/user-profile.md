# User Taste Profile

The taste profile is a dictionary that captures the user's listening preferences. It is passed directly to the recommender and compared against each song's features using the scoring formula defined in [feature-selection.md](feature-selection.md).

## Profile Dictionary

```python
user_prefs = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.8,
    "target_valence": 0.8,
    "likes_acoustic": False,
}
```

## Key Reference

| Key | Type | Value | Rationale |
|---|---|---|---|
| `favorite_genre` | str | `"pop"` | Highest-weight feature (0.35). Genre match is binary — the recommender scores 1 if the song's genre matches, 0 otherwise. |
| `favorite_mood` | str | `"happy"` | Second weight (0.20). Mood match is binary. "happy" is one of the 6 valid moods in the dataset. |
| `target_energy` | float | `0.8` | Third weight (0.25). Scored as `1 - abs(song.energy - target_energy)`. Must be within the dataset range of 0.28–0.93. |
| `target_valence` | float | `0.8` | Fourth weight (0.10). Scored as `1 - abs(song.valence - target_valence)`. Breaks ties in the mid-energy cluster where genre/mood are both 0. Set to 0.8 to align with happy mood (high valence). |
| `likes_acoustic` | bool | `False` | Tie-breaker weight (0.10). `False` means the recommender favors low-acousticness songs, scoring them as `1 - song.acousticness`. |

## Mapping to Code

These keys map 1:1 to the `UserProfile` dataclass fields in [src/recommender.py](../src/recommender.py):

```
user_prefs["favorite_genre"]  →  UserProfile.favorite_genre
user_prefs["favorite_mood"]   →  UserProfile.favorite_mood
user_prefs["target_energy"]   →  UserProfile.target_energy
user_prefs["target_valence"]  →  UserProfile.target_valence
user_prefs["likes_acoustic"]  →  UserProfile.likes_acoustic
```

They also correspond to columns in `data/songs.csv`: `genre`, `mood`, `energy`, `valence`, and `acousticness`.
