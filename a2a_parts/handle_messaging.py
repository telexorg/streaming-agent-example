from fastapi.responses import StreamingResponse
import a2a.types as a2a_types
import a2a.error_types as a2a_error_types
import os
import time
import json
import random
from functools import reduce
from uuid import uuid4 as uuid
from a2a_parts.messaging import build_agent_message_from_line

def get_task_id(params: a2a_types.MessageSendParams):
    task_id = uuid().hex if not params.message.taskId else params.message.taskId
    return task_id

def iterfile(filepath: str):
    with open(filepath, mode="rb") as file_like:
        yield from file_like


def waypoints_generator():
    waypoints = open('documents/waypoints.json')
    waypoints = json.load(waypoints)
    for waypoint in waypoints[0: 10]:
        data = json.dumps(waypoint)
        yield f"event: locationUpdate\ndata: {data}\n\n"

def get_random_sherlock_chapter():
    file_path = "documents/the-adventures-of-sherlock-holmes.txt"

    # From the Table of Contents
    chapter_titles = [
        "I. A SCANDAL IN BOHEMIA",
        "II. THE RED-HEADED LEAGUE",
        "III. A CASE OF IDENTITY",
        "IV. THE BOSCOMBE VALLEY MYSTERY",
        "V. THE FIVE ORANGE PIPS",
        "VI. THE MAN WITH THE TWISTED LIP",
        "VII. THE ADVENTURE OF THE BLUE CARBUNCLE",
        "VIII. THE ADVENTURE OF THE SPECKLED BAND",
        "IX. THE ADVENTURE OF THE ENGINEER’S THUMB",
        "X. THE ADVENTURE OF THE NOBLE BACHELOR",
        "XI. THE ADVENTURE OF THE BERYL CORONET",
        "XII. THE ADVENTURE OF THE COPPER BEECHES",
    ]

    chosen_idx = random.randint(0, len(chapter_titles) - 1)
    chosen_title = chapter_titles[chosen_idx]
    next_title = chapter_titles[chosen_idx + 1] if chosen_idx + 1 < len(chapter_titles) else None

    with open(file_path, "r", encoding="utf-8") as f:
        in_chapter = False
        passed_intro = False

        for line in f:
            stripped = line.strip().upper()

            # Wait until we pass the TOC and reach the real content
            if not passed_intro:
                if stripped == "I. A SCANDAL IN BOHEMIA":
                    passed_intro = True
                else:
                    continue  # skip lines until we reach real chapters

            # Start capturing if the chapter title matches
            if stripped == chosen_title.upper():
                in_chapter = True

                meta_response = build_agent_message_from_line(chosen_title.title())

                yield f"event: storyMeta\ndata: {meta_response.model_dump_json()}\n\n"
                continue

            # If we're inside the chapter and we hit the next one, break
            if in_chapter and next_title and stripped == next_title.upper():
                break

            if in_chapter:
                if line.strip():
                    a2a_response = build_agent_message_from_line(line)
                    yield f"event: storyLine\ndata: {a2a_response.model_dump_json()}\n\n"


def get_random_bible_chapter():
    '''
    Get a random 100KB chunk
    Seek up to the beginning of the nearest chapter
    Read down to the end of the chapter
    Stream that chapter verse by verse
    '''

    def extract_chapter_verse(line):
        parts = line.strip().split(" ", 1)
        if len(parts) < 2:
            return None, None
        chapter_verse = parts[0]
        if ":" not in chapter_verse:
            return None, None
        try:
            chapter_str, verse_str = chapter_verse.split(":")
            return int(chapter_str), int(verse_str)
        except ValueError:
            return None, None

    file_path = "documents/bible.txt"
    file_size = os.path.getsize(file_path)

    # Choose a random offset
    start_pos = random.randint(0, max(0, file_size - 100 * 1024))

    with open(file_path, "r", encoding="utf-8") as f:
        f.seek(start_pos)
        if start_pos != 0:
            f.readline()  # skip partial line
        forward_lines = f.readlines()

    with open(file_path, "r", encoding="utf-8") as f:
        full_lines = f.readlines()

    # Find the index of the first full line from the forward chunk
    first_line = forward_lines[0].strip()
    try:
        start_index = full_lines.index(first_line + "\n")
    except ValueError:
        # fallback in case of line-ending inconsistency
        start_index = 0

    # Walk backward to find the nearest line with verse `X:1`
    chapter_start_index = start_index
    for i in range(start_index, -1, -1):
        line = full_lines[i]
        chapter, verse = extract_chapter_verse(line)
        if chapter is not None and verse == 1:
            chapter_start_index = i
            break

    # Identify the current chapter
    current_chapter, _ = extract_chapter_verse(full_lines[chapter_start_index])

    # Yield lines in this chapter until next chapter begins
    for line in full_lines[chapter_start_index:]:
        chapter, verse = extract_chapter_verse(line)
        if chapter is not None and chapter != current_chapter and verse == 1:
            break


        a2a_response = build_agent_message_from_line(line)

        yield f"event: verse\ndata: {a2a_response.model_dump_json()}\n\n"


def get_random_rj_scene():
    file_path = "documents/romeo-and-juliet.txt"

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    scenes = []
    act_at_last_scene = None
    current_act = None
    current_scene = None
    buffer = []
    start_index = 0

    for i, line in enumerate(lines):
        stripped = line.strip().upper()

        if stripped.startswith("ACT "):
            current_act = stripped.title()  # Don't assign yet
            continue

        if stripped.startswith("SCENE "):
            # Capture the previous scene
            if current_scene and buffer:
                scenes.append({
                    "act": act_at_last_scene,
                    "scene": current_scene,
                    "start": start_index,
                    "end": i,
                    "lines": buffer,
                })
                buffer = []

            # New scene begins here
            current_scene = stripped.title()
            start_index = i
            act_at_last_scene = current_act  # Now assign act to this scene
            continue

        if current_scene:
            buffer.append(line)

    # Capture final scene
    if current_scene and buffer:
        scenes.append({
            "act": act_at_last_scene,
            "scene": current_scene,
            "start": start_index,
            "end": len(lines),
            "lines": buffer,
        })

    if not scenes:
        raise ValueError("No scenes found in Romeo and Juliet text.")

    chosen = random.choice(scenes)

    # Yield ACT and SCENE as meta info
    meta_text = f"{chosen['act']} - {chosen['scene']}"
    meta_response = build_agent_message_from_line(meta_text)

    yield f"event: sceneMeta\ndata: {meta_response.model_dump_json()}\n\n"

    # Yield lines from the scene
    for line in chosen["lines"]:
        a2a_response = build_agent_message_from_line(line)

        yield f"event: sceneLine\ndata: {a2a_response.model_dump_json()}\n\n"


def handle_message_stream(params: a2a_types.MessageSendParams):
    try:
        params.message.parts
        text_prompt = reduce(
            lambda acc, cur: (acc + cur.text).lower() if cur.kind == "text" else acc, 
            params.message.parts, 
            ""
        )

        if "bible" in text_prompt:
            return StreamingResponse(get_random_bible_chapter(), media_type="text/event-stream")
        elif "romeo" in text_prompt or "juliet" in text_prompt:
            return StreamingResponse(get_random_rj_scene(), media_type="text/event-stream")
        else:
            return StreamingResponse(get_random_sherlock_chapter(), media_type="text/event-stream")
        
    except:
        response = a2a_types.JSONRPCResponse(
            messageId=uuid().hex,
            error=a2a_error_types.InternalError(
                message="An error occured",
            ),
        )
        return response
