# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**MoodMatch 1.0** — a rule-based music recommender that scores songs by how closely they match a user's genre, mood, and energy preferences.

---

## 2. Intended Use  

- Suggests songs from a fixed catalog based on three stated preferences: genre, mood, and energy level
- Assumes the user already knows what they want and can express it as a genre + mood + energy number
- Built for classroom exploration — not a production app
- Not intended to learn from listening history or adapt over time

**Not intended for:**
- Personalization based on past behavior
- Discovering music outside the 18-song catalog
- Any deployment to real users or commercial use

---

## 3. How the Model Works  

Every song in the catalog gets a score based on how well it matches what the user asked for. Higher score = better match = higher ranking.

**Scoring rules (three signals):**

- **Genre match (+2.0 points):** If the song's genre equals the user's preferred genre, it gets a flat 2-point bonus. Either it matches or it doesn't — no partial credit.
- **Energy proximity (0 to +1.0 points):** Songs closer in energy level to the user's target score higher. A perfect energy match gives +1.0; a song on the opposite end of the scale gives close to 0.
- **Mood match (+1.5 points, currently disabled in code):** Originally gave bonus points when the song's mood matched the user's. Turned off during an experiment and not yet restored.

The scores from all active signals are added up. The top 5 highest-scoring songs are returned as recommendations.

**What the model ignores (even though the data has it):** tempo, danceability, valence (positivity), and acousticness — these are loaded but not used in scoring.

---

## 4. Data  

- **18 songs** total, all manually created for this project (not pulled from a real music API)
- **14 genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, classical, r&b, folk, edm, metal, blues, country
- **Most genres have only 1 song** — lofi is the exception with 3 (Library Rain, Midnight Coding, Focus Flow)
- **Moods in the catalog:** happy, chill, intense, focused, euphoric, aggressive, relaxed, moody, energetic, melancholic, romantic, nostalgic, heartfelt, sad
- **Energy range:** 0.22 (Moonlight Sonata Redux) to 0.98 (Iron Cathedral) — skews toward extremes, very few songs in the 0.45–0.65 middle range

**What's missing:**
- No reggae, Latin, gospel, or K-pop genres — requests for those silently fail
- No songs with energy near 0.5, so "moderate energy" users are under-served
- Dataset is too small to surface meaningful diversity in results — genres with 1 song always hit a ceiling after position 1

---

## 5. Strengths  

- **Works well when genre and energy align:** High-Energy Pop and Deep Intense Rock profiles both returned obvious, correct top results (Sunrise City, Storm Runner) because the genre bonus + energy signal pointed at the same song
- **Lofi catalog is deep enough to rank meaningfully:** With 3 lofi songs, the Chill Lofi profile produced a genuinely ordered list where small energy differences separated the results — not just a random tie
- **Adversarial cases still return something:** Even when the genre doesn't exist (reggae) or the mood is impossible (aggressive lofi), the system returns 5 songs rather than crashing or returning nothing
- **Genre penalty is implicit and effective:** Songs outside the user's genre consistently rank below same-genre songs, which matches basic intuition about what people want

---

## 6. Limitations and Bias 

**Observed weaknesses from experiments:**

- The genre match gives a flat +2.0 bonus regardless of how close the rest of the song's attributes are, meaning a pop song with the wrong energy, mood, and feel will always outrank a near-perfect non-pop song for a pop user — the system over-rewards genre agreement and cannot compensate with any combination of other signals.
- Users who prefer moderate energy levels (around 0.5) are systematically under-served: the catalog skews toward low (lofi/ambient) and high (edm/metal) energy extremes, so the energy proximity term never gives a midpoint user a strong match, and genre dominates their results by default.
- Four song features — valence, danceability, acousticness, and tempo — are loaded from the dataset but contribute zero to the score, meaning two users with opposite preferences on these dimensions receive identical recommendations as long as their genre and energy are the same.
- When a user requests a genre not present in the catalog (such as reggae), the system silently falls back to energy-only ranking with no notification — the recommendations look plausible but are built on a fundamentally different logic than what the user asked for.
- The mood signal, even when enabled, is a binary all-or-nothing check: a song labeled "relaxed" gets zero credit when the user wants "chill," even though those moods are conceptually adjacent, causing the system to treat near-misses the same as total mismatches.

---

## 7. Evaluation

### Profiles Tested

We tested eight user profiles in total — three "standard" profiles designed to match songs we expected, and five "adversarial" profiles designed to break or stress-test the system.

