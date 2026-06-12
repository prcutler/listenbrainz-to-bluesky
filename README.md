# listenbrainz-to-bluesky

Automatically updates your Bluesky profile bio with your most recent [ListenBrainz](https://listenbrainz.org) scrobble, run on a schedule via cron on your own server.

Your bio will get a line appended like:

> 🎵 Listening to: Lateralus by Tool

When the track changes, the line is replaced. Your existing bio text is preserved.

## Inspiration

This project is inspired by [scrobble-blue](https://github.com/willmanduffy/scrobble-blue) by [Will Manduffy](https://github.com/willmanduffy), which does the same thing (plus weekly top-artist posts) using Cloudflare Workers and supports both Last.fm and ListenBrainz. This project is a simpler, self-hosted version focused solely on ListenBrainz bio updates.

## Requirements

- A [ListenBrainz](https://listenbrainz.org) account with scrobbling enabled
- A [Bluesky](https://bsky.app) account
- A server or machine that can run a cron job (Linux, macOS, Raspberry Pi, etc.)
- Python 3.10+

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/listenbrainz-to-bluesky.git
cd listenbrainz-to-bluesky
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create a Bluesky app password

In Bluesky, go to **Settings → App Passwords** and create a new password. Do not use your main account password.

### 4. Configure credentials

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```
LISTENBRAINZ_USERNAME=your_listenbrainz_username
BLUESKY_HANDLE=yourname.bsky.social
BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### 5. Test the script

```bash
source venv/bin/activate
python update_bio.py
```

### 6. Set up the cron job

Run `crontab -e` and add:

```
2,7,12,17,22,27,32,37,42,47,52,57 6-21 * * * /path/to/venv/bin/python /path/to/listenbrainz-to-bluesky/update_bio.py >> /path/to/listenbrainz-to-bluesky/update_bio.log 2>&1
```

Replace `/path/to/` with the actual path on your server. This runs every 5 minutes between 6am and 10pm in your server's local time.

If your server runs in UTC and you want the quiet hours to match CST (UTC-6), use this instead:

```
2,7,12,17,22,27,32,37,42,47,52,57 0-3,12-23 * * * /path/to/venv/bin/python /path/to/listenbrainz-to-bluesky/update_bio.py >> /path/to/listenbrainz-to-bluesky/update_bio.log 2>&1
```

## How it works

1. Fetches your most recent listen from the ListenBrainz public API (no token required for reads)
2. Authenticates to Bluesky using the AT Protocol XRPC API
3. Retrieves your current profile record
4. Strips any previous `🎵 Listening to:` section and appends the new track
5. Skips the write if the track hasn't changed since the last run
6. Truncates the track info if needed to stay within Bluesky's 256-character bio limit

Output is logged with timestamps, making it easy to review with `tail -f update_bio.log`.

## License

MIT — see [LICENSE](LICENSE).

## Misc.

Made with Claude. (I know, I know)
