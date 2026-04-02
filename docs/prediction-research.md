# How Streaming Platforms Predict What You'll Love Next

A research summary of recommendation system techniques used by major music streaming platforms — Spotify, YouTube Music, Apple Music, and Pandora.

---

## Table of Contents

1. [Overview](#overview)
2. [Collaborative Filtering](#1-collaborative-filtering)
3. [Content-Based Filtering](#2-content-based-filtering)
4. [Hybrid Approaches](#3-hybrid-approaches)
5. [Behavioral Data Types](#4-behavioral-data-types)
6. [Audio and Content Data Types](#5-audio-and-content-data-types)
7. [Platform-Specific Approaches](#6-platform-specific-approaches)
8. [The Cold-Start Problem](#7-the-cold-start-problem)
9. [Summary: Data Types at a Glance](#8-summary-data-types-at-a-glance)

---

## Overview

Major streaming platforms use **hybrid recommendation systems** that combine multiple techniques:

- **Collaborative filtering** — learns from patterns across many users' behavior
- **Content-based filtering** — analyzes audio and metadata attributes of individual songs
- **Contextual signals** — time of day, device type, session activity
- **Human curation** — expert editors and musicologists who guide or supplement algorithms

No single technique is sufficient on its own. Platforms blend all of these to handle both new users/songs (where behavioral data is scarce) and established listeners (where rich history is available).

---

## 1. Collaborative Filtering

Collaborative filtering predicts what a user will like based on the collective behavior of many users. The core assumption is: **users with similar tastes in the past will continue to like similar things**.

### How It Works

There are two main variants:

**User-Based (User-User)**
- Finds other users with taste profiles similar to yours
- Recommends songs those users liked that you haven't heard yet
- Example: If you and User B have 90% song overlap, songs B loves that you haven't played get surfaced to you

**Item-Based (Item-Item)**
- Finds songs that tend to be liked together by the same users
- Pre-computes a song-to-song similarity matrix from co-occurrence data
- Example: Because many users added Song A and Song B to the same playlists, they're treated as related items

### Matrix Factorization

Instead of computing raw similarity across billions of user-item pairs, modern systems use **matrix factorization** — decomposing the user-item interaction matrix into two lower-dimensional matrices (a user matrix and an item matrix). This lets the system represent both users and songs as vectors of **latent factors** (implicit concepts like "melancholic indie" or "high-energy dance") without ever explicitly labeling them.

**Bayesian Personalized Ranking (BPR)** is a related technique that frames recommendation as a ranking problem: given that a user interacted with Song A but not Song B, train the model so that Song A scores higher. This works especially well with **implicit feedback** (plays, skips, saves) rather than explicit star ratings.

### Strengths

- Discovers non-obvious connections between users and items
- Improves with scale — more users means better patterns
- Effective for serendipitous recommendations (music the user wouldn't have searched for)

### Weaknesses

- **Cold-start problem for new users**: No history means no collaborative signal
- **Cold-start problem for new songs**: A newly released track with zero plays can't be matched to user clusters
- **Sparsity**: The user-item interaction matrix (billions of users × millions of songs) is extremely sparse
- Not interpretable — it's hard to explain *why* a specific song was recommended

---

## 2. Content-Based Filtering

Content-based filtering recommends songs by analyzing the song's own attributes and finding other songs with similar characteristics to what the user already enjoys.

### How It Works

1. Extract a feature vector for every song in the catalog (audio features + metadata)
2. Build a profile of the user's preferences based on features of songs they've liked
3. Compute similarity (typically cosine similarity) between the user's preference profile and all other songs
4. Recommend the most similar songs

### Audio Feature Extraction via CNNs

Beyond hand-crafted features, modern systems use **Convolutional Neural Networks (CNNs)** on raw audio:

1. Audio waveforms are converted to **mel-spectrograms** (frequency-time visual representations tuned to human hearing)
2. CNNs scan these spectrograms with learnable filters to extract hierarchical patterns
3. The output is a rich feature embedding that captures rhythm, texture, timbre, and structure

Spotify has publicly described using this approach to generate audio embeddings for every song in its catalog.

### Strengths

- Solves item cold-start: new songs can be analyzed immediately upon upload
- Interpretable: recommendations can be explained through specific features ("similar tempo and mood to what you like")
- Works without any user history — useful at onboarding

### Weaknesses

- Tends toward **filter bubble** effects — keeps recommending similar things without diversifying
- Hard to capture subjective attributes like emotional resonance or cultural context
- Lyrics and narrative meaning are difficult to encode purely from audio

---

## 3. Hybrid Approaches

All major platforms combine both techniques, typically following this pattern:

1. **Cold-start phase**: Use content-based filtering for new users or new songs
2. **Established phase**: Layer in collaborative filtering as interaction data accumulates
3. **Final scoring**: Blend collaborative signals, content signals, contextual signals, and behavioral feedback into a single ranked list

**Example recommendation flow:**
- A user builds a "Late Night Study" playlist with low energy, high acousticness, and low valence songs
- A similar user with 85% taste overlap hasn't heard Track X yet
- Track X's audio features match the study playlist profile (low energy, high acousticness)
- **Collaborative signal** says: "Users like you liked Track X"
- **Content signal** says: "Track X fits the mood profile of your listening pattern"
- Track X gets recommended with high confidence

### Advanced Techniques in Use

| Technique | Description |
|-----------|-------------|
| **Graph Neural Networks (GNNs)** | Model users, songs, and interactions as a graph; learn from structure and features together |
| **Transformer models** | Process user action sequences; weight recent session context more heavily (used by YouTube Music) |
| **Reinforcement Learning / Bandits** | Optimize the balance between discovery and familiarity per session based on user feedback |

---

## 4. Behavioral Data Types

These are **implicit feedback signals** — what users do, not what they explicitly rate. They are more abundant and often more informative than explicit ratings.

### Signals and What They Mean

| Signal | What It Captures | Notes |
|--------|-----------------|-------|
| **Skip** | Strong dissatisfaction with the current song in context | Early skips (< 30 seconds) are especially negative signals |
| **Completion / listening duration** | Preference — playing to completion signals approval | Partial listening (30–60 seconds) is neutral |
| **Replay / repeat play** | Strong positive preference | Multiple plays in a short window indicate high impact |
| **Like / Save** | Explicit positive signal | More intentional than a passive play |
| **Playlist add** | Contextual affinity — user sees the song fitting a specific mood or activity | Stronger signal than a simple play |
| **Search query** | Active intent — user is consciously seeking something | Reveals emerging interests |
| **Time of day** | Contextual signal for mood and activity | Morning → energetic; night → introspective |
| **Device type** | Infers activity context | Phone → mobile/casual; speaker → leisure/party |
| **Session sequence** | The order of recent actions within a listening session | Transformers use this to infer current intent |

Spotify is known to train on approximately **700 million user-generated playlists**, using playlist co-occurrence (which songs users place together) as the primary collaborative filtering signal, rather than raw play counts.

---

## 5. Audio and Content Data Types

These are features derived from the song itself, independent of user behavior.

### Numeric Audio Features (Spotify API scale: 0.0–1.0 unless noted)

| Feature | Description | Example Use |
|---------|-------------|-------------|
| **Tempo (BPM)** | Speed of the track in beats per minute | Match energy levels; workout vs. relaxation contexts |
| **Energy** | Perceptual intensity and activity (0.0–1.0) | High energy → fast/loud/noisy; low energy → calm/quiet |
| **Valence (Mood)** | Musical positiveness (0.0–1.0) | High → happy/euphoric; low → sad/melancholic/dark |
| **Danceability** | Suitability for dancing based on rhythm stability and beat strength | Workout playlists, party mixes |
| **Acousticness** | Confidence that the track is acoustic (0.0–1.0) | Cluster acoustic vs. produced tracks |
| **Loudness** | Average loudness in decibels (dB) | Listening context and dynamic range |
| **Instrumentalness** | Absence of vocals (0.0–1.0) | Focus playlists, background music |
| **Liveness** | Presence of audience/concert atmosphere | Distinguish studio recordings from live versions |
| **Speechiness** | Presence of spoken word | Distinguish podcasts from music, identify rap |
| **Key / Mode** | Musical key (C, D, F#, etc.) and major/minor mode | Harmonic compatibility; mixing and DJ contexts |

### Metadata and Categorical Features

| Feature | Description |
|---------|-------------|
| **Genre tags** | Top-level genre classification (pop, hip-hop, jazz, etc.) |
| **Subgenre / style tags** | More granular stylistic labels (lo-fi hip-hop, bedroom pop, math rock) |
| **Artist similarity** | Pre-computed artist-to-artist relationships, often from NLP on music descriptions |
| **Release year / era** | Temporal context; users often have era preferences |
| **Language** | Spoken/sung language of the track |

### NLP and Lyrical Features

| Feature | Description |
|---------|-------------|
| **Lyric embeddings** | TF-IDF or Word2Vec representations of song lyrics; enables thematic similarity |
| **Lyrical theme** | Heartbreak, nostalgia, celebration, protest, etc. |
| **Playlist title/description NLP** | Titles like "3am Melancholy" or "Morning Run" are parsed to infer song relationships |
| **Artist bios and reviews** | Named entities and descriptions used to cluster stylistically related artists |

---

## 6. Platform-Specific Approaches

### Spotify

- **Primary collaborative signal**: Playlist co-occurrence across ~700 million user playlists
- **Content signal**: CNNs on raw audio waveforms to produce song embeddings; also uses matrix factorization with latent factors
- **NLP**: Processes playlist titles and descriptions to identify contextual patterns
- **Reinforcement Learning**: Uses neural contextual bandits to tune the discovery/familiarity balance per session
- **Key products**: Discover Weekly (weekly CF-driven mixtape), Release Radar (new releases matched to taste)

### YouTube Music

- **Session-based**: Transformer models process recent action sequences within a session to infer current intent
- **Long-term preferences**: Historical YouTube and YouTube Music watch history (months/years)
- **Cross-platform integration**: Regular YouTube watch history informs music recommendations (cooking videos → cooking-themed playlists)
- **Unique advantage**: Session context diversity — the same user might receive very different recommendations in different sessions based on what they just watched

### Apple Music

- **Collaborative filtering**: Identifies favorite artists, then finds related artists others also like
- **Content-based**: Proprietary audio analysis and feature extraction (not publicly documented)
- **Heavy human curation**: Expert editors manually tag songs (e.g., "perfect for running", "bedroom pop essentials") and this editorial context is weighted alongside algorithmic signals
- **Neural embeddings**: Maps songs and users to high-dimensional space where proximity equals similarity

### Pandora — The Music Genome Project

- **Unique approach**: A team of trained musicologists analyzes every song across ~450 "genes" (musical attributes), spending 20–30 minutes per track
- **Genes include**: Vocalist gender and timbre, groove and rhythm, guitar distortion level, background vocal style, harmonic structure, lyrical themes, cultural era
- **Hybrid**: Combines the Music Genome Project's content analysis with collaborative filtering across millions of users
- **Explicit feedback loop**: Thumbs up/down directly refines station behavior in real time
- **Strength**: High interpretability and cold-start resilience for new items (musicologists analyze on release)
- **Limitation**: Labor-intensive; slower to scale than fully algorithmic approaches

---

## 7. The Cold-Start Problem

The cold-start problem occurs when the system lacks sufficient data to make good recommendations — for new users or new songs.

### Two Types

| Type | Problem | Common Solutions |
|------|---------|-----------------|
| **User cold-start** | New user with no listening history | Onboarding questionnaire; demographic profiling; popular/trending recommendations |
| **Item cold-start** | New song with few/no interactions | Content-based filtering using audio features; human curation to manually promote new releases |

### How Platforms Address It

1. **Content features for new items**: Audio CNNs and feature extraction work immediately on upload; new songs get matched to users with compatible taste profiles
2. **Onboarding questions**: Ask new users for favorite artists/genres to bootstrap a preference vector
3. **Human curation**: Spotify and Apple Music use expert editors to identify promising new artists before the algorithm can; Pandora uses musicologists to analyze songs immediately
4. **Gradual hybrid transition**: Start with content-based recommendations; shift to collaborative filtering as interaction history grows

---

## 8. Summary: Data Types at a Glance

### Behavioral Signals
`likes` · `skips` · `replays` · `playlist adds` · `listening duration` · `search queries` · `time of day` · `device type` · `session sequence`

### Audio Features
`tempo (BPM)` · `energy` · `valence/mood` · `danceability` · `acousticness` · `loudness` · `instrumentalness` · `liveness` · `speechiness` · `key/mode`

### Content & Metadata
`genre` · `subgenre` · `artist similarity` · `release year` · `language` · `lyric embeddings` · `lyrical themes` · `playlist title NLP`

### Platform Data at Scale
| Platform | Primary Scale Signal |
|----------|---------------------|
| Spotify | 700M+ user playlists; 700M+ active users |
| YouTube Music | Billions of YouTube watch history events |
| Apple Music | Cross-device listening history |
| Pandora | 450 musicologist-analyzed genes per song |

---

*Research compiled April 2026. Covers Spotify, YouTube Music, Apple Music, and Pandora recommendation architectures.*
