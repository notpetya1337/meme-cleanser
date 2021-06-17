import os
import re

from PIL import Image
from pathlib import Path
import pyperclip
import requests

from PIL import ImageGrab
import win32clipboard as winclip
import win32con
from io import BytesIO

def colordiff(color1, color2):
    return [c1 - c2 for c1, c2 in zip(color1, color2)]

def abscolordiff(color1, color2):
    return sum(map(abs, colordiff(color1, color2)))

# removes the bottom most bar/banner from the image if it's dark enough
# I have yet to encounter a light watermark bar
def removeWatermarks(img):

    compimg = img.convert("RGBA")

    x = compimg.size[0] * 0
    y = compimg.size[1] - 1
    print(f"Image height: {y}")

    # find bottom-most bar
    colorInitial = compimg.getpixel((x,y))[:3]
    while y >= compimg.size[1] * 0.5:
        color = compimg.getpixel((x,y))[:3]
        print(color)
        # color change -> end of bottom bar
        if abscolordiff(color, colorInitial) > 30:
            break
        # probably doesn't look like a watermark bar
        if sum(color) > 150:
            break
        y -= 1
    print(y)

    newSize = [0,0] + list(img.size)
    newSize[3] = y + 1 # + 1 because we go from index to size
    print(f"Image height reduced by {img.size[1] - newSize[3]} pixels")
    return img.crop(newSize)

def getImageFromText():
    url = pyperclip.paste()
    if len(url) == 0:
        return None

    # remove size restrictions
    url = re.sub(r"\??(&?(width|height|size)=[-_a-zA-Z0-9]*)", "", url)

    # remove discord shit (if possible, the original might not exist anymore)
    if match := re.match(r".*images-ext-[a-zA-Z0-9].discordapp.net/external/.*/(https?/.*)", url):
        newurl = match.group(1)
        newurl = newurl.replace("/", "://", 1)
        response = requests.get(newurl, stream=True)
        if response.ok:
            response.raw.decode_content = True # handle spurious Content-Encoding
            img = Image.open(response.raw)
            return img

    # just fetch the url
    response = requests.get(url, stream=True)
    if response.ok:
        response.raw.decode_content = True # handle spurious Content-Encoding
        img = Image.open(response.raw)
        return img

    print("Failed to get image from url")

def main():
    # TODO: find better solution for clipboard handling

    img = getImageFromText()

    tempfilepath = Path("./tmp/clip.png")
    if not img:
        # load image directly from clipboard
        grabimg = ImageGrab.grabclipboard()
        grabimg.save(tempfilepath, 'png')
        print(tempfilepath.stat().st_size)
        if tempfilepath.stat().st_size > 0:
            img = Image.open("./tmp/clip.png")

    if not img:
        print("No image found, aborting :(")
        return

    # actually do the thing
    img = removeWatermarks(img)

    # put image back into clipboard
    img.save("./tmp/clip.png")
    output = BytesIO()
    img.convert('RGB').save(output, 'BMP')
    clipdata = output.getvalue()[14:]
    output.close()
    winclip.OpenClipboard()
    winclip.EmptyClipboard()
    winclip.SetClipboardData(win32con.CF_DIB, clipdata)
    winclip.CloseClipboard()
    img.show()

if __name__ == "__main__":
    main()
