# 2023-05-21, J. Köppern
# %%

import pandas as pd
import os


filename = "G:\Meine Ablage\johannes_notes\diary_johannes_koeppern.md"

filename_out = "out.md"


df = pd.DataFrame()

with open(filename, "r") as file:
    text_in = file.read()

lines = text_in.split("\n")

for line in lines:
    line = line.strip()

    if line.startswith("## "):
            this_date = line[3:]
    elif line.startswith("- "):
        this_text = line[2:].lstrip(" ")


        new_row = pd.DataFrame({"date": [this_date], "text": [this_text]})

        df = pd.concat([df, new_row], ignore_index=True)

dates_texts = df.groupby("date").apply(lambda x: "\n".join("- " + row["text"] for _, row in x.iterrows()) + "\n").reset_index()
dates_texts["date"] = pd.to_datetime(dates_texts["date"])  # Convert date column to datetime type
dates_texts = dates_texts.sort_values("date")  # Sort by date column in ascending order
dates_texts["date"] = dates_texts["date"].dt.strftime("%Y-%m-%d")  # Convert date column back to string format

texts_out = "# Diary\n\n" + "\n".join(["## " + row["date"] + "\n" + row[0] for _, row in dates_texts.iterrows()])

with open(filename_out, "w") as file:
    file.write(texts_out)










# %%
