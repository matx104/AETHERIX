#!/usr/bin/env python3
"""
AETHERIX Daily Lesson Delivery Script v2
========================================
- Phase 1 (Jul 23 → Aug 27): Teaching — Days 1-36, one new lesson per day
- Phase 2 (Aug 28 → Sep 2): Revision Week — 6 consolidated review days
- Saves each delivered lesson to curriculum/delivered/ as a markdown file
- Outputs Discord-friendly summary for cron delivery

Usage:
    python3 deliver_lesson.py              # Today's lesson (auto-detect phase)
    python3 deliver_lesson.py --day 5      # Force specific teaching day
    python3 deliver_lesson.py --rev 3      # Force specific revision day
    python3 deliver_lesson.py --list       # List full schedule
"""

import os
import sys
import glob
import re
from datetime import date, timedelta

START_DATE = date(2026, 7, 23)
EXAM_DATE = date(2026, 9, 3)
REVISION_START = date(2026, 8, 28)
TEACHING_END = date(2026, 8, 27)
CURRICULUM_DIR = os.path.dirname(os.path.abspath(__file__))
DELIVERED_DIR = os.path.join(CURRICULUM_DIR, "delivered")

# Revision week schedule: each day reviews a cluster of teaching lessons
REVISION_SCHEDULE = {
    1: {
        "title": "🔄 Revision Day 1 — DTN Foundations",
        "date": "Aug 28",
        "review_lessons": [1, 2, 3, 4, 9],
        "focus": "Bundle Protocol v7, convergence layers (LTP/TCPCL/UDP-CL), store-and-forward, custody transfer, DTN integration",
        "key_numbers": "RFC 9171, RFC 5326, CCSDS 734.2-B-1, CUSTODY_REQUESTED=0x08, 37.5 min TCP handshake",
    },
    2: {
        "title": "🔄 Revision Day 2 — RL Routing Mastery",
        "date": "Aug 29",
        "review_lessons": [5, 6, 7, 8],
        "focus": "CGR vs RL, Q-learning agent (4 actions, 8 state vars), reward function, epsilon-greedy, multi-agent federated learning",
        "key_numbers": "R = α·delivery(1.0) − β·delay − γ·hops − δ·drops(10.0) − ε·energy, ε-decay=0.995, CGR fallback<0.3",
    },
    3: {
        "title": "🔄 Revision Day 3 — Quantum Security Deep Review",
        "date": "Aug 30",
        "review_lessons": [10, 11, 12, 13, 14],
        "focus": "BB84 (8 steps, sifting, QBER), E91 (entanglement, Bell inequality), quantum repeaters (ES-L4/L5), post-quantum crypto (ML-KEM/ML-DSA)",
        "key_numbers": "QBER<11%, Bell S≤2.0, Tsirelson=2.828, ML-DSA-65=3309 bytes, FIPS 203/204/205",
    },
    4: {
        "title": "🔄 Revision Day 4 — Infrastructure & Link Budgets",
        "date": "Aug 31",
        "review_lessons": [15, 16, 17, 18, 21, 23, 24, 25],
        "focus": "5-tier topology (241 nodes), DSN, constellations, Lagrange relays, optical link budget, FSPL derivation, orbital mechanics, contact windows",
        "key_numbers": "241 nodes, FSPL=365 dB, 1550nm, 54.6M-401M km, areostationary=17,032 km, synodic=780 days",
    },
    5: {
        "title": "🔄 Revision Day 5 — Systems, Standards & Design Defense",
        "date": "Sep 1",
        "review_lessons": [28, 29, 30, 32, 35, 37, 38],
        "focus": "Radiation effects (SEU/SEL/TID), TMR/SECDED mitigation, FDIR, data prioritization (P0-P4), CCSDS compression, standards compliance, performance analysis, design rationale defense",
        "key_numbers": "TMR=3x redundancy, SECDED ECC, P0<1min→P4<30days, 98.7% delivery ratio, CCSDS 121/122",
    },
    6: {
        "title": "🔄 Revision Day 6 — Presentation Rehearsal & Exam Strategy",
        "date": "Sep 2",
        "review_lessons": [39, 40, 41, 42],
        "focus": "Full presentation timing (18 min), mock interview (15 Qs, STAR-T), exam day protocol, ultimate cheat sheet, mindset",
        "key_numbers": "Presentation=15-20 min, Interview=30-40 min, Weights: Tech 40% / Pres 30% / Problem 20% / Practical 10%",
    },
}