**Standard profiles:**

| Profile | Genre | Mood | Energy | Expected top result |
|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.85 | Sunrise City |
| Chill Lofi | lofi | chill | 0.38 | Library Rain or Midnight Coding |
| Deep Intense Rock | rock | intense | 0.92 | Storm Runner |

**Adversarial profiles:**

| Profile | What we were testing |
|---|---|
| Sad + High Energy (blues) | Contradictory mood vs. energy — can the system handle a request that no song satisfies? |
| Unknown Genre (reggae) | No reggae in the catalog — does the fallback make any sense? |
| Energy Midpoint (edm) | Energy = 0.50, which no catalog song sits near — does genre still rescue it? |
| Impossible Mood Combo (lofi) | Mood "aggressive" doesn't exist for any lofi song — will the system notice? |
| Max Energy Boundary (metal) | Energy pushed to 1.0 — does this distort rankings for non-metal songs? |

---

### What We Looked For

For each profile we asked: does the top-ranked song match what a real person with these preferences would actually want? We also compared positions 2–5 to see whether the runner-up results were plausible or surprising. When two profiles were similar (e.g., both asking for lofi), we checked whether the outputs were meaningfully different.

---

### What Surprised Us

**1. "Gym Hero" keeps crashing the party.**

Gym Hero (pop, intense, energy=0.93) scored 2.92 for the High-Energy Pop profile — only 0.05 points below #1 Sunrise City (2.97). Because the mood signal is currently disabled, the system cannot tell that Gym Hero is a high-intensity workout track and Sunrise City is a cheerful pop song. For a user who just wants something happy to sing along to, an aggressive gym anthem appearing at #2 is a bad recommendation. The genre match gets it in the door; energy keeps it near the top; and with no mood check, nothing pushes it out.

This same song showed up at #3 for the Max Energy Metal profile. Someone asking for aggressive metal got a pop track at position three — because Gym Hero's energy (0.93) is close to 1.0, and without mood, "intense pop" and "aggressive metal" look nearly identical to the scorer.

**2. The reggae fallback is invisible.**

