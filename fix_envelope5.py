from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import math

# Load original
img = Image.open('envelope-original.png').convert('RGBA')
arr = np.array(img)

# Seal position in original: x=[318-617], y=[690-1025]
# Center: (467, 857), radius ~150
seal_cx, seal_cy = 467, 857
seal_r = 155

# Step 1: Create a new wax seal from scratch
seal_size = seal_r * 2 + 20
seal_img = Image.new('RGBA', (seal_size, seal_size), (0, 0, 0, 0))
sd = ImageDraw.Draw(seal_img)

# Scalloped edge - draw multiple overlapping circles
center = seal_size // 2
num_scallops = 24
scallops_r = seal_r
inner_r = seal_r - 8

# Draw base circle (dark burgundy)
sd.ellipse([center-scallops_r, center-scallops_r, center+scallops_r, center+scallops_r], fill=(90, 15, 15, 255))

# Draw scalloped bumps around edge
for i in range(num_scallops):
    angle = (2 * math.pi * i) / num_scallops
    bump_x = center + int((scallops_r - 8) * math.cos(angle))
    bump_y = center + int((scallops_r - 8) * math.sin(angle))
    bump_r = 18
    sd.ellipse([bump_x-bump_r, bump_y-bump_r, bump_x+bump_r, bump_y+bump_r], fill=(90, 15, 15, 255))

# Inner circle with gradient effect (slightly lighter burgundy)
for r_offset in range(20):
    alpha = int(255 * (1 - r_offset / 30))
    shade = 80 + r_offset * 2
    sd.ellipse([center-inner_r+r_offset, center-inner_r+r_offset, 
                center+inner_r-r_offset, center+inner_r-r_offset], 
               fill=(shade, max(0, shade//6), max(0, shade//6), alpha))

# Add texture noise to the seal
seal_arr = np.array(seal_img)
for c in range(3):
    noise = np.random.randint(-8, 9, (seal_size, seal_size), dtype=np.int16)
    ch = seal_arr[:,:,c].astype(np.int16)
    # Only add noise where seal exists
    mask = seal_arr[:,:,3] > 0
    ch[mask] = np.clip(ch[mask] + noise[mask], 0, 255)
    seal_arr[:,:,c] = ch.astype(np.uint8)
seal_img = Image.fromarray(seal_arr, 'RGBA')

# Step 2: Draw "C & D" in gold on the seal
text_layer = Image.new('RGBA', (seal_size, seal_size), (0, 0, 0, 0))
td = ImageDraw.Draw(text_layer)

# Use Great Vibes for the script
font = ImageFont.truetype('GreatVibes-Regular.ttf', 110)

text = "C \u0026 D"
bbox = td.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = center - tw // 2 - bbox[0]
ty = center - th // 2 - bbox[1]

# Gold with slight gradient effect
td.text((tx, ty), text, fill=(200, 155, 85, 230), font=font)

# Shadow for depth
shadow = Image.new('RGBA', (seal_size, seal_size), (0, 0, 0, 0))
shd = ImageDraw.Draw(shadow)
shd.text((tx+1, ty+2), text, fill=(60, 30, 10, 100), font=font)
shadow = shadow.filter(ImageFilter.GaussianBlur(2))

# Clip to seal shape
seal_alpha = seal_img.split()[3]
text_layer.putalpha(Image.composite(text_layer.split()[3], Image.new('L', (seal_size, seal_size), 0), seal_alpha))
shadow.putalpha(Image.composite(shadow.split()[3], Image.new('L', (seal_size, seal_size), 0), seal_alpha))

# Composite seal + shadow + text
result = Image.alpha_composite(seal_img, shadow)
result = Image.alpha_composite(result, text_layer)

# Step 3: Paste new seal over original image
paste_x = center - seal_size // 2
paste_y = center - seal_size // 2
# We need to paste at the seal's position in the original image
# Original seal center: (467, 857)
offset_x = seal_cx - seal_size // 2
offset_y = seal_cy - seal_size // 2

# Create a full-size overlay
overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
overlay.paste(result, (offset_x, offset_y))

# Use the seal alpha to blend
img = Image.alpha_composite(img, overlay)

# Step 4: Remove "TAP TO OPEN" text
draw = ImageDraw.Draw(img)
tap_y1, tap_y2 = 1045, 1130
tap_x1, tap_x2 = 330, 620
tap_crop = img.crop((tap_x1, tap_y1, tap_x2, tap_y2))
tap_arr = np.array(tap_crop).astype(np.int16)
n = np.random.randint(-2, 3, tap_arr.shape, dtype=np.int16)
tap_arr = np.clip(tap_arr + n, 0, 255).astype(np.uint8)
img.paste(Image.fromarray(tap_arr, 'RGBA'), (tap_x1, tap_y1))

# Save
img.save('envelope-cd.png')
print("Saved envelope-cd.png")
img.convert('RGB').save('envelope-cd.jpg', quality=95)
print("Saved envelope-cd.jpg")
print("Done!")
