"""File, text, and prompt utilities."""

import json
import re
from pathlib import Path

import json5
from safetytooling.data_models import Prompt


def find_spec_path(spec_name: str) -> Path:
    """Find a spec text file by name, searching spec/ and its subdirectories."""
    spec_filename = f"{spec_name}.txt"
    project_root = Path(__file__).resolve().parent.parent.parent
    spec_base_dir = project_root / "spec"

    direct_path = spec_base_dir / spec_filename
    if direct_path.exists():
        return direct_path

    found_paths = list(spec_base_dir.rglob(spec_filename))

    if len(found_paths) == 0:
        raise FileNotFoundError(
            f"Spec file '{spec_filename}' not found in {spec_base_dir} or its subdirectories.\n"
            f"Searched for: {spec_base_dir / spec_filename} and {spec_base_dir}/**/{spec_filename}"
        )
    elif len(found_paths) > 1:
        paths_str = "\n  ".join(str(p) for p in found_paths)
        raise FileNotFoundError(
            f"Multiple spec files named '{spec_filename}' found:\n  {paths_str}\n"
            f"Spec names must be unique across all subdirectories."
        )

    return found_paths[0]


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a file or directory name."""
    invalid_chars = '<>:"/\\|?*'
    sanitized = name
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    sanitized = ''.join(char if char.isprintable() else '_' for char in sanitized)
    sanitized = sanitized.strip('. ')
    return sanitized[:200]


def create_json_prompt(MODEL_ID: str, user_text: str, prefill: str = '```json\n[\n  {"') -> Prompt:
    """Create a prompt with prefill for JSON generation."""
    if "claude" in MODEL_ID and prefill:
        return Prompt(messages=[
            {"role": "user", "content": [{"type": "text", "text": user_text}]},
            {"role": "assistant", "content": [{"type": "text", "text": prefill}]}
        ])
    else:
        return Prompt(messages=[
            {"role": "user", "content": [{"type": "text", "text": user_text}]}
        ])


def parse_json_response(response: str, prefill: str | None = None):
    """Parse JSON from LLM response with prefill, handling malformed JSON."""
    cleaned_response = response.replace("```json", "").replace("```", "").strip()
    try:
        return json5.loads(cleaned_response)
    except json.JSONDecodeError:
        pass

    if prefill and not response.strip().startswith(prefill.strip()):
        full_response = prefill + response
    else:
        full_response = response

    full_response_cleaned = full_response.replace("```json", "").replace("```", "").strip()
    try:
        return json5.loads(full_response_cleaned)
    except json.JSONDecodeError:
        pass

    print(f"Failed to parse JSON from response")
    print(f"Response length: {len(response)}")
    print(f"Response: {response}")
    print(f"Cleaned response: {cleaned_response}")
    raise ValueError(f"Failed to parse JSON from response: {response}")


def extract_text_from_tag(response: str, tag_name: str) -> str:
    """Extract text content from XML-style tags in LLM response."""
    pattern = rf"<{tag_name}>(.+?)</{tag_name}>"
    try:
        return re.findall(pattern, response, re.DOTALL)[0].strip()
    except IndexError:
        if f"<{tag_name}>" in response and f"</{tag_name}>" not in response:
            print(f"Warning: No closing tag </{tag_name}> found in response")
            return response.split(f"<{tag_name}>")[-1].strip()
        elif f"</{tag_name}>" in response and f"<{tag_name}>" not in response:
            print(f"Warning: No opening tag <{tag_name}> found in response")
            return response.split(f"</{tag_name}>")[0].strip()
        else:
            print(f"Warning: No <{tag_name}> tags found in response")
            return response
