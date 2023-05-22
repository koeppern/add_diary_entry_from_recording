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

### Write diary MD file

## Recording on my smartphone


