# 2023-05-21, J. Köppern
# %%

import pandas as pd
import os
import re
import openai
import configparser
import shutil



# Parameters
config_filename = "cofig.ini"

filename = "G:\Meine Ablage\johannes_notes\diary_johannes_koeppern.md"

filename_out = "out.md"

folder_audio = "G:\Meine Ablage\Easy Voice Recorder"

open_ai_key = os.environ.get("OPENAI_API_KEY")

# Funcitons
def add_audios_to_df(df, folder_audio, open_ai_key):
    openai.api_key = open_ai_key
    
    # Load the list from the file if it exists
    if os.path.isfile('scanned_files.txt'):
        with open('scanned_files.txt', 'r') as file:
            scanned_files = file.read().splitlines()
    else:
        scanned_files = []

    print(scanned_files)

    # Loop through the files in the folder
    for filename in os.listdir(folder_audio):
        if filename.endswith(".mp3"):
            # Extract the date from the file name using regular expressions
            match = re.search(r"\d{4}-\d{2}-\d{2}", filename)
            if match:
                date = match.group()
                print(date)
                audio_file = folder_audio + "\\" + filename

                with open(audio_file, "rb") as f:
                    # Pass the file object to the transcribe method
                    if audio_file not in scanned_files:
                        result = openai.Audio.translate(
                            model = "whisper-1", 
                            language="en",
                            response_format="text",
                            file=f)

                        print(result)

                        print(f"Apply Whisper to {audio_file}.")

                        scanned_files.append(audio_file)

                        df = add_new_ro_to_df(df, date, result)

    # Write the list to the file
    with open('scanned_files.txt', 'w') as file:
        file.write('\n'.join(scanned_files))

    return df

def add_new_ro_to_df(df, this_date, this_text):
    new_row = pd.DataFrame({"date": [this_date], "text": [this_text]})

    df = pd.concat([df, new_row], ignore_index=True)
    return df

def write_df_to_md_file(filename_out, df):
    dates_texts = df.groupby("date").apply(lambda x: "\n".join("- " + row["text"] for _, row in x.iterrows()) + "\n").reset_index()
    dates_texts["date"] = pd.to_datetime(dates_texts["date"])  # Convert date column to datetime type
    dates_texts = dates_texts.sort_values("date")  # Sort by date column in ascending order
    dates_texts["date"] = dates_texts["date"].dt.strftime("%Y-%m-%d")  # Convert date column back to string format

    texts_out = "# Diary\n\n" + "\n".join(["## " + row["date"] + "\n" + row[0] for _, row in dates_texts.iterrows()])

    with open(filename_out, "w") as file:
        file.write(texts_out)

def load_md_file_into_df(filename, df):
    with open(filename, "r") as file:
        text_in = file.read()

    lines = text_in.split("\n")

    for line in lines:
        line = line.strip()

        if line.startswith("## "):
                this_date = line[3:]
        elif line.startswith("- "):
            this_text = line[2:].lstrip(" ")


            df = add_new_ro_to_df(df, this_date, this_text)

    return df



# Main script
config = configparser.ConfigParser()

config.read(config_filename)

open_ai_key = config['DEFAULT']['OPENAI_API_KEY']


df = load_md_file_into_df(filename, pd.DataFrame())

df_with_audio = add_audios_to_df(df, folder_audio, open_ai_key)

write_df_to_md_file(filename_out, df_with_audio)

shutil.copyfile(filename_out, filename)
# %%
