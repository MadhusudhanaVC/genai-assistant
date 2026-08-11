import re


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = []
    previous_blank = False

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            if not previous_blank:
                lines.append("")
            previous_blank = True
            continue

        lines.append(line)
        previous_blank = False

    return "\n".join(lines).strip()


def split_sections(text: str) -> list[str]:
    sections = []
    current = []

    for line in text.splitlines():
        is_heading = re.match(r"^#{1,6}\s+", line)

        if is_heading and current:
            section = "\n".join(current).strip()

            if section:
                sections.append(section)

            current = []

        current.append(line)

    if current:
        section = "\n".join(current).strip()

        if section:
            sections.append(section)

    return sections


def split_large_section(
    section: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    if len(section) <= chunk_size:
        return [section]

    lines = section.splitlines()
    chunks = []
    current_lines = []
    current_length = 0
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block

        line_length = len(line)

        if current_lines and current_length + line_length + 1 > chunk_size:
            if in_code_block:
                current_lines.append(line)
                current_length += line_length + 1
                continue

            chunk = "\n".join(current_lines).strip()

            if chunk:
                chunks.append(chunk)

            overlap_lines = []
            overlap_length = 0

            for previous_line in reversed(current_lines):
                if overlap_length + len(previous_line) + 1 > overlap:
                    break

                overlap_lines.insert(0, previous_line)
                overlap_length += len(previous_line) + 1

            current_lines = overlap_lines
            current_length = overlap_length

        current_lines.append(line)
        current_length += line_length + 1

    if current_lines:
        chunk = "\n".join(current_lines).strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 80,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    text = clean_text(text)

    if not text:
        return []

    sections = split_sections(text)

    chunks = []
    current = ""

    for section in sections:
        if len(section) > chunk_size:
            if current:
                chunks.append(current)
                current = ""

            chunks.extend(
                split_large_section(
                    section,
                    chunk_size,
                    overlap,
                )
            )

            continue

        if not current:
            current = section
            continue

        combined = current + "\n\n" + section

        if len(combined) <= chunk_size:
            current = combined
        else:
            chunks.append(current)
            current = section

    if current:
        chunks.append(current)

    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]