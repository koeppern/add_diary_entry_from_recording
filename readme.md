# Adding audio notes as text to a markdown dictionary
2023-05-22, J. Köppern with support from GPT-4

My daily notes look like
```
# Notes

## 2023-05-21
- I did this.
- I did that.

## 2023-05-22
- I did this.
- I did that.
```
I want to be able to edit the Markdown file on my PC as well as to be able to add a single note (single bullet point) via an audio recording I create on my smartphone. If I start the script in this repository all texts in all new recordings shall be extracted, translated to English (if they are in a different language) and be inserted at the correct position in the Markdown file.

## Overview

This is the main part of thescript:
``` python
config = configparser.ConfigParser()

config.read(config_filename)

open_ai_key = config['DEFAULT']['OPENAI_API_KEY']

df = load_md_file_into_df(filename, pd.DataFrame())

df_with_audio = add_audios_to_df(df, folder_audio, open_ai_key)

write_df_to_md_file(filename_out, df_with_audio)

shutil.copyfile(filename_out, filename)
```
It 
1. load my `OpenAI` API key from a non-versioned config file, 
2. parsed the existing diary file ino a Pandas data frame, 
2. extract/translates all text from the previously unseen recordings using *Whisper API* and add the to the data frame as well and
4. overwrites the ‘diary.md’ with the data in the data frame.

## The steps in detail

### Load API key from config.ini

The file ` config.ini` looks like:
```
[DEFAULT]
 OPENAI_API_KEY = sk-5IMfN______________________SY3Pkm8N3SLoWt
```
It’s read by
``` python
import configparser


config = configparser.ConfigParser()

config.read(config_filename)

open_ai_key = config['DEFAULT']['OPENAI_API_KEY']

```
like shown above.

### Load MD file into data frame

The script continues with
``` python
df = load_md_file_into_df(filename, pd.DataFrame())
```
calling the function
``` python
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

```

First, let's break down the function itself. The function is called "load_md_file_into_df" and takes two arguments: "filename" and "df". The "filename" argument is the name of the markdown file that you want to read in, and the "df" argument is a pandas dataframe that will be used to store the dictionary entries.

The function starts by opening the markdown file using the "open" function and reading in the contents using the "read" method. It then splits the text into individual lines using the "split" method and loops through each line.

For each line, the function checks if it starts with "## " or "- ". If it starts with "## ", it assumes that this is a new date and sets the "this_date" variable to the date string. If it starts with "- ", it assumes that this is a new dictionary entry and sets the "this_text" variable to the text string.

The function then calls another function called "add_new_row_to_df" to add the new dictionary entry to the dataframe. This function takes three arguments: the dataframe, the date string, and the text string. It creates a new row in the dataframe with the date and text strings as the values.

Finally, the function returns the updated dataframe.


### Recognize text in audio files

OpenAI's [Whisper](https://openai.com/research/whisper) is used to extract and translate text from MP3 files. The function
``` python
df_with_audio = add_audios_to_df(df, folder_audio, open_ai_key)
```
adds the text to a Pandas data frame:
``` python
def add_audios_to_df(df, folder_audio, open_ai_key):
    openai.api_key = open_ai_key
    
    # Load the list from the file if it exists
    if os.path.isfile('scanned_files.txt'):
        try:
            with open('scanned_files.txt', 'r') as file:
                scanned_files = file.read().splitlines()

                print(f"Loaded list of of already scanned audio files:\n{scanned_files}")
        except:
            scanned_files = []
    
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
                            
                            print(result)

                            print(f"Apply Whisper to {audio_file}.")

                            scanned_files.append(audio_file)

                            df = add_new_row_to_df(df, date, result)
                except:
                    result = ""

                    

    # Write the list to the file
    try:
        with open('scanned_files.txt', 'w') as file:
            file.write('\n'.join(scanned_files))
    except:
        print("Error while saving list of processed audio files.")

    return df
```

The function takes in three parameters: df, which is a pandas DataFrame, folder_audio, which is a string representing the path to the folder containing the audio files, and open_ai_key, which is a string representing the OpenAI API key.

The function first sets the OpenAI API key using the openai.api_key variable. It then checks if a file called scanned_files.txt exists in the current directory. If it does, the function reads the contents of the file into a list called scanned_files. If it doesn't exist, the function initializes an empty list called scanned_files.

The function then loops through all the files in the folder_audio directory and checks if the file has a .mp3 extension. If it does, the function extracts the date from the file name using regular expressions and reads the audio file into a file object. If the audio file has not already been scanned (i.e., its path is not in the scanned_files list), the function passes the file object to the OpenAI API's Audio.translate method to transcribe the audio file. The resulting transcription is added to the df DataFrame using the add_new_row_to_df function (not shown in this code snippet).

Finally, the function writes the scanned_files list to the scanned_files.txt file and returns the updated df DataFrame.



### Write diary MD file

``` python
write_df_to_md_file(filename_out, df_with_audio)
```
stores the content of my diary data fame `df` as a markdownfile in the format I denfied. For that the function
``` python
def write_df_to_md_file(filename_out, df):
    df_for_output = df
    df_for_output["date"] = pd.to_datetime(df["date"])

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
```
is used: The function takes two arguments: "filename_out" and "df". The "filename_out" argument is the name of the markdown file that you want to write the dataframe to, and the "df" argument is the pandas dataframe that contains the dictionary entries.

The function starts by grouping the dataframe by the "date" column using the "groupby" method. It then applies a lambda function to each group that concatenates the "text" column for each row with a dash ("-") and a newline character ("\n"). This creates a string of all the dictionary entries for each date.

The resulting "dates_texts" variable is a dataframe with two columns: "date" and "0". The "date" column contains the date strings and the "0" column contains the concatenated dictionary entries for each date.

The function then converts the "date" column to a datetime type using the "pd.to_datetime" method. This allows the dates to be sorted in chronological order.

The "dates_texts" dataframe is then sorted by the "date" column in ascending order using the "sort_values" method.

The "date" column is then converted back to a string format using the "dt.strftime" method.

The "texts_out" variable is then created by concatenating the date strings and dictionary entries using the "join" method. The resulting string is formatted with headers and newlines to create a markdown file.

Finally, the markdown file is written to disk using the "open" function and the "write" method.


## Recording on my smartphone

I use [Easy Voice Recorder]() on my Android smartphone to record the audio file. The apps automatically names the filies in the fomat*YYYY-MM-DD-HH-MM.mp3*, for example *2023-05-22-16-55.mp3*. The rexcordings are synced with my *Google Drive* account so this script can also access them after they were synced with my Windows PC.

