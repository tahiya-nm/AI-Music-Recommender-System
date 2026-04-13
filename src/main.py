"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs

# Column widths for the results table
_W = {"rank": 2, "title": 24, "artist": 14, "genre": 9, "mood": 11, "energy": 6, "score": 5}
_LINE_WIDTH = sum(_W.values()) + len(_W) * 3 + 1  # padding + separators


def _table_row(rank, title, artist, genre, mood, energy, score) -> str:
    """Format one song row with fixed-width columns."""
    cells = [
        str(rank).rjust(_W["rank"]),
        str(title)[: _W["title"]].ljust(_W["title"]),
        str(artist)[: _W["artist"]].ljust(_W["artist"]),
        str(genre)[: _W["genre"]].ljust(_W["genre"]),
        str(mood)[: _W["mood"]].ljust(_W["mood"]),
        f"{energy:.2f}".rjust(_W["energy"]),
        f"{score:.2f}".rjust(_W["score"]),
    ]
    return "| " + " | ".join(cells) + " |"


def _table_header() -> str:
    labels = ["#", "Title", "Artist", "Genre", "Mood", "Energy", "Score"]
    keys = list(_W.keys())
    cells = [lbl.ljust(_W[k]) if lbl != "#" else lbl.rjust(_W[k]) for lbl, k in zip(labels, keys)]
    return "| " + " | ".join(cells) + " |"


def _separator(char: str = "-") -> str:
    return "+" + "+".join(char * (_W[k] + 2) for k in _W) + "+"


def run_profile(profile_name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=k)

    # Profile banner
    prefs_str = f"genre={user_prefs['genre']}  |  mood={user_prefs['mood']}  |  energy={user_prefs['energy']}"
    banner_width = max(_LINE_WIDTH, len(profile_name) + 4, len(prefs_str) + 4)
    print("\n" + "=" * banner_width)
    print(f"  {profile_name}")
    print(f"  {prefs_str}")
    print("=" * banner_width)

    # Table header
    print(_separator("="))
    print(_table_header())
    print(_separator("="))

    for rank, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        reasons = [r.strip() for r in explanation.split(",")]

        # Song row
        print(_table_row(
            rank,
            song["title"],
            song["artist"],
            song["genre"],
            song["mood"],
            song["energy"],
            score,
        ))

        # Reasons sub-row — indented under the title column
        indent = " " * (_W["rank"] + 3)  # align with title column start
        reasons_str = "  •  ".join(reasons)
        print(f"|{indent}Reasons: {reasons_str}")
        print(_separator())

    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")

    # ------------------------------------------------------------------ #
    #  STANDARD PROFILES                                                   #
    # ------------------------------------------------------------------ #

    # Genre=pop, Mood=happy, Energy=0.85 → ideal match: "Sunrise City"
    high_energy_pop = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
    }

    # Genre=lofi, Mood=chill, Energy=0.38 → ideal matches: "Library Rain", "Midnight Coding"
    chill_lofi = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
    }

    # Genre=rock, Mood=intense, Energy=0.92 → ideal match: "Storm Runner"
    deep_intense_rock = {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
    }

    # ------------------------------------------------------------------ #
    #  ADVERSARIAL / EDGE-CASE PROFILES                                   #
    # ------------------------------------------------------------------ #

    # EDGE 1 — Contradictory mood vs. energy
    # energy=0.95 signals "I want high-intensity music" but mood="sad" signals
    # the opposite. No song in the catalog is both sad AND high-energy.
    # Scoring will split: genre+mood match a slow sad song while energy bonus
    # pulls toward fast energetic songs that share no other attributes.
    # Expected trap: "Rainy Day Blues" wins on genre+mood alone (score ~3.94)
    # even though its energy (0.34) is far from the requested 0.95.
    conflicting_sad_high_energy = {
        "genre": "blues",
        "mood": "sad",
        "energy": 0.95,
    }

    # EDGE 2 — Genre that does not exist in the catalog ("reggae")
    # Genre match can never fire → max achievable score is 2.5
    # (mood +1.5 + perfect energy +1.0). The recommender silently falls back
    # to mood+energy ranking, which may feel "off" to the user who wanted reggae.
    unknown_genre = {
        "genre": "reggae",
        "mood": "happy",
        "energy": 0.70,
    }

    # EDGE 3 — Energy at the exact midpoint (0.5)
    # energy proximity = 1 - |song_energy - 0.5|, which tops out at 1.0 only
    # for a song with energy exactly 0.5. No such song exists in the catalog,
    # so the energy bonus is uniformly suppressed for every song. Genre and
    # mood dominate even more than usual; two songs with the same genre+mood
    # but very different energies will score almost identically.
    energy_midpoint_edm = {
        "genre": "edm",
        "mood": "euphoric",
        "energy": 0.50,
    }

    # EDGE 4 — Mood that never appears in the catalog ("aggressive" in lofi)
    # genre="lofi" can match, but mood="aggressive" matches nothing, so the
    # +1.5 mood bonus is permanently locked out. Every lofi song scores the
    # same genre bonus; only energy separates them.
    impossible_mood_combo = {
        "genre": "lofi",
        "mood": "aggressive",
        "energy": 0.40,
    }

    # EDGE 5 — Boundary energy values (0.0 and 1.0 tested back-to-back)
    # energy=1.0 makes the energy term equal to (1 - |song_energy - 1|) = song_energy.
    # Extremely quiet songs are penalised most; extremely loud songs are rewarded.
    # Scores for genre/mood non-matches can creep above scores for genre matches
    # if the non-match song happens to be louder.
    max_energy_metal = {
        "genre": "metal",
        "mood": "aggressive",
        "energy": 1.0,
    }

    # ------------------------------------------------------------------ #
    #  RUN ALL PROFILES                                                    #
    # ------------------------------------------------------------------ #

    standard_profiles = [
        ("High-Energy Pop",   high_energy_pop),
        ("Chill Lofi",        chill_lofi),
        ("Deep Intense Rock", deep_intense_rock),
    ]

    adversarial_profiles = [
        ("ADVERSARIAL — Sad + High Energy (blues)",    conflicting_sad_high_energy),
        ("ADVERSARIAL — Unknown Genre (reggae)",       unknown_genre),
        ("ADVERSARIAL — Energy Midpoint (edm)",        energy_midpoint_edm),
        ("ADVERSARIAL — Impossible Mood Combo (lofi)", impossible_mood_combo),
        ("ADVERSARIAL — Max Energy Boundary (metal)",  max_energy_metal),
    ]

    print("### STANDARD PROFILES ###")
    for name, prefs in standard_profiles:
        run_profile(name, prefs, songs)

    print("\n### ADVERSARIAL PROFILES ###")
    for name, prefs in adversarial_profiles:
        run_profile(name, prefs, songs)


if __name__ == "__main__":
    main()
