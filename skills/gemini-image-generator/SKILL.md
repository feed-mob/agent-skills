---
name: gemini-image-generator
description: Generate images with Gemini Nano Banana using the bundled Python script (gemini-2.5-flash-image or gemini-3-pro-image-preview), including aspect ratio and resolution handling. Use when users request image generation, image variations, or specific aspect ratios or resolutions.
---

# Gemini Image Generator

Use this skill to turn a user prompt into a Gemini image generation call via the bundled Python script.

## Workflow

1. Collect the user prompt only.
2. Infer optional parameters and translate them into CLI flags.
3. Run the script to generate images.
4. Return the output file paths.

## Defaults and Rules

- Default model: `gemini-2.5-flash-image` (CLI value `flash`).
- Default aspect ratio: `9:16`.
- Default count: `1` (max `3`).
- Default image size: `1K`, but only apply it for the Pro model.
- If the user specifies a size (`1K|2K|4K`), switch to Pro (`gemini-3-pro-image-preview`).
- If the user explicitly asks for Pro or higher quality, use Pro.
- Only set `--size` when using Pro.

## Allowed Values

- Aspect ratios: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`.
- Image sizes (Pro only): `1K`, `2K`, `4K`.

## Script

Run:

```bash
python scripts/generate_image.py \
  --prompt "<user prompt>" \
  --aspect 9:16 \
  --count 1 \
  --model flash \
  --out-dir outputs
```

Only add flags when the user asks for them. The script reads `GEMINI_API_KEY` from the environment.

## Examples

User: "Generate a portrait of a dancer in a foggy forest."
Claude:
- Use defaults (flash, 9:16, count 1).
- Run:
  `python scripts/generate_image.py --prompt "Generate a portrait of a dancer in a foggy forest."`

User: "Make a 2K 16:9 cinematic still of a neon city, give me 3 options."
Claude:
- Use Pro with size 2K, aspect 16:9, count 3.
- Run:
  `python scripts/generate_image.py --prompt "Make a 2K 16:9 cinematic still of a neon city" --aspect 16:9 --size 2K --count 3 --model pro`

## Notes

- If the script fails with a missing module, install `google-genai` and retry.
- Output files are written into the `outputs/` directory using timestamped names.
