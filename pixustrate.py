from PIL import Image, ImageEnhance
from io import BytesIO
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_image_from_keywords(keywords):
    """Fetch image URL using Google Custom Search API directly"""
    api_key = os.getenv("googleSearchAPI")
    search_engine_id = os.getenv("searchEngineAPI")
    
    if not api_key or not search_engine_id:
        raise ValueError("Google API credentials not found. Please check your .env file.")
    
    # Google Custom Search API endpoint
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': keywords,
        'searchType': 'image',
        'num': 1,
        'safe': 'off',
        'fileType': 'jpg,png'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'items' in data and len(data['items']) > 0:
            return data['items'][0]['link']
        else:
            return None
    except Exception as e:
        raise ValueError(f"Failed to search for images: {e}")

def is_url(string):
    """Check if string is a URL"""
    return string.startswith(('http://', 'https://'))

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
    # brightness * 2
    threshold = 115  # brightness threshold

    for i, (x, y) in enumerate(dots):
        if y < len(block) and x < len(block[0]):
            if block[y][x] < threshold:
                value |= (1 << i)
    
    return chr(0x2800 + value)

def image_to_braille(image_path, max_width=120, invert=True):
    # Determine if input is keywords or URL
    if is_url(image_path):
        image_url = image_path
    else:
        # Search for image using keywords
        image_url = fetch_image_from_keywords(image_path)
        if not image_url:
            raise ValueError("No image found for given keywords.")
    
    response = requests.get(image_url)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content)).convert('L')

    width, height = img.size
    if invert:
        img = Image.eval(img, lambda x: 255 - x)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # more contrast

    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.2)  # slightly brighter
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

if __name__ == "__main__":
    # brightness = int(input("Input the brightness between 0-100: "))
    image_path = input("Input the keywords or imageURL for creating image: ")
    try:
        braille_art = image_to_braille(image_path)
        print("\nPixustrate Art Output:\n")
        print(braille_art)
    except Exception as e:
        print("Failed to load or process image:", e)