#!/usr/bin/env python3
"""
AETHERIX Daily Lesson Delivery Script
=====================================
Outputs the lesson for the current day (Day 1 = July 23, 2026).
Designed to be called by a daily cron job.

Usage:
    python3 curriculum/deliver_lesson.py          # Today's lesson
    python3 curriculum/deliver_lesson.py --day 5  # Specific day
    python3 curriculum/deliver_lesson.py --list   # List all lessons
"""

import os
import sys
import glob
import re
from datetime import date, timedelta

# Day 1 starts July 23, 2026
START_DATE = date(2026, 7, 23)
EXAM_DATE = date(2026, 9, 3)
CURRICULUM_DIR = os.path.dirname(os.path.abspath(__file__))


def get_current_day():
    """Calculate which day number we're on (1-indexed)."""
    today = date.today()
    delta = (today - START_DATE).days + 1
    return max(1, min(delta, 42))


def get_lesson_file(day_num):
    """Find the lesson file for a given day number."""
    pattern = os.path.join(CURRICULUM_DIR, f"day_{day_num:02d}_*.md")
    matches = glob.glob(pattern)
    if matches:
        return matches[0]
    # Try without zero-padding
    pattern = os.path.join(CURRICULUM_DIR, f"day_{day_num}_*.md")
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def format_lesson_for_discord(filepath):
    """Read a lesson file and format key sections for Discord delivery."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Extract day number from filename
    basename = os.path.basename(filepath)
    day_match = re.match(r'day_(\d+)', basename)
    day_num = int(day_match.group(1)) if day_match else 0

    # Extract title (first H1)
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else basename

    # Extract learning objective
    obj_match = re.search(r'## 🎯 Learning Objective\s+(.+?)(?=\n---|\n## )', content, re.DOTALL)
    objective = obj_match.group(1).strip() if obj_match else ""

    # Extract core concept (first paragraph after 📖)
    concept_match = re.search(r'## 📖 The Core Concept\s+(.+?)(?=\n## )', content, re.DOTALL)
    concept = concept_match.group(1).strip() if concept_match else ""

    # Extract key numbers
    numbers_match = re.search(r'## 📐 Key Numbers & Formulas\s+(.+?)(?=\n---|\n## )', content, re.DOTALL)
    numbers = numbers_match.group(1).strip() if numbers_match else ""

    # Extract references
    refs_match = re.search(r'## 🔗 Standards & References\s+(.+?)(?=\n---|\n## )', content, re.DOTALL)
    refs = refs_match.group(1).strip() if refs_match else ""

    # Build Discord-friendly message
    days_to_exam = (EXAM_DATE - date.today()).days

    msg = f"""📚 **AETHERIX Exam Prep — {title}**

📅 **Day {day_num} of 42** | {days_to_exam} days to exam (Sep 3)

🎯 **Today's Objective**
{objective}

📖 **The Lesson**

{concept[:3000]}"""

    if numbers:
        # Clean up bullet points for Discord
        numbers_clean = numbers.replace('- ', '• ')
        msg += f"\n\n📐 **Key Numbers to Memorize**\n{numbers_clean[:1500]}"

    if refs:
        # Extract just the URLs for compact display
        urls = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', refs)
        if urls:
            msg += "\n\n🔗 **References & Standards**"
            for name, url in urls[:8]:
                msg += f"\n• [{name}]({url})"

    msg += f"\n\n📂 **Full Lesson:** `{basename}` in the AETHERIX repo"
    msg += f"\n📁 **All Lessons:** [curriculum/](https://github.com/matx104/AETHERIX/tree/main/curriculum)"
    msg += f"\n🌐 **Demo Site:** https://matx104.github.io/AETHERIX/"

    return msg


def list_all_lessons():
    """Print a summary of all 42 lessons."""
    print("=" * 60)
    print("AETHERIX 42-DAY CURRICULUM — ALL LESSONS")
    print("=" * 60)
    for day in range(1, 43):
        filepath = get_lesson_file(day)
        if filepath:
            basename = os.path.basename(filepath)
            # Extract title from H1
            with open(filepath, 'r') as f:
                first_line = f.readline().strip()
            title = first_line.replace('# ', '')
            lesson_date = START_DATE + timedelta(days=day - 1)
            print(f"  Day {day:2d} ({lesson_date.strftime('%b %d')}): {title}")
        else:
            print(f"  Day {day:2d}: *** MISSING ***")
    print("=" * 60)


def main():
    if '--list' in sys.argv:
        list_all_lessons()
        return

    if '--day' in sys.argv:
        idx = sys.argv.index('--day')
        day_num = int(sys.argv[idx + 1])
    else:
        day_num = get_current_day()

    filepath = get_lesson_file(day_num)
    if not filepath:
        print(f"❌ No lesson file found for Day {day_num}")
        sys.exit(1)

    # Output the formatted Discord message to stdout (cron picks this up)
    msg = format_lesson_for_discord(filepath)
    print(msg)


if __name__ == "__main__":
    main()
