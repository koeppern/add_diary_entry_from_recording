# TITLE

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

### Recognize text in audio files

### Write diary MD file

## Recording on my smartphone


