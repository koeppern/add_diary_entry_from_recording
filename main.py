# 2023-05-21, J. Köppern
# %%

import pandas as pd
import os
import re
import openai
import configparser
import shutil
import subprocess
import getpass




# Parameters
git_folder_path = "G://Meine Ablage//johannes_notes"
# config_filename = "cofig.ini"
config_filename = "C:\config\cofig.ini"

filename = "G:\Meine Ablage\johannes_notes\diary_johannes_koeppern.md"

filename_out = "out.md"

folder_audio = "G:\Meine Ablage\Easy Voice Recorder"

open_ai_key = os.environ.get("OPENAI_API_KEY")

# Funcitons
def add_audios_to_df(folder_audio, open_ai_key, df=pd.DataFrame):
    openai.api_key = open_ai_key
    
    # Load the list from the file if it exists
    if os.path.isfile('scanned_files.txt'):
        try:
            with open('scanned_files.txt', 'r', encoding='utf-8') as file:
                scanned_files = file.read().splitlines()

                # print(f"Loaded list of of already scanned audio files:\n{scanned_files}")
        except:
            scanned_files = []
    
    else:
        scanned_files = []


    # Loop through the files in the folder
    for filename in os.listdir(folder_audio):
        if filename.endswith(".mp3"):
            # Extract the date from the file name using regular expressions
            match = re.search(r"\d{4}-\d{2}-\d{2}", filename)
            if match:
                date = match.group()
                #print(date)
                audio_file = folder_audio + "\\" + filename

                try:
                    with open(audio_file, "rb") as f:
                        # Pass the file object to the transcribe method
                        if audio_file not in scanned_files:
                            result = openai.Audio.translate(
                                model = "whisper-1", 
                                language="en",
                                response_format="text",
                                file=f)
                            
                            audio_file_replace = (audio_file.
                                                  strip().
                                                  replace("\\", "/").
                                                  replace(" ", "%20").
                                                  rstrip("\n").rstrip("\r\n").
                                                  replace("\n", ""))
                            
                            result = result.strip() + f", [{filename}](file://{audio_file_replace})"

                

                            result = result.strip()
                            
                            #print(result)

                            print(f"Apply Whisper to {audio_file}.")

                            scanned_files.append(audio_file)

                            df = add_new_row_to_df(df, date, result)
                except:
                    result = ""

                    

    # Write the list to the file
    try:
        with open('scanned_files.txt', 'w', encoding='utf-8') as file:
            file.write('\n'.join(scanned_files))
    except:
        print("Error while saving list of processed audio files.")

    return df

def add_new_row_to_df(df, this_date, this_text):
    new_row = pd.DataFrame({"date": [this_date], "text": [this_text]})

    df = pd.concat([df, new_row], ignore_index=True)
    return df

def write_df_to_md_file(filename_out, df):
    df_for_output = df.drop_duplicates()
    df_for_output.loc[:, "date"] = pd.to_datetime(df["date"])

    df_for_output_sorted = df_for_output.sort_values("date")  # Sort by date column in ascending order
    df_for_output_sorted.date = df_for_output_sorted["date"].dt.strftime("%Y-%m-%d")  # Convert date column back to string format
    df_for_output_sorted.text = [text.rstrip('\n') for text in df_for_output_sorted.text]

    texts_out = "# Diary\n\n"#

    for date, group in df_for_output_sorted.groupby("date"):
        texts_out += f"## {date}\n"
        for value in group.text:
            value = value.lstrip('\t ')  # Remove leading tabs and spaces

            texts_out += "- " + value + "\n"
        texts_out += "\n\n"


    with open(filename_out, "w", newline='\n', encoding='utf-8') as file:
        file.write(texts_out)

def load_md_file_into_df(filename, df=pd.DataFrame()):
    with open(filename, "r", encoding="utf-8") as file:
        text_in = file.read()

    lines = text_in.split("\n")

    for line in lines:
        line = line.strip()

        if line.startswith("## "):
                this_date = line[3:]
        elif line.startswith("- "):
            this_text = line[2:].lstrip(" ")


            df = add_new_row_to_df(df, this_date, this_text)

    return df

def load_api_key(config_filename):
    config = configparser.ConfigParser()

    config.read(config_filename)

    open_ai_key = config['DEFAULT']['OPENAI_API_KEY']
    
    return open_ai_key

def git_commit(git_folder_path, commit_message = "diary_whisper", debug=False):
    

    print(f"Current working directory: {os.getcwd()}")
    print(f"Git folder path: {git_folder_path}")

    # Commit the changes with the specified message
    try:
        subprocess.run(["git", "add", "-A"], check=True, cwd=git_folder_path)

        

        commit_process = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)
        if debug:
            print(f"Git commit output: {commit_process.stdout}")
            print(f"Git commit error: {commit_process.stderr}")
            print(f"Git commit exit code: {commit_process.returncode}")
    except subprocess.CalledProcessError as e:
        # Add debug information
        print(f"Git commit failed. Error message: {e.stderr}")




# Main script
os.chdir(git_folder_path)

open_ai_key = load_api_key(config_filename)

df = load_md_file_into_df(filename)

df_with_audio = add_audios_to_df(folder_audio, open_ai_key, df)

write_df_to_md_file(filename_out, df_with_audio)

shutil.copyfile(filename_out, filename)

git_commit(git_folder_path)
# %%
