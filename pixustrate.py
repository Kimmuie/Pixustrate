from PIL import Image

# Map of 8-dot Braille characters
def get_braille_char(block):
    dots = [
        (0, 0),  # dot 1
        (0, 1),  # dot 2
        (0, 2),  # dot 3
        (1, 0),  # dot 4
        (1, 1),  # dot 5
        (1, 2),  # dot 6
        (0, 3),  # dot 7
        (1, 3),  # dot 8
    ]
    value = 0
    brightness * 2
    threshold = brightness  # brightness threshold

    for i, (x, y) in enumerate(dots):
        if y < len(block) and x < len(block[0]):
            if block[y][x] < threshold:
                value |= (1 << i)
    
    return chr(0x2800 + value)

def image_to_braille(image_path, max_width=100):
    img = Image.open(image_path).convert('L')  # grayscale
    width, height = img.size

    # Resize for terminal width
    aspect_ratio = height / width
    new_width = min(max_width, width)
    new_height = int(aspect_ratio * new_width)
    img = img.resize((new_width, new_height))

    pixels = img.load()

    braille_lines = []
    for y in range(0, img.height, 4):
        line = ''
        for x in range(0, img.width, 2):
            block = []
            for dy in range(4):
                row = []
                for dx in range(2):
                    px = x + dx
                    py = y + dy
                    if px < img.width and py < img.height:
                        row.append(pixels[px, py])
                    else:
                        row.append(255)  # white
                block.append(row)
            line += get_braille_char(block)
        braille_lines.append(line)

    return "\n".join(braille_lines)

# === Main Program ===
if __name__ == "__main__":
    brightness = int(input("Input the brightness between 0-100: "))
    image_path = input("Input the words for creating image: ")
    try:
        braille_art = image_to_braille(image_path)
        print("\Pixustrate Art Output:\n")
        print(braille_art)
    except Exception as e:
        print("Failed to load or process image:", e)
