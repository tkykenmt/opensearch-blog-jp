#!/usr/bin/env python3
"""Prepare session article from YouTube videos."""
import argparse
import subprocess
import re
from pathlib import Path
from datetime import datetime
from lib.state import get_work_dir, load_checkpoint, save_checkpoint

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
    ]
    for p in patterns:
        match = re.search(p, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id: str, output_dir: Path) -> Path:
    """Download transcript using yt-dlp."""
    output = output_dir / f"{video_id}.txt"
    if output.exists():
        return output
    
    try:
        subprocess.run([
            "yt-dlp", "--write-auto-sub", "--sub-lang", "en,ja",
            "--skip-download", "--sub-format", "vtt",
            "-o", str(output_dir / "%(id)s.%(ext)s"),
            f"https://www.youtube.com/watch?v={video_id}"
        ], check=True, capture_output=True)
        
        # Convert VTT to plain text
        vtt_files = list(output_dir.glob(f"{video_id}*.vtt"))
        if vtt_files:
            vtt = vtt_files[0].read_text()
            # Remove VTT headers and timestamps
            lines = []
            for line in vtt.split("\n"):
                if not line.strip() or line.startswith("WEBVTT") or "-->" in line:
                    continue
                if not re.match(r'^\d+$', line.strip()):
                    lines.append(line.strip())
            output.write_text("\n".join(lines))
            return output
    except Exception as e:
        print(f"Warning: Failed to get transcript for {video_id}: {e}")
    return None

def get_thumbnail(video_id: str, output_dir: Path) -> Path:
    """Download thumbnail."""
    output = output_dir / f"{video_id}.jpg"
    if output.exists():
        return output
    
    try:
        subprocess.run([
            "yt-dlp", "--write-thumbnail", "--skip-download",
            "-o", str(output_dir / "%(id)s.%(ext)s"),
            f"https://www.youtube.com/watch?v={video_id}"
        ], check=True, capture_output=True)
        
        # Find downloaded thumbnail
        for ext in [".jpg", ".webp", ".png"]:
            thumb = output_dir / f"{video_id}{ext}"
            if thumb.exists():
                if ext != ".jpg":
                    # Convert to jpg
                    subprocess.run(["convert", str(thumb), str(output)], check=True)
                    thumb.unlink()
                return output
    except Exception as e:
        print(f"Warning: Failed to get thumbnail for {video_id}: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description="Prepare session article from YouTube")
    parser.add_argument("--urls", nargs="+", required=True, help="YouTube URLs")
    parser.add_argument("--slug", help="Article slug (default: session-YYYYMMDD)")
    args = parser.parse_args()
    
    slug = args.slug or f"session-{datetime.now().strftime('%Y%m%d')}"
    work_dir = get_work_dir(slug)
    
    print(f"📁 Work directory: work/{slug}/")
    
    videos = []
    for url in args.urls:
        video_id = extract_video_id(url)
        if not video_id:
            print(f"⚠️  Invalid URL: {url}")
            continue
        
        print(f"📺 Processing: {video_id}")
        
        transcript = get_transcript(video_id, work_dir)
        if transcript:
            print(f"   ✓ Transcript: {transcript.name}")
        
        thumbnail = get_thumbnail(work_dir / "images", video_id)
        if thumbnail:
            print(f"   ✓ Thumbnail: {thumbnail.name}")
        
        videos.append({
            "id": video_id,
            "url": url,
            "transcript": str(transcript) if transcript else None,
            "thumbnail": str(thumbnail) if thumbnail else None
        })
    
    # Save checkpoint
    checkpoint = load_checkpoint(slug)
    checkpoint.update({
        "status": "prepared",
        "type": "session",
        "videos": videos
    })
    save_checkpoint(slug, checkpoint)
    
    print(f"\n✅ Ready for writing")
    print(f"   Transcripts and thumbnails saved to work/{slug}/")
    print(f"   Next: Run Kiro with session-writer agent")

if __name__ == "__main__":
    main()
