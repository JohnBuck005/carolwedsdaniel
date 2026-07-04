from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import math

img = Image.open('envelope-original.png').convert('RGBA')
arr = np.array(img)

# Seal center and radius
scx, scy, sr = 467, 857, 165

# STEP 1: Erase the original seal completely by filling with envelope color
# Sample envelope color around the seal (just outside it)
samples = []
for angle in range(0, 360, 45):
    rad = math.radians(angle)
    sx = int(scx + (sr + 20) * math.cos(rad))
    sy = int(scy + (sr + 20) * math.sin(rad))
    if 0 <= sx < img.width and 0 <= sy < img.height:
        samples.append(arr[sy, sx, :3].tolist())
env_color = [int(np.mean([s[c] for s in samples])) for c in range(3)]
print(f"Envelope color: RGB({env_color[0]}, {env_color[1]}, {env_color[2]})")

# Draw filled circle over original seal
draw = ImageDraw.Draw(img)
draw.ellipse([scx-sr, scy-sr, scx+sr, scy+sr], fill=(env_color[0], env_color[1], env_color[2], 255))

# Add subtle noise to the filled area so it doesn't look flat
patch_arr = np.array(img)
for y in range(max(0,scy-sr), min(img.height, scy+sr)):
    for x in range(max(0,scx-sr), min(img.width, scx+sr)):
        dx, dy = x - scx, y - scy
        if dx*dx + dy*dy <= sr*sr:
            n = np.random.randint(-3, 4)
            for c in range(3):
                patch_arr[y,x,c] = max(0, min(255, env_color[c] + n))
img = Image.fromarray(patch_arr, 'RGBA')

# STEP 2: Create a new wax seal
seal_size = sr * 2 + 30
seal_img = Image.new('RGBA', (seal_size, seal_size), (0, 0, 0, 0))
sd = ImageDraw.Draw(seal_img)
center = seal_size // 2

# Base circle - deep burgundy
base_r = sr - 5
sd.ellipse([center-base_r, center-base_r, center+base_r, center+base_r], fill=(95, 18, 18, 255))

# Scalloped bumps
n_bumps = 28
for i in range(n_bumps):
    angle = (2 * math.pi * i) / n_bumps
    bx = center + int((base_r - 5) * math.cos(angle))
    by = center + int((base_r - 5) * math.sin(angle))
    sd.ellipse([bx-16, by-16, bx+16, by+16], fill=(95, 18, 18, 255))

# Inner gradient (lighter center for 3D effect)
inner_r = base_r - 25
for r_off in range(0, inner_r, 2):
    t = r_off / inner_r
    shade = int(120 - t * 40)
    a = int(255 * (1 - t * 0.3))
    sd.ellipse([center-r_off, center-r_off, center+r_off, center+r_off],
               fill=(shade, max(0, shade//5), max(0, shade//5), a))

# Add noise texture
seal_arr = np.array(seal_img)
mask = seal_arr[:,:,3] > 100
noise = np.random.randint(-10, 11, seal_arr.shape[:2], dtype=np.int16)
for c in range(3):
    ch = seal_arr[:,:,c].astype(np.int16)
    ch[mask] = np.clip(ch[mask] + noise[mask], 0, 255)
    seal_arr[:,:,c] = ch.astype(np.uint8)
seal_img = Image.fromarray(seal_arr, 'RGBA')

# STEP 3: Draw "C & D" in gold
text_layer = Image.new('RGBA', (seal_size, seal_size), (0, 0, 0, 0))
td = ImageDraw.Draw(text_layer)

# Use Great Vibes but make it BIG and clear
font = ImageFont.truetype('GreatVibes-Regular.ttf', 120)
text = "C \u0026 D"
bbox = td.textbbox((0, 0), text, font=font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
tx = center - tw // 2 - bbox[0]
ty = center - th // 2 - bbox[1]

# Bright gold
td.text((tx, ty), text, fill=(210, 165, 80, 245), font=font)

# Shadow
shadow = Image.new('RGBA', (seal_size, seal_size), (0, 0, 0, 0))
shd = ImageDraw.Draw(shadow)
shd.text((tx+1, ty+2), text, fill=(50, 20, 5, 120), font=font)
shadow = shadow.filter(ImageFilter.GaussianBlur(3))

# Clip to seal shape
seal_alpha = seal_img.split()[3]
text_layer.putalpha(Image.composite(text_layer.split()[3], Image.new('L', (seal_size, seal_size), 0), seal_alpha))
shadow.putalpha(Image.composite(shadow.split()[3], Image.new('L', (seal_size, seal_size), 0), seal_alpha))

# Composite seal + shadow + text
result = Image.alpha_composite(seal_img, shadow)
result = Image.alpha_composite(result, text_layer)

# STEP 4: Paste new seal onto main image
ox = scx - seal_size // 2
oy = scy - seal_size // 2
overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
overlay.paste(result, (ox, oy))
img = Image.alpha_composite(img, overlay)

# STEP 5: Remove "TAP TO OPEN" text
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
