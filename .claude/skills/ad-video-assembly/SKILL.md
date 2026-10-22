---
name: "ad-video-assembly"
description: "When the user wants an actual video ad/reel ASSEMBLED (not just scripted) from real photos and videos they own or upload — raw brand footage, product photos, Instagram exports. Use when they say 'monta um vídeo com essas fotos/vídeos', 'cria um anúncio em vídeo usando esse material', 'edita um reel pra mim', or upload a batch of brand media and ask for a creative/ad out of it. Distinct from video-content-strategist (planning/scripts, no file) and ad-creative (copy only, no rendered file). This skill produces a real .mp4 file via ffmpeg."
license: MIT
metadata:
  version: 1.0.0
  category: marketing
  updated: 2026-10-22
---

# Ad Video Assembly

> **Not the same tool as `videos/_kit/`** in this repo. That kit templates a fixed 18s hook-A/hook-B ad from a handful of client photos plus synthetic TTS narration and stock music — use it when the client has few real assets and no usable footage/voice of their own. Use *this* skill instead when the client dumps real raw material (an Instagram export, a folder of phone photos and Reels, a founder interview) and the job is to cut an authentic piece out of what already exists — real video, real narration, real captions to work around.

Methodology for turning a brand's raw, unglamorous asset dump (phone photos, Instagram video exports, random Reels) into an actual rendered ad/reel — not a plan, not a shot list, a finished `.mp4`. Built from a real job: a clothing brand sent ~25 photos and ~9 videos with zero curation, and the task was to cut a sellable 40-50s vertical ad out of it using ffmpeg in a sandboxed cloud session (no browser, no GPU editor, no Premiere).

## 0. Getting the raw material

If the brand's content lives on Instagram/a website and you have no browser/computer-use tool in this session: say so plainly (don't pretend to browse), and ask the person to paste photos/videos directly into the chat. Large video files that won't paste can still arrive as `@/path/to/file.mp4` attachments — check `ls` on the upload path before assuming you can't reach them.

**Never skip watching a video because it's a video.** A video the model hasn't actually seen is not usable material — don't write descriptions from the filename or from what a similar video "probably" shows.
- `ffprobe -show_entries format=duration -show_entries stream=width,height,codec_type` every file first — know duration/orientation before anything else.
- Extract 4–10 frames evenly spaced (`ffmpeg -ss <t> -frames:v 1`) and actually read them as images. For a long documentary/interview-style file (anything over ~60s), sample more densely — the good material (founder story, a real cultural event, a craft process) is usually buried in the middle, not the first 5 seconds.
- If the video has burned-in captions, read a few of them — they're free transcript and tell you the narration's actual content and emotional arc, which matters later for the audio decision.
- Catalog everything before cutting anything: what it shows, which product line, which aesthetic (editorial fashion / street / product-reveal motion graphic / documentary), usable duration, anything baked into the frame (text, logos, captions).

## 1. Design the arc before touching ffmpeg

The failure mode is a catalog dump — every product, in order, with no story. The arc that actually sells to a brand owner:

1. **Pertencimento / Place** — establish the brand is *from* somewhere real (a landmark, a street, a door), not a generic studio void.
2. **Processo / Craft** — the making-of: hands drawing, a screen with the brand name, pottery, anything that proves authorship instead of dropshipping.
3. **Produto como resultado** — the actual clothing, as the *consequence* of the place and the craft, not a cold catalog. This is the section to weight more heavily when the brief asks for "more product."
4. **CTA** — whatever the brand already has ready-made (a site-launch card, a logo card) beats anything you'd generate from scratch; look for it in the footage before building a title card.

Favor the clip that is *proof*, not just pretty: a brand physically marching in a real cultural festival with its own flag/banner beats any stock-feeling lifestyle shot, every time. Mix real video clips with Ken Burns (slow zoom) on static product photos — you will not have enough usable video alone to cover every beat.

## 2. Verify cut points with real frames, not memory

