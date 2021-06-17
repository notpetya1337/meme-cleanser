# Meme Cleanser

Takes whatever is in your clipboard and attempts to first convert it into an image. Currently supports images and URLs to images.
The image is then cleansed of heresy and returned to the clipboard.

# Cleansing steps

- Size limiters like `width=420&height=690` in URLs are discarded.
- If the URL is a discord thumnail url, the original address is queried. If that fails, the thumbnail url is used.
- The bottom-most image segment is removed if it looks like a watermark.

# Notes:

- It is assumed that a watermark with a dark background exists.
  If it doesn't or if there is no clear seperation between the watermark and the image, parts of the image proper may be cut off.
