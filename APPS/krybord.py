from PIL import Image, ImageDraw

# Create a blank image with a white background
width, height = 800, 600
background_color = (255, 255, 255)
image = Image.new("RGB", (width, height), background_color)
draw = ImageDraw.Draw(image)

# Define snake body colors
body_colors = [(0, 0, 0), (50, 50, 50), (30, 30, 30)]

# Draw the snake body
num_segments = 20
segment_length = 25
for i in range(num_segments):
    x1 = 400 - segment_length * i
    x2 = x1 - segment_length
    y = 300
    color = body_colors[i % len(body_colors)]
    draw.line([(x1, y), (x2, y)], fill=color, width=15)

# Draw the snake head
head_center = (x1 - segment_length, y)
head_radius = 25
draw.ellipse([(head_center[0] - head_radius, head_center[1] - head_radius),
              (head_center[0] + head_radius, head_center[1] + head_radius)],
             fill=(0, 0, 0))

# Save the image
image.save("realistic_snake.png")
image.show()