Before trimming a clip, extract a verification frame at the *exact* candidate timestamp and look at it. Source videos frequently contain quick internal cuts (a 3s window you think is "the pottery shot" may be pottery for 2s then cut to something else entirely) — a frame grabbed 10s earlier during cataloging is not proof of what's at the precise in/out point you're about to use. This step has caught real errors (a "Forte" establishing shot that was actually the CTA card one second away; a caption whose band didn't line up with where a crop was aimed).

## 3. ffmpeg pipeline

**Normalize every segment to one common spec before concatenating** (concat demuxer requires matching params):
```
scale=<W>:<H>:force_original_aspect_ratio=increase,crop=<W>:<H>,fps=30,format=yuv420p,setsar=1
```
Strip audio from every video segment (`-an`) — audio is handled once, separately, over the whole timeline.

**Ken Burns on a static photo** — pre-scale to ~2x the target resolution, then zoompan down; zoompan on a 1x-scaled image looks jittery:
```
scale=<2W>:<2H>:force_original_aspect_ratio=increase,crop=<2W>:<2H>,
zoompan=z='min(zoom+0.0012,1.2)':d=<fps*dur>:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=<W>x<H>:fps=30,
format=yuv420p,setsar=1
```

**Concatenate**: write a `list.txt` of `file 'segNN.mp4'` lines, same folder, then `ffmpeg -f concat -safe 0 -i list.txt -c:v copy`.

**Audio bed — the part most likely to go wrong:**
- You're allowed to lift the narration/music from one source video and lay it under a completely different visual cut — that's normal for this kind of remix.
- **Never hard-truncate spoken narration mid-sentence.** A VO cut at an arbitrary target duration (e.g. "I need exactly 40s") reads as broken, not intentional. Find the narration's own natural resolution point instead:
  - `silencedetect` often fails outright when there's a continuous music bed masking the gaps between phrases — don't trust a null result as "no pauses exist."
  - Burned-in captions are the reliable fallback: sample the caption band densely across the tail of the audio, read the actual sentence, and find where it *grammatically* ends (a period, an exclamation, a resolved clause) rather than guessing. The real ending is sometimes dramatically better material than whatever arbitrary point you'd have cut at — the a poetic list-closing line is far stronger than a truncated fragment.
  - If the natural ending runs longer than the original target length, extend the edit to meet it rather than mutilating the audio to hit a number. A 50s ad that resolves cleanly beats a 40s ad that cuts off mid-word.
- **Burned-in captions from the source become a liability once audio is decoupled/reordered.** A caption timed to the *original* video's narration will contradict whatever is playing at that point in the *new* edit. Fix options, in order of preference: (a) pick a different in/out window of the same shot with no caption active, (b) crop/reframe to exclude the caption band while preserving the subject — verify the crop band's exact pixel range by sampling a caption frame first (`crop=iw:<band_h>:0:<band_y>`) before committing, and re-verify after the fix (a shallow crop can leave a caption fragment visible at the very edge). Don't leave a mismatched caption in and hope it reads as "stylistic."

**Mux**: `ffmpeg -i video_silent.mp4 -i audio_bed.m4a -c:v copy -c:a aac -shortest`.

## 4. On-screen text readability budget

Any segment whose job is to be *read* (a tee's printed slogan, a CTA card, a product-reveal wordmark) needs real dwell time:
- Short punchy phrase (2-4 words, large type): ~3–3.5s minimum.
- Multi-line paragraph-style text on a product (worn, smaller): ~4s.
- A CTA with a URL the viewer needs to actually register: ~5s+, don't undercut this to save runtime elsewhere.
- Compensate by trimming segments that carry *no* text-reading demand (b-roll, lifestyle shots) rather than shrinking every segment proportionally — the viewer doesn't need 3.5s to parse a building facade.

## 5. Post-build sanity pass — always

Before delivering, extract frames at each segment's approximate midpoint across the *final* concatenated file (not the source clips) and look at them. This is the only reliable way to catch: a caption that's still partially visible after a "fix," a segment that landed in the wrong order, a crop that cut off the subject, or a duration miscalculation. Confirming against the source clips in isolation is not the same as confirming against the actual rendered output.

## 6. Delivery and honesty

- Default to vertical 9:16 (e.g. 720×1280) for Reels/Stories unless told otherwise.
- Say plainly what's still a draft vs. ready-to-publish: cross-source color consistency, a persistent logo bug, a spoken (not just text) CTA are common gaps worth naming rather than overclaiming polish.
- When the person gives corrective feedback, it's almost always specific and small (one scene's crop, one segment's duration) — fix exactly that with the same verification discipline (re-extract, re-check) rather than re-deriving the whole edit from scratch.