def get_phase():
    """Determine if today is teaching or revision phase."""
    today = date.today()
    if today < START_DATE:
        return ("pre", 0)
    if today > TEACHING_END:
        if today >= REVISION_START and today <= date(2026, 9, 2):
            rev_day = (today - REVISION_START).days + 1
            return ("revision", rev_day)
        elif today >= EXAM_DATE:
            return ("exam", 0)
        else:
            return ("post", 0)
    else:
        day_num = (today - START_DATE).days + 1
        return ("teaching", day_num)


def get_lesson_file(day_num):
    """Find the lesson file for a given day number."""
    pattern = os.path.join(CURRICULUM_DIR, f"day_{day_num:02d}_*.md")
    matches = glob.glob(pattern)
    if matches:
        return matches[0]
    pattern = os.path.join(CURRICULUM_DIR, f"day_{day_num}_*.md")
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def read_lesson_content(filepath):
    """Read full lesson file content."""
    with open(filepath, 'r') as f:
        return f.read()


def extract_section(content, header_pattern):
    """Extract content between a header and the next header/horizontal rule."""
    match = re.search(header_pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def format_teaching_lesson(filepath, day_num):
    """Format a teaching lesson for Discord delivery."""
    content = read_lesson_content(filepath)
    basename = os.path.basename(filepath)

    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else basename

    objective = extract_section(content, r'## 🎯 Learning Objective\s+(.+?)(?=\n---|\n## )')
    concept = extract_section(content, r'## 📖 The Core Concept\s+(.+?)(?=\n## )')
    numbers = extract_section(content, r'## 📐 Key Numbers & Formulas\s+(.+?)(?=\n---|\n## )')
    refs = extract_section(content, r'## 🔗 Standards & References\s+(.+?)(?=\n---|\n## )')

    days_to_exam = (EXAM_DATE - date.today()).days

    msg = f"📚 **AETHERIX Exam Prep — {title}**\n\n"
    msg += f"📅 **Day {day_num} of 36 (Teaching)** | {days_to_exam} days to exam (Sep 3)\n\n"
    msg += f"🎯 **Today's Objective**\n{objective}\n\n"
    msg += f"📖 **The Lesson**\n\n{concept[:3000]}"

    if numbers:
        numbers_clean = numbers.replace('- ', '• ')
        msg += f"\n\n📐 **Key Numbers to Memorize**\n{numbers_clean[:1500]}"

    if refs:
        urls = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', refs)
        if urls:
            msg += "\n\n🔗 **References & Standards**"
            for name, url in urls[:8]:
                msg += f"\n• [{name}]({url})"

    msg += f"\n\n📂 **Full lesson:** `{basename}`"
    msg += f"\n📁 **All lessons:** [curriculum/](https://github.com/matx104/AETHERIX/tree/main/curriculum)"
    msg += f"\n🌐 **Demo site:** https://matx104.github.io/AETHERIX/"

    return msg


def format_revision_day(rev_num):
    """Format a revision day for Discord delivery."""
    rev = REVISION_SCHEDULE[rev_num]
    days_to_exam = (EXAM_DATE - date.today()).days

    msg = f"🔄 **AETHERIX {rev['title']}**\n\n"
    msg += f"📅 **Revision Day {rev_num} of 6** | {days_to_exam} days to exam (Sep 3)\n\n"
    msg += f"🎯 **Today's Focus**\n{rev['focus']}\n\n"
    msg += f"📐 **Key Numbers to Recall**\n{rev['key_numbers']}\n\n"

    # List the lessons being reviewed with links
    msg += "📚 **Lessons to Re-Review Today**"
    for day in rev["review_lessons"]:
        filepath = get_lesson_file(day)
        if filepath:
            basename = os.path.basename(filepath)
            # Extract title from file
            content = read_lesson_content(filepath)
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            lesson_title = title_match.group(1) if title_match else basename
            msg += f"\n• **Day {day}:** {lesson_title} → `{basename}`"

    msg += "\n\n⚡ **Action:** Re-read each lesson file. Focus on the '📐 Key Numbers' and '💡 How the Examiner Will Probe This' sections."
    msg += f"\n📁 **All lessons:** [curriculum/](https://github.com/matx104/AETHERIX/tree/main/curriculum)"
    msg += f"\n🌐 **Demo site:** https://matx104.github.io/AETHERIX/"

    return msg


def save_delivered_lesson(content, day_label):
    """Save the delivered lesson content to the delivered/ directory."""
    os.makedirs(DELIVERED_DIR, exist_ok=True)
    today_str = date.today().strftime("%Y-%m-%d")
    filename = f"{today_str}_{day_label}.md"
    filepath = os.path.join(DELIVERED_DIR, filename)

    # Write as a proper markdown file with metadata header
    with open(filepath, 'w') as f:
        f.write(f"<!-- Delivered: {today_str} -->\n\n")
        f.write(content)

    return filepath


def list_schedule():
    """Print the full 42-day schedule."""
    print("=" * 65)
    print("AETHERIX 42-DAY CURRICULUM — FULL SCHEDULE")
    print(f"  Teaching: Jul 23 → Aug 27 (36 days)")
    print(f"  Revision: Aug 28 → Sep 2 (6 days)")
    print(f"  Exam:     Sep 3, 2026")
    print("=" * 65)

    print("\n📖 TEACHING PHASE (Days 1-36)")
    print("-" * 65)
    for day in range(1, 37):
        filepath = get_lesson_file(day)
        if filepath:
            with open(filepath, 'r') as f:
                title = f.readline().strip().replace('# ', '')
            lesson_date = START_DATE + timedelta(days=day - 1)
            print(f"  Day {day:2d} ({lesson_date.strftime('%b %d')}): {title}")
        else:
            print(f"  Day {day:2d}: *** MISSING ***")

    print("\n🔄 REVISION WEEK (Aug 28 → Sep 2)")
    print("-" * 65)
    for rev_num in range(1, 7):
        rev = REVISION_SCHEDULE[rev_num]
        rev_date = REVISION_START + timedelta(days=rev_num - 1)
        print(f"  Rev {rev_num} ({rev_date.strftime('%b %d')}): {rev['title']}")

    print("=" * 65)


def main():
    if '--list' in sys.argv:
        list_schedule()
        return

    # Force specific teaching day
    if '--day' in sys.argv:
        idx = sys.argv.index('--day')
        day_num = int(sys.argv[idx + 1])
        filepath = get_lesson_file(day_num)
        if not filepath:
            print(f"❌ No lesson file found for Day {day_num}")
            sys.exit(1)
        msg = format_teaching_lesson(filepath, day_num)
        saved_path = save_delivered_lesson(msg, f"day_{day_num:02d}")
        print(f"<!-- Saved to: {saved_path} -->\n")
        print(msg)
        return

    # Force specific revision day
    if '--rev' in sys.argv:
        idx = sys.argv.index('--rev')
        rev_num = int(sys.argv[idx + 1])
        msg = format_revision_day(rev_num)
        # Save combined revision content
        full_content = msg + "\n\n---\n\n"
        for day in REVISION_SCHEDULE[rev_num]["review_lessons"]:
            fpath = get_lesson_file(day)
            if fpath:
                full_content += f"\n\n{'='*60}\n{read_lesson_content(fpath)}\n"
        saved_path = save_delivered_lesson(full_content, f"revision_{rev_num}")
        print(f"<!-- Saved to: {saved_path} -->\n")
        print(msg)
        return

    # Auto-detect phase
    phase, num = get_phase()

    if phase == "teaching":
        day_num = num
        filepath = get_lesson_file(day_num)
        if not filepath:
            print(f"❌ No lesson file found for Day {day_num}")
            sys.exit(1)
        msg = format_teaching_lesson(filepath, day_num)
        # Save to disk
        saved_path = save_delivered_lesson(msg, f"day_{day_num:02d}")
        print(f"<!-- Saved to: {saved_path} -->\n")
        print(msg)

    elif phase == "revision":
        rev_num = num
        msg = format_revision_day(rev_num)
        # Also pull full content from review lessons and save combined file
        full_content = msg + "\n\n---\n\n"
        for day in REVISION_SCHEDULE[rev_num]["review_lessons"]:
            filepath = get_lesson_file(day)
            if filepath:
                lesson_content = read_lesson_content(filepath)
                full_content += f"\n\n{'='*60}\n{lesson_content}\n"
        saved_path = save_delivered_lesson(full_content, f"revision_{rev_num}")
        print(f"<!-- Saved to: {saved_path} -->\n")
        print(msg)

    elif phase == "exam":
        print("🎓 **TODAY IS EXAM DAY — BISMILLAH!** 🦁")
        print("You've prepared for 42 days. Trust your preparation. Walk in as the expert.")

    elif phase == "pre":
        days_until = (START_DATE - date.today()).days
        print(f"⏳ Curriculum starts in {days_until} day(s). First lesson: Jul 23.")

    else:
        print("✅ Curriculum complete. Exam done.")


if __name__ == "__main__":
    main()
