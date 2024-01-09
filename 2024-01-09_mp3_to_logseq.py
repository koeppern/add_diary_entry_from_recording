print  # 2024-01-09_mp3_to_logseq.py
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


def extract_text_from_audios(client, df_audio, play_audio=False):
    df_audio.reset_index(drop=True, inplace=True)

    df_audio_not_extracted = df_audio[df_audio["did_extraction"] == False]

    for index, row in df_audio_not_extracted.iterrows():
        audio_file = row["audio_file"]

        date = row["date"]

        try:
            result = ""

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
                df_audio.loc[index, "written_to_df"] = False
                df_audio.loc[index, "did_extraction"] = True
        except:
            result = ""


def add_item_to_audio_section(filename_journal, new_item, print_new_content=False):
    try:
        with open(filename_journal, "r", encoding="utf-8") as file:
            content = file.read()
    except:
        content = ""

    # extract section - Audio notes from content
    # Pattern to extract content starting with '- # Voice recording' and ending at the next header or end of content
    audio_pattern = r"^- # Voice recording$(.*?)(?=^- # |\Z)"
    content_audio = re.search(audio_pattern, content, re.MULTILINE | re.DOTALL)

    if content_audio:
        content_audio = content_audio.group(0)
    else:
        content_audio = r"\t- # Voice recording"

    # Content without audio part
    content_wo_audio = re.sub(
        audio_pattern, "", content, flags=re.MULTILINE | re.DOTALL
    )

    # Find all elements underneath # Voice recording
    # Regular expression pattern to match entries following '- '
    entry_pattern = r"(?m)^\s*- (.*?)(?=\n\s*- |\Z)"

    # drop first row containing '- # Voice recording' from content_audio
    content_audio = re.sub(r"^- # Voice recording", "", content_audio)

    # if content_wo_audio only contains one ore more \n, set content_wo_audio to empty string
    if re.match(r"^\n+$", content_wo_audio):
        content_wo_audio = ""

    # Finding all matches
    audio_entries = re.findall(entry_pattern, content_audio, re.DOTALL)

    # Add header to otherwise empty content_audio
    content_audio = r"- # Voice recording"

    if new_item not in audio_entries:
        audio_entries.append(new_item)

    # remove duplicates in audio_entries
    audio_entries = list(dict.fromkeys(audio_entries))

    for entry in audio_entries:
        content_audio += f"\n\t- {entry}"

    # add \n to content_wo_audio if it doesn't end with \n
    if not content_wo_audio.endswith("\n"):
        if len(content_wo_audio) > 0:
            content_wo_audio += "\n"

    print("---", content_wo_audio, content_audio)

    updated_content = content_wo_audio + content_audio

    with open(filename_journal, "w", encoding="utf-8") as file:
        file.write(updated_content)

    if print_new_content:
        print("Hola")
        print(updated_content)


# -------------------------------------------------------
## App
# -------------------------------------------------------
client = init_openai()

df_audio = load_and_update_df_audio(parameters)

extract_text_from_audios(client, df_audio)

# Write items to journal files ------------------------------------------------------------------
# Loop over the rows of df_audio where did_extraction is True and written_to_df is False
if "written_to_df" not in df_audio.columns:
    df_audio["written_to_df"] = False

df_audio_to_write = df_audio[
    (df_audio["did_extraction"] == True) & (df_audio["written_to_df"] == False)
]

for index, row in df_audio_to_write.iterrows():
    this_date = row["date"]

    this_text = row["text"]

    this_filename_journal = (
        r"C:\documents\johannes_notes\logseq\journals\\" + this_date + ".md"
    )

    add_item_to_audio_section(this_filename_journal, this_text, print_new_content=False)

    df_audio.loc[index, "written_to_df"] = True

df_audio["written_to_df"] = False
save_df_audio_to_file(parameters, df_audio)
