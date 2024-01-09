# 2024-01-09_mp3_to_logseq.py
# 2024-01-09
# This script works with a dataframe (from and to CSV) containing all MP3s in a folder
# younger then a date. If the column did_extraction indicates that the text wasn't recognized yet
# OpenAI whisper is used for text extraction and translation. The result is stored in the dataframe.
# Then, the notes from the MP3s (now in the df) are added to md journal files for the date of the note.
# The date of the note is part of the resp. filename
import pandas as pd
import os
import re
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv


# -------------------------------------------------------
## Parameters
# -------------------------------------------------------
parameters = {
    "folder_audio": "G:\Meine Ablage\Easy Voice Recorder",
    "start_date": "2024-01-01",
    "filename_df_audio": "df_audio.csv",
}


# -------------------------------------------------------
## Functions
# -------------------------------------------------------
# Function to load and update df_audio with filenames from the folder
def load_and_update_df_audio(parameters):
    try:
        df_audio = pd.read_csv(parameters["filename_df_audio"], encoding="utf-8")
    except:
        df_audio = pd.DataFrame(
            columns=["date", "audio_file", "did_extraction", "text"]
        )

    # Loop through the files in the folder and update df_audio with filenames
    for filename in os.listdir(parameters["folder_audio"]):
        if filename.endswith(".mp3"):
            # Extract the date from the file name using regular expressions
            match = re.search(r"\d{4}-\d{2}-\d{2}", filename)
            if match:
                date = match.group()

                audio_file = parameters["folder_audio"] + "\\" + filename

                # Test if audio_file is in df_audio["audio_file"]
                if audio_file in df_audio["audio_file"].values:
                    continue
                else:
                    if date > parameters["start_date"]:
                        this_text = ""
                        this_did_extraction = False

                        this_file = pd.DataFrame(
                            {
                                "date": date,
                                "audio_file": audio_file,
                                "did_extraction": this_did_extraction,
                                "text": this_text,
                            },
                            index=[0],
                        )

                        df_audio = pd.concat([df_audio, this_file])
    return df_audio


# stroe df_audio as utf-8 encoded csv without index
def save_df_audio_to_file(parameters, df_audio):
    df_audio.to_csv(parameters["filename_df_audio"], index=False, encoding="utf-8")


def init_openai():
    load_dotenv(find_dotenv())

    api_key = os.environ.get("OPENAI_API_KEY")

    return OpenAI(api_key=api_key)


def extract_text_from_audios(client, df_audio):
    df_audio_not_extracted = df_audio[df_audio["did_extraction"] == False]

    for index, row in df_audio_not_extracted.iterrows():
        audio_file = row["audio_file"]
        date = row["date"]

        try:
            with open(audio_file, "rb") as f:
                # Pass the file object to the transcribe method
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    language="en",
                    response_format="text",
                    file=f,
                )

                audio_file_replace = (
                    audio_file.strip()
                    .replace("\\", "/")
                    .replace(" ", "%20")
                    .rstrip("\n")
                    .rstrip("\r\n")
                    .replace("\n", "")
                )

                result = (
                    result.strip() + f", [{audio_file}](file://{audio_file_replace})"
                )

                result = result.strip()

                print(f"Apply Whisper to {audio_file}.")

                df_audio.loc[index, "text"] = result
                df_audio.loc[index, "did_extraction"] = True
        except:
            result = ""


# -------------------------------------------------------
## App
# -------------------------------------------------------
client = init_openai()

df_audio = load_and_update_df_audio(parameters)

extract_text_from_audios(client, df_audio)

save_df_audio_to_file(parameters, df_audio)


# MD ------------------------------------------------------------------
filename_journal = r"C:\documents\johannes_notes\logseq\journals\2023_11_12.md"

nnew_item = "Pferd"


def add_item_to_audio_section(filename_journal, new_item, print_new_content=False):
    with open(filename_journal, "r", encoding="utf-8") as file:
        content = file.read()

    # extract section - Audio notes from content
    # Pattern to extract content starting with '- # Voice recording' and ending at the next header or end of content
    audio_pattern = r"^- # Voice recording$(.*?)(?=^- # |\Z)"
    content_audio = re.search(audio_pattern, content, re.MULTILINE | re.DOTALL)

    if content_audio:
        content_audio = content_audio.group(0)
    else:
        content_audio = ""

    # Content without audio part
    content_wo_audio = re.sub(
        audio_pattern, "", content, flags=re.MULTILINE | re.DOTALL
    )

    # Find all elements underneath # Voice recording
    # Regular expression pattern to match entries following '- '
    entry_pattern = r"(?m)^\s*- (.*?)(?=\n\s*- |\Z)"

    # Finding all matches
    audio_entries = re.findall(entry_pattern, content_audio, re.DOTALL)

    # Add header to otherwise empty content_audio
    content_audio = audio_entries[0]

    if new_item not in audio_entries:
        audio_entries.append(new_item)

    for entry in audio_entries[1:]:
        content_audio += f"\n\t- {entry}"

    updated_content = content_wo_audio + "\n\n" + content_audio

    with open(filename_journal, "w", encoding="utf-8") as file:
        file.write(updated_content)

    if print_new_content:
        print(content_audio)


add_item_to_audio_section(filename_journal, nnew_item, print_new_content=True)
