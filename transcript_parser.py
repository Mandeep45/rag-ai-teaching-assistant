import io
import re

import webvtt


def parse_transcript(content, format="auto"):
    """
    Parse transcript from any format and return clean plain text.
    format: "auto", "vtt", "srt", "plain"
    """
    if format == "auto":
        if content.strip().startswith("WEBVTT"):
            format = "vtt"
        elif re.search(r'^\d+\s*\n\d{2}:\d{2}', content, re.MULTILINE):
            format = "srt"
        else:
            format = "plain"

    if format == "vtt":
        try:
            vtt_file = io.StringIO(content)
            captions = webvtt.read_buffer(vtt_file)
            clean_text = " ".join([caption.text.strip() for caption in captions])
            clean_text = re.sub(r'\[.*?\]', '', clean_text)  # remove [Instructor], [Narrator] etc
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            return clean_text
        except Exception as e:
            print(f"VTT parsing failed: {e}")
            clean_text = re.sub(r'\d{2,3}:\d{2}:\d{2}\.\d{3} --> \d{2,3}:\d{2}:\d{2}\.\d{3}', '', content)
            clean_text = re.sub(r'WEBVTT.*?\n', '', clean_text)
            clean_text = re.sub(r'Kind:.*?\n', '', clean_text)       # remove Kind: captions
            clean_text = re.sub(r'Language:.*?\n', '', clean_text)   # remove Language: en
            clean_text = re.sub(r'\[.*?\]', '', clean_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            return clean_text
    
    if format == "srt":
        try:
            clean_text = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)
            clean_text = re.sub(r'\[.*?\]', '', clean_text)  # remove [Instructor], [Narrator] etc
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            return clean_text
        except Exception as e:
            print(f"SRT parsing failed: {e}")
            return content
    
    if format == "plain":
        clean_text = re.sub(r'\s+', ' ', content).strip()
        return clean_text