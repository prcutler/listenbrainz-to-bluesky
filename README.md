# listenbrainz-to-bluesky

Automatically updates your Bluesky profile bio with your most recent [ListenBrainz](https://listenbrainz.org) scrobble, run on a schedule via GitHub Actions.

Your bio will get a line appended like:

> 🎵 Listening to: Lateralus by Tool

When the track changes, the line is replaced. Your existing bio text is preserved.

## Inspiration

This project is inspired by [scrobble-blue](https://github.com/willmanduffy/scrobble-blue) by [Will Manduffy](https://github.com/willmanduffy), which does the same thing (plus weekly top-artist posts) using Cloudflare Workers and supports both Last.fm and ListenBrainz. This project is a simpler, Cloudflare-free version focused solely on ListenBrainz bio updates.

## Requirements

- A [ListenBrainz](https://listenbrainz.org) account with scrobbling enabled
- A [Bluesky](https://bsky.app) account
- A GitHub account (to host and schedule the workflow)

## Setup

### 1. Fork or clone this repo

Push it to your own GitHub account. Make the repo **public** if you want to use the free unlimited GitHub Actions minutes tier. Private repos are limited to 2,000 minutes/month, which this workflow will exceed at the default 5-minute interval.

### 2. Create a Bluesky app password

In Bluesky, go to **Settings → App Passwords** and create a new password. Do not use your main account password.

### 3. Add GitHub Actions secrets

In your repo, go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `LISTENBRAINZ_USERNAME` | Your ListenBrainz username |
| `BLUESKY_HANDLE` | Your Bluesky handle, e.g. `yourname.bsky.social` |
| `BLUESKY_APP_PASSWORD` | The app password created in step 2 |

### 4. Enable Actions

GitHub Actions should run automatically once the repo is pushed. You can also trigger a manual run from the **Actions** tab using the **Run workflow** button to test it.

## How it works

The script (`update_bio.py`) runs every 5 minutes via a scheduled GitHub Actions workflow:

1. Fetches your most recent listen from the ListenBrainz public API (no token required for reads)
2. Authenticates to Bluesky using the AT Protocol XRPC API
3. Retrieves your current profile record
4. Strips any previous `🎵 Listening to:` section and appends the new track
5. Skips the write if the track hasn't changed since the last run
6. Truncates the track info if needed to stay within Bluesky's 256-character bio limit

## Configuration

The workflow runs every 5 minutes between 6am and 10pm CST (`2,7,12,17,22,27,32,37,42,47,52,57 0-3,12-23 * * *`). It does not run overnight. The minutes are offset from zero to avoid GitHub's most congested scheduling windows. The schedule can be changed by editing the `cron` expression in [`.github/workflows/update_bio.yml`](.github/workflows/update_bio.yml).

If you use a self-hosted Bluesky instance, set the `BLUESKY_HOST` environment variable to your PDS URL (defaults to `https://bsky.social`).

## License

MIT — see [LICENSE](LICENSE).

## Misc.

Made with Claude. (I know, I know)
