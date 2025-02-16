from PIL import Image, ImageDraw

# Create a 256x256 image with transparent background
size = 256
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Colors
blue = "#4B8BBE"  # Child-friendly blue
yellow = "#FFD43B"  # Warm yellow
white = "#FFFFFF"
red = "#FF6B6B"  # Soft red

# Draw a ruler/height measure
ruler_width = 40
ruler_x = size * 0.7
ruler_height = size * 0.8
ruler_y = size * 0.1

# Draw ruler base
draw.rectangle(
    [(ruler_x, ruler_y), (ruler_x + ruler_width, ruler_y + ruler_height)],
    fill=blue
)

# Draw measurement lines
for i in range(10):
    y = ruler_y + (ruler_height * i / 9)
    line_length = 20 if i % 3 == 0 else 10
    draw.line(
        [(ruler_x, y), (ruler_x + line_length, y)],
        fill=white,
        width=3
    )

# Draw a simple child figure
# Head
head_x = size * 0.3
head_y = size * 0.2
head_size = size * 0.2
draw.ellipse(
    [(head_x, head_y), (head_x + head_size, head_y + head_size)],
    fill=yellow
)

# Body
body_width = head_size * 0.6
body_height = head_size * 1.5
draw.rectangle(
    [(head_x + head_size/2 - body_width/2, head_y + head_size),
     (head_x + head_size/2 + body_width/2, head_y + head_size + body_height)],
    fill=red
)

# Save as ICO file
img.save('app_icon.ico', format='ICO', sizes=[(256, 256)]) 