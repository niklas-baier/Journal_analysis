import os
import re
import pandas as pd

# The new robust regex to handle various date/time/title formats
DATE_TIME_TITLE_REGEX = r"(\d{2}[-./]\d{2}[-./]\d{4})(?:(?:\s+)(\d{1,2}\s+\d{1,2}))?(?:(?:\s+)(.*))?\.md$"

def parse_obsidian_file(filepath):
    filename = os.path.basename(filepath)

    match = re.search(DATE_TIME_TITLE_REGEX, filename)

    date = None
    time_part = None
    title = None

    if match:
        date = match.group(1)
        time_part = match.group(2) # e.g., '1 49' or None
        raw_title = match.group(3)

        # Since the time part is a structured group, we should only set 'title' if Group 3 (raw_title) is present.
        if raw_title is not None:
            # Clean up the title by replacing spaces or underscores
            title = raw_title.strip().replace("_", " ")


    # Read the file
    with open(filepath, 'r') as file:
        content = file.read()

    # Extract frontmatter (YAML style metadata block
    metadata = {}
    body = content
    if content.startswith("---"):
        try:
            frontmatter, body = content.split('---', 2)[1:]
            for line in frontmatter.splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
        except ValueError:
             # Handle case where frontmatter starts but doesn't close correctly
             body = content

    metadata['filename'] = filename
    metadata['date'] = date
    metadata['title'] = title
    metadata['content'] = body.strip()
    metadata['time_part'] = time_part

    return metadata

def iterate_files(folder_path):
    data = []
    # Ensure folder_path exists before trying to list contents
    if not os.path.isdir(folder_path):
        print(f"Error: Folder path does not exist: {folder_path}")
        return pd.DataFrame()

    for file in os.listdir(folder_path):
        if file.endswith('.md'):
            filepath = os.path.join(folder_path, file)
            metadata = parse_obsidian_file(filepath)
            data.append(metadata)
    df = pd.DataFrame(data)
    reduced = df[df['content'] != ""] # filter out the empty entries
    return reduced
