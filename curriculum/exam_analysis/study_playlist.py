#!/usr/bin/env python3
"""
AETHERIX Exam Playlist Study Script
=====================================
Fetches transcripts for un-studied videos from the Al-Nafi exam playlist,
saves them to disk for the agent cron to analyze.

Usage:
  python3 study_playlist.py              # Fetch next batch (13 videos)
  python3 study_playlist.py --batch 5    # Fetch specific batch size
  python3 study_playlist.py --status     # Show progress
  python3 study_playlist.py --list       # List unstudied videos
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, date
from pathlib import Path

# Paths
BASE = Path("/home/ubuntu/AETHERIX/curriculum/exam_analysis")
PLAYLIST_FILE = BASE / "playlist_videos.json"
PROGRESS_FILE = BASE / "progress.json"
TRANSCRIPTS_DIR = BASE / "transcripts"
PATTERNS_FILE = BASE / "AETHERIX_EXAM_PATTERNS.md"

# Load APIFY_TOKEN from Infisical vault (fallback: flat .env)
def load_apify_token():
    """Load APIFY_TOKEN from Infisical vault, fall back to flat .env if vault is unreachable."""
    # --- Try Infisical first ---
    try:
        import urllib.request, json as _json

        # Machine Identity creds live in AMEEN's .env (the vault keeper)
        inf_env = Path("/home/ubuntu/.hermes/profiles/ameen/.env")
        creds = {}
        if inf_env.exists():
            for line in inf_env.read_text().splitlines():
                if line.startswith("INFISICAL_") and "=" in line:
                    k, v = line.split("=", 1)
                    creds[k] = v.strip()

        client_id = creds.get("INFISICAL_CLIENT_ID", "")
        client_secret = creds.get("INFISICAL_CLIENT_SECRET", "")
        domain = creds.get("INFISICAL_DOMAIN", "https://app.infisical.com")
        project_id = creds.get("INFISICAL_PROJECT_ID", "40614a4c-30a7-4efb-bc12-2354300d24b6")

        if client_id and client_secret:
            # Auth
            auth_body = _json.dumps({"clientId": client_id, "clientSecret": client_secret}).encode()
            req = urllib.request.Request(
                f"{domain}/api/v1/auth/universal-auth/login",
                data=auth_body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                auth_data = _json.loads(resp.read())
            access_token = auth_data["accessToken"]

            # Read APIFY_TOKEN
            secret_url = f"{domain}/api/v3/secrets/raw/APIFY_TOKEN?workspaceId={project_id}&environment=dev"
            req2 = urllib.request.Request(
                secret_url,
                headers={"Authorization": f"Bearer {access_token}"},
                method="GET",
            )
            with urllib.request.urlopen(req2, timeout=10) as resp:
                secret_data = _json.loads(resp.read())

            token = secret_data.get("secret", {}).get("secretValue", "")
            if token:
                os.environ["APIFY_TOKEN"] = token
                return  # Success — we're done

    except Exception as e:
        # Vault unreachable — fall through to .env backup
        print(f"  ⚠️  Infisical vault unreachable ({e}), falling back to .env")

    # --- Fallback: flat .env ---
    env_file = Path("/home/ubuntu/.hermes/.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("APIFY_TOKEN=") or line.startswith("APIFY_API_TOKEN="):
                key, val = line.split("=", 1)
                os.environ[key] = val.strip()


def load_progress():
    """Load or create progress tracker"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {
        "total_videos": 131,
        "studied_video_ids": [],
        "study_start_date": str(date.today()),
        "max_days": 10,
        "videos_per_day": 13,
        "last_run_date": None,
        "run_history": []
    }


