#!/usr/bin/env python3
import os
from collections import defaultdict
from rich.table import Table
from rich.console import Console
from itertools import groupby
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import csv
ps = PorterStemmer()

VIDEO_FOLDER = "videos/"
DIGITS = "1234567890"



def normalise(filepath: str, stem=False) -> str:
    clean_filepath = filepath.lstrip(DIGITS)[:-4]
    if stem:
        clean_filepath = clean_filepath.lower().replace("tiktok", "tik tok")
        words = word_tokenize(clean_filepath)
        stemmed = " ".join(ps.stem(w) for w in words)
        return stemmed
    else:
        return clean_filepath



# return dict, stem : number of stem appearances
def numbers_table(file_list: list[str], stem: bool) -> dict[str, int]:
    clean_files = sorted(normalise(file, stem) for file in file_list)
    table = {group_key : len(list(group_values)) for group_key, group_values in groupby(clean_files)}
    return table


# return dict, video name : number of VIDEO NAME appearances
def video_name_stem(file_list: list[str]) -> dict[str, str]:
    return {normalise(file, stem=False) : normalise(file, stem=True) for file in file_list}

    
def main() -> None:
    file_list = os.listdir(VIDEO_FOLDER)
    
    
    
    stem_numbers = numbers_table(file_list, stem=True)
    fname_numbers = numbers_table(file_list, stem=False)
    stem_to_fnames = {
        group_key: list(row[1] for row in group_rows)
        for group_key, group_rows in groupby(sorted(
            (stem, fname)
            for fname, stem in video_name_stem(file_list).items()
        ), key=lambda item: item[0])
    }    
    console = Console()
    console_table = Table(title="Ssniperwolf duplicate video names")
    console_table.add_column("Stem Name")
    console_table.add_column("Video Name")
    console_table.add_column("Number of times repeated")
    
    with open("duplicate_videonames.csv","w",newline="") as csvfile:
        csv_writer = csv.writer(csvfile , quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["Stem Name", "Video Name", "Number of times repeated"])
        for stem, stem_num in sorted(stem_numbers.items(), key=lambda x: -x[1]):
            console_table.add_row(stem, "", str(stem_num))
            csv_writer.writerow([stem, "", stem_num])
            for vid in stem_to_fnames[stem]:
                console_table.add_row("", vid, f"  {fname_numbers[vid]}")
                csv_writer.writerow(["", vid, fname_numbers[vid]])
            console_table.add_row("", "", "")
            csv_writer.writerow(["","",""])
    
    console.print(console_table)
    

if __name__ == "__main__":
    main()