When the user asked for reggae (which doesn't exist in the catalog), the system returned Night Drive Loop (synthwave) at #1 and Rooftop Lights (indie pop) at #2. These songs have nothing in common with reggae — they just happened to sit near energy=0.70. The system gave no warning and the output looked perfectly reasonable on the surface. A real user would assume those were reggae recommendations and have no way to know the system had quietly given up on the genre entirely.

**3. An EDM fan at medium energy gets a country song at #2.**

The Energy Midpoint EDM profile asked for edm, euphoric, energy=0.50. Signal Drop (the only EDM song) scored 2.54 and landed at #1. But #2 was Porch Light Waiting, a country song with energy=0.55. It scored 0.95 purely because its energy happened to sit closest to the 0.50 target. A person who wanted EDM and got country as their second recommendation would be confused and trust the system less.

**4. The "impossible mood" lofi profile got perfectly reasonable results — accidentally.**

The Impossible Mood Combo profile asked for lofi with an "aggressive" mood (which no lofi song has). Since mood is disabled, the system just ranked lofi songs by energy proximity. Focus Flow came out #1 with a perfect energy match. The results looked sensible, but only because we'd turned off the one signal that would have exposed the problem. If mood were active and scored 0 for every song (no match possible), the lofi genre songs would still win — but the explanation would reveal that the mood was never satisfied.

**5. Chill Lofi's #1 result was a "focused" song, not a "chill" one.**

With mood disabled, Focus Flow (lofi, focused, energy=0.40) scored 2.98 and beat Library Rain (lofi, chill, energy=0.35) which scored 2.97 — a difference of 0.01 points driven entirely by the fact that Focus Flow sits 0.02 closer to the user's target energy of 0.38. A user who wanted something calming and dreamy got a study-music track instead. The difference is real, but the scoring system could not see it.

---

## 8. Experiment Log

### Experiment 1 — Removing the Mood Signal

**What we changed:** The scoring function originally gave a song +1.5 points whenever its mood matched the user's preferred mood. We temporarily disabled that check to see how much the rankings actually depend on it.

**Why:** We wanted to know whether mood was doing real work — or whether genre and energy were already enough to surface good results.

**How scores changed:**

| Feature | Before | After |
|---|---|---|
| Genre match | +2.0 | +2.0 (unchanged) |
| Mood match | +1.5 | disabled |
| Energy proximity | 0.0 – 1.0 | 0.0 – 1.0 (unchanged) |
| **Max possible score** | **4.5** | **3.0** |

**What happened to the recommendations:**

| Test Profile | Before (mood ON) | After (mood OFF) | What it tells us |
|---|---|---|---|
| High-Energy Pop (happy) | Sunrise City #1 — energy + mood both match | Sunrise City still #1 — energy alone was enough | Mood was redundant here |
| Chill Lofi (chill) | Library Rain #2 — chill mood match | Focus Flow #1 — better energy match takes over | Mood was tiebreaking within the genre |
| Sad + High Energy blues | Rainy Day Blues #1 — mood signal helped it hold on | Still #1, but score drops — energetic non-sad songs crowd positions 2–5 | Mood was protecting the result; removing it made this worse |
| Impossible Mood (lofi + aggressive) | No song could match the impossible mood, so all got 0 mood bonus | Focus Flow scores a perfect 3.0 — clean genre + energy result | Removing mood actually improved this case; the impossible request no longer penalizes the user |

**Conclusion:**

Mood is not always necessary; in straightforward cases where genre and energy already agree, its removal barely changed anything. But it matters as a guardrail: when the user's energy preference points toward songs that contradict their mood, the mood signal was the only thing keeping those songs out of the top results. The biggest surprise was the "impossible mood" case: disabling mood made the system *more* sensible there, because it stopped trying to match a mood that didn't exist in the catalog.

**Status:** Reverted. The mood check has been restored to the scoring function. The experiment confirmed mood is worth keeping, though future work could reduce its weight rather than removing it entirely.

---

## 9. Future Work  

- **Re-enable and tune the mood signal:** The +1.5 mood bonus was disabled during an experiment and never restored. Turning it back on (possibly at a lower weight like +0.8) would fix the "Gym Hero problem" where intense songs outrank happy ones for users who asked for happy
- **Add partial genre credit:** Right now genre is all-or-nothing (+2.0 or 0). A softer approach — like giving +1.0 for adjacent genres (e.g., indie pop when someone asks for pop) — would make the fallback results much more sensible
- **Warn the user when their genre or mood has no catalog match:** Instead of silently returning energy-only results, the system should say "no reggae songs found — showing closest matches by energy" so the user knows what happened
- **Use the unused features:** Valence, danceability, acousticness, and tempo are already in the data. Even a small weight on acousticness would separate an acoustic folk song from an electric rock song for users who care about that distinction

---

## 10. Personal Reflection  

**Biggest learning moment**
- Turning the mood signal *off* taught me more than leaving it on. The moment I disabled it, Gym Hero started crashing happy pop lists and Focus Flow beat Library Rain for a chill user by 0.01 points. The failures were invisible until I removed the guardrail — that told me more about what the signal was actually doing than any amount of reading the code would have.

**How AI tools helped — and where I had to double-check**
- Claude helped me articulate *why* the genre bonus dominates before I'd fully worked it out myself: 2.0 vs. a max 1.0 for energy means genre always wins a tie. That framing was immediately useful.
- I had to verify it by actually running the adversarial profiles — the tool was right about the logic, but the real surprise (an EDM user getting a country song at #2) only showed up in the output. AI explained the math; the experiment confirmed whether the math mattered in practice.
- I also caught one case where a suggested weight (mood at +1.5) felt off after testing — the number came from reasoning about relative importance, not from watching what it actually did to rankings. Running it changed my intuition.

**What surprised me about how a simple algorithm can "feel" like recommendations**
- The results looked plausible even when the reasoning was completely broken. The reggae fallback returned synthwave and indie pop with perfectly normal-looking scores — nothing in the output signaled that the system had quietly given up on the genre. That's unsettling: a simple formula can produce confident-looking results that are built on nothing.
- Lofi actually felt like a real recommender. Three songs, small energy differences, and the output produced a sensible ranked list where each position felt earned. It only works because the catalog happens to have enough lofi songs to rank — but within that pocket, the simplicity disappeared.

**What I'd try next**
- Add partial genre credit — give +1.0 for adjacent genres (indie pop when someone asks for pop) so the fallback isn't silent and binary
- Use valence and acousticness in scoring; they're already in the data and would separate songs that currently score identically
- Surface a warning when no catalog song matches the requested genre or mood, instead of returning plausible-looking nonsense
- Try collaborative filtering on a bigger dataset to see at what point the "every flaw is immediately visible" property of a small catalog disappears — and whether that's actually an improvement or just better hiding
