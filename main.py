from pytubefix import YouTube
import re
from datetime import datetime

url = "paste youtube link here"

video = YouTube(url)
# Required to be able to access the description
video.streams.first()

description_list = video.description.split("\n")

for i, line in enumerate(description_list):
    if ("0:00" in line):
        description_list = description_list[i:]
        break

timecode_regex = "[0-9]*:?[0-9]+:[0-9]+"
chapters_timecodes = {}
for i, line in enumerate(description_list):
    timecode = re.findall(timecode_regex, line)[0]
    timecode_len = len(timecode)
    if (timecode_len == 4):
        timecode = "0:0" + timecode
    if (timecode_len == 5):
        timecode = "0:" + timecode


    title = re.sub(timecode_regex + " ", '', line)
    chapters_timecodes[timecode] = title

caption = video.captions["a.en"]

srt_captions = caption.generate_srt_captions()
srt_captions_list = srt_captions.split("\n")

srt_captions_cleaned = []
for element in srt_captions_list:
    if re.search("^\\d{1,4}$", element) :
        continue

    regex_results = re.findall(timecode_regex, element)

    if len(regex_results) != 0:
        srt_captions_cleaned.append(regex_results[0])
        continue

    if element == "":
        continue

    srt_captions_cleaned.append(element)

transcript = {srt_captions_cleaned[i]: srt_captions_cleaned[i + 1] for i in range(0, len(srt_captions_cleaned), 2)}

chapters_keys = [key for key, _ in chapters_timecodes.items()]
sections = [[] for _ in range(len(chapters_keys))]

chapters_keys_index = 1
for key, text in transcript.items():
    if chapters_keys_index > len(chapters_keys) - 1:
        sections[-1].append(text)
        continue

    transcript_time = datetime.strptime(key, '%H:%M:%S')
    chapter_time = datetime.strptime(chapters_keys[chapters_keys_index], '%H:%M:%S')
    
    if transcript_time < chapter_time:
        sections[chapters_keys_index - 1].append(text)
    elif transcript_time > chapter_time:
        chapters_keys_index += 1
        sections[chapters_keys_index - 1].append(text)

def divide_chunks(l, n): 
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

print("Writing article based on YouTube video")
with open("article.md", "w") as file:
    print("Writing in progress...")
    for i, section in enumerate(sections):
        title = "# " + chapters_timecodes[chapters_keys[i]] + "\n"
        chunks = divide_chunks(section, 15)

        file.write(title)
        file.write("\n")
        for chunk in chunks:
            file.write(''.join(chunk))
            file.write("\n")
            file.write("\n")
    print("Done!")