def save_progress(progress):
    """Save progress tracker"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def load_playlist():
    """Load playlist video list"""
    with open(PLAYLIST_FILE) as f:
        return json.load(f)


def get_unstudied(videos, progress):
    """Get list of videos not yet studied"""
    studied = set(progress.get("studied_video_ids", []))
    return [v for v in videos if v["id"] not in studied]


def fetch_transcript(video_id):
    """Fetch transcript via Apify using summarize CLI"""
    transcript_file = TRANSCRIPTS_DIR / f"{video_id}.txt"
    
    # Skip if already downloaded
    if transcript_file.exists() and transcript_file.stat().st_size > 100:
        return True, "already cached"
    
    load_apify_token()
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    json_output = f"/tmp/transcript_{video_id}.json"
    
    # Fetch via summarize + apify (safe: url and json_output are internally constructed)
    with open(json_output, 'w') as outfile:
        result = subprocess.run(
            ["summarize", url, "--youtube", "apify", "--extract", "--json"],
            stdout=outfile, stderr=subprocess.PIPE, text=True, timeout=120
        )
    
    if result.returncode != 0:
        return False, f"summarize failed: {result.stderr[:200]}"
    
    # Parse JSON and extract transcript
    try:
        with open(json_output) as f:
            raw = f.read()
        
        # Handle extra data after JSON
        decoder = json.JSONDecoder()
        data, _ = decoder.raw_decode(raw)
        
        content = data.get("extracted", {}).get("content", "")
        source = data.get("extracted", {}).get("transcriptSource", "none")
        word_count = data.get("extracted", {}).get("transcriptWordCount", 0)
        
        if not content or word_count < 50:
            return False, f"empty transcript (source={source}, words={word_count})"
        
        # Save clean transcript
        with open(transcript_file, 'w') as f:
            f.write(content)
        
        # Clean up temp file
        os.unlink(json_output)
        
        return True, f"source={source}, words={word_count}"
        
    except Exception as e:
        return False, f"parse error: {e}"


def run_batch(batch_size=None):
    """Fetch transcripts for next batch of unstudied videos"""
    progress = load_progress()
    videos = load_playlist()
    unstudied = get_unstudied(videos, progress)
    
    if not unstudied:
        print("ALL VIDEOS STUDIED! Nothing to do.")
        return
    
    if batch_size is None:
        batch_size = progress.get("videos_per_day", 13)
    
    batch = unstudied[:batch_size]
    today = str(date.today())
    
    print(f"=== AETHERIX Playlist Study Batch ===")
    print(f"Date: {today}")
    print(f"Unstudied: {len(unstudied)} | Batch size: {len(batch)}")
    print()
    
    success = 0
    failed = 0
    new_ids = []
    
    for i, video in enumerate(batch, 1):
        vid = video["id"]
        title = str(video.get("title", "Unknown"))[:60]
        print(f"[{i}/{len(batch)}] {vid} | {title}")
        
        ok, msg = fetch_transcript(vid)
        
        if ok:
            success += 1
            new_ids.append(vid)
            print(f"  ✅ {msg}")
        else:
            failed += 1
            # Still mark as attempted so we don't retry forever
            new_ids.append(vid)
            print(f"  ❌ {msg}")
        
        # Rate limit — don't hammer Apify
        if i < len(batch):
            time.sleep(3)
    
    # Update progress
    progress["studied_video_ids"].extend(new_ids)
    progress["last_run_date"] = today
    
    # Check if we've hit the day limit
    start_date = datetime.strptime(progress["study_start_date"], "%Y-%m-%d").date()
    days_elapsed = (date.today() - start_date).days
    
    run_entry = {
        "date": today,
        "batch_size": len(batch),
        "success": success,
        "failed": failed,
        "video_ids": new_ids,
        "day": days_elapsed + 1
    }
    progress["run_history"].append(run_entry)
    
    save_progress(progress)
    
    print()
    print(f"=== Batch Complete ===")
    print(f"Success: {success} | Failed: {failed}")
    print(f"Total studied: {len(progress['studied_video_ids'])} / {progress['total_videos']}")
    print(f"Day {days_elapsed + 1} of {progress['max_days']}")
    
    if days_elapsed + 1 >= progress["max_days"]:
        print()
        print("⚠️  MAX DAYS REACHED — Study period complete!")
        print("The cron should auto-pause after this run.")
    
    remaining = progress["total_videos"] - len(progress["studied_video_ids"])
    if remaining > 0:
        print(f"Remaining: {remaining} videos")
    else:
        print("🎉 ALL VIDEOS STUDIED!")


def show_status():
    """Show current study progress"""
    progress = load_progress()
    videos = load_playlist()
    studied = progress.get("studied_video_ids", [])
    remaining = len(videos) - len(studied)
    
    start_date = datetime.strptime(progress["study_start_date"], "%Y-%m-%d").date()
    days_elapsed = (date.today() - start_date).days + 1
    
    print("=== AETHERIX Playlist Study Status ===")
    print(f"Total videos:      {len(videos)}")
    print(f"Studied:           {len(studied)}")
    print(f"Remaining:         {remaining}")
    print(f"Study start:       {progress['study_start_date']}")
    print(f"Day:               {days_elapsed} of {progress['max_days']}")
    print(f"Videos per day:    {progress.get('videos_per_day', 13)}")
    print(f"Last run:          {progress.get('last_run_date', 'never')}")
    print()
    
    if progress.get("run_history"):
        print("Run History:")
        for run in progress["run_history"][-5:]:
            print(f"  Day {run['day']} ({run['date']}): {run['success']}✅ {run['failed']}❌")


def list_unstudied():
    """List all unstudied videos"""
    progress = load_progress()
    videos = load_playlist()
    unstudied = get_unstudied(videos, progress)
    
    print(f"=== Unstudied Videos ({len(unstudied)}) ===")
    for i, v in enumerate(unstudied[:20], 1):
        print(f"  {i}. {v['id']} | {str(v.get('title', '?'))[:60]}")
    if len(unstudied) > 20:
        print(f"  ... and {len(unstudied) - 20} more")


def check_should_pause():
    """Check if the study period is over — used by cron to auto-pause"""
    progress = load_progress()
    start_date = datetime.strptime(progress["study_start_date"], "%Y-%m-%d").date()
    days_elapsed = (date.today() - start_date).days + 1
    
    if days_elapsed > progress["max_days"]:
        print("PAUSE: Study period exceeded max days")
        sys.exit(99)  # Special exit code for cron to detect
    
    remaining = progress["total_videos"] - len(progress.get("studied_video_ids", []))
    if remaining <= 0:
        print("PAUSE: All videos studied")
        sys.exit(99)
    
    print(f"CONTINUE: Day {days_elapsed}/{progress['max_days']}, {remaining} remaining")


if __name__ == "__main__":
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if "--status" in sys.argv:
        show_status()
    elif "--list" in sys.argv:
        list_unstudied()
    elif "--check-pause" in sys.argv:
        check_should_pause()
    elif "--batch" in sys.argv:
        idx = sys.argv.index("--batch")
        size = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else 13
        run_batch(size)
    else:
        run_batch()
