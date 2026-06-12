#!/usr/bin/env python3
"""Update Bluesky profile bio with the most recent ListenBrainz scrobble."""

import json
import os
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

LISTENBRAINZ_USERNAME = os.environ["LISTENBRAINZ_USERNAME"]
BLUESKY_HANDLE = os.environ["BLUESKY_HANDLE"]
BLUESKY_APP_PASSWORD = os.environ["BLUESKY_APP_PASSWORD"]
BLUESKY_HOST = os.environ.get("BLUESKY_HOST", "https://bsky.social")

ADAFRUIT_AIO_USERNAME = os.environ.get("ADAFRUIT_AIO_USERNAME")
ADAFRUIT_IO_KEY = os.environ.get("ADAFRUIT_IO_KEY")
ADAFRUIT_IO_FEED = os.environ.get("ADAFRUIT_IO_FEED", "now-playing")

NOW_PLAYING_MARKER = "\n\n🎵 "
MAX_BIO_LENGTH = 256


def get_latest_listen() -> tuple[str, str] | None:
    url = f"https://api.listenbrainz.org/1/user/{LISTENBRAINZ_USERNAME}/listens"
    resp = requests.get(url, params={"count": 1}, timeout=10)
    resp.raise_for_status()
    listens = resp.json().get("payload", {}).get("listens", [])
    if not listens:
        return None
    meta = listens[0].get("track_metadata", {})
    track = meta.get("track_name") or "Unknown Track"
    artist = meta.get("artist_name") or "Unknown Artist"
    return track, artist


def create_session() -> tuple[str, str]:
    resp = requests.post(
        f"{BLUESKY_HOST}/xrpc/com.atproto.server.createSession",
        json={"identifier": BLUESKY_HANDLE, "password": BLUESKY_APP_PASSWORD},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["accessJwt"], data["did"]


def get_profile_record(access_jwt: str, did: str) -> dict:
    resp = requests.get(
        f"{BLUESKY_HOST}/xrpc/com.atproto.repo.getRecord",
        params={"repo": did, "collection": "app.bsky.actor.profile", "rkey": "self"},
        headers={"Authorization": f"Bearer {access_jwt}"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["value"]


def put_profile_record(access_jwt: str, did: str, record: dict) -> None:
    resp = requests.post(
        f"{BLUESKY_HOST}/xrpc/com.atproto.repo.putRecord",
        json={
            "repo": did,
            "collection": "app.bsky.actor.profile",
            "rkey": "self",
            "record": record,
        },
        headers={"Authorization": f"Bearer {access_jwt}"},
        timeout=10,
    )
    resp.raise_for_status()


def send_to_adafruit_io(track: str, artist: str) -> None:
    if not ADAFRUIT_AIO_USERNAME or not ADAFRUIT_IO_KEY:
        return
    payload = json.dumps({"title": track, "artist": artist})
    resp = requests.post(
        f"https://io.adafruit.com/api/v2/{ADAFRUIT_AIO_USERNAME}/feeds/{ADAFRUIT_IO_FEED}/data",
        json={"value": payload},
        headers={"X-AIO-Key": ADAFRUIT_IO_KEY},
        timeout=10,
    )
    resp.raise_for_status()
    log(f"Sent to Adafruit IO: {payload}")


def build_description(current: str, track_info: str) -> str:
    base = current.split(NOW_PLAYING_MARKER)[0] if NOW_PLAYING_MARKER in current else current
    suffix = f"{NOW_PLAYING_MARKER}Listening to: {track_info}"

    # Truncate track info if the full bio would exceed Bluesky's limit
    combined = base + suffix
    if len(combined) > MAX_BIO_LENGTH:
        available = MAX_BIO_LENGTH - len(base) - len(NOW_PLAYING_MARKER) - len("Listening to: ")
        track_info = track_info[:max(0, available - 1)] + "…"
        suffix = f"{NOW_PLAYING_MARKER}Listening to: {track_info}"

    return base + suffix


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def main() -> None:
    result = get_latest_listen()
    if not result:
        log("No recent listens found.")
        sys.exit(0)

    track, artist = result
    track_info = f"{track} by {artist}"

    access_jwt, did = create_session()
    record = get_profile_record(access_jwt, did)

    current_description = record.get("description") or ""
    new_description = build_description(current_description, track_info)

    if new_description == current_description:
        log(f"No change: {track_info}")
        sys.exit(0)

    record["description"] = new_description
    put_profile_record(access_jwt, did, record)
    log(f"Updated bio: {track_info}")

    send_to_adafruit_io(track, artist)


if __name__ == "__main__":
    main()
