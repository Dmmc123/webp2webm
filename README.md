# webp2webm

I don't know why it's such a pain to do bulk conversion of `.webp` emotes into `.webm` format. Most scripts I found either (1) didn't preserve the animation effects or (2) didn't preserve the transparent background or (3) didn't even try to save relative speed of animation. And most online solutions require money for batch conversion.

Sigh.

I guess, we're building our own conversion tool then.

## Usage

1. Prepare a new `venv` in any way you like. Let's assume you have a `pyenv` virtual environment named `3.12.2`
2. Attach the new env poetry using `poetry env use 3.12.2`
3. Install the dependencies with `poetry install`
4. Get some of `.webp` emotes from [7tv](https://7tv.app/) (this is where I get them) and put them in a folder named `twitch`
5. `python webp2webm/cli.py --webp-dir twitch --webm-dir webm` go brr
6. Вы великолепны

**Note**: use `python webp2webm/cli.py --help` to get description of parameters, you might wanna tune the conversion process to your needs if you're not doing it for creating a video emote pack in Telegram

## How it works

Pretty simple: 
1. Split `.webp` into fix-sized transparent frames using `Pillow` and derive the FPS of an emote
2. Merge `.png` frames into `.webp` using `ffpmeg` with recommended settings from [Telegram Guideline](https://core.telegram.org/stickers#video-requirements) while doing our best to maintain the original speed
