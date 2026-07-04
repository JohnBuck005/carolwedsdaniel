from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

img = Image.open('envelope-original.png').convert('RGBA')
arr = np.array(img)

# Seal bounds
sx1, sy1, sx2, sy2 = 318, 690, 617, 1025
seal = img.crop((sx1, sy1, sx2, sy2)).copy()
seal_arr = np.array(seal)
sw, sh = seal.size

# Create seal shape mask (non-cream pixels)
cream = (seal_arr[:,:,0] > 220) & (seal_arr[:,:,1] > 210) & (seal_arr[:,:,2] > 190)
seal_shape = ~cream

# Find ALL gold pixels within seal
gold = (seal_arr[:,:,0] > 150) & (seal_arr[:,:,1] > 100) & (seal_arr[:,:,2] < 130) & seal_shape

# Get seal bg color from dark area
dark = (seal_arr[:,:,0] < 120) & (seal_arr[:,:,1] < 60) & (seal_arr[:,:,2] < 60) & seal_shape
dark_px = seal_arr[dark]
bg = [int(dark_px[:,c].mean()) for c in range(3)]

# Paint over gold with seal colors + noise
np.random.seed(42)
noise = np.random.randint(-6, 7, (sh, sw), dtype=np.int16)
for c in range(3):
    ch = seal_arr[:,:,c].astype(np.int16)
    ch[gold] = np.clip(bg[c] + noise[gold], 0, 255)
    seal_arr[:,:,c] = ch.astype(np.uint8)

seal_pil = Image.fromarray(seal_arr, 'RGBA')

# Blur patched area to blend
patch_mask = Image.new('L', (sw, sh), 0)
pa = np.array(patch_mask)
pa[gold] = 255
patch_mask = Image.fromarray(pa).filter(ImageFilter.GaussianBlur(3))

original_seal = img.crop((sx1, sy1, sx2, sy2))
seal_pil = Image.composite(seal_pil, original_seal, patch_mask)

# Create circular mask for seal interior
seal_mask = Image.new('L', (sw, sh), 0)
md = ImageDraw.Draw(seal_mask)
md.ellipse([25, 25, sw-25, sh-25], fill=255)

# Try Cinzel font (serif, elegant, clearly readable letters)
font_paths = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
]

# Draw "C & D" using Great Vibes but individually positioned for clarity
text_layer = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
td = ImageDraw.Draw(text_layer)

# Use Great Vibes for elegance
font = ImageFont.truetype('GreatVibes-Regular.ttf', 100)

# Draw each letter individually for better control
letters = ["C", "\u0026", "D"]
colors = [(195, 150, 90, 240)] * 3

# Measure each letter
total_w = 0
letter_widths = []
for l in letters:
    bb = td.textbbox((0, 0), l, font=font)
    w = bb[2] - bb[0]
    h = bb[3] - bb[1]
    letter_widths.append((w, h, bb[0], bb[1]))
    total_w += w

# Add spacing between letters
spacing = 8
total_w += spacing * (len(letters) - 1)

# Start x position
start_x = (sw - total_w) // 2
# Center vertically
max_h = max(lw[1] for lw in letter_widths)
start_y = (sh - max_h) // 2 + 10

x = start_x
for i, (l, (w, h, ox, oy)) in enumerate(zip(letters, letter_widths)):
    # Center each letter vertically
    y_off = (max_h - h) // 2
    td.text((x - ox, start_y + y_off - oy), l, fill=(195, 150, 90, 240), font=font)
    x += w + spacing

# Shadow
shadow_layer = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow_layer)
x = start_x
for i, (l, (w, h, ox, oy)) in enumerate(zip(letters, letter_widths)):
    y_off = (max_h - h) // 2
    sd.text((x - ox + 1, start_y + y_off - oy + 2), l, fill=(100, 70, 40, 80), font=font)
    x += w + spacing
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(2))

# Clip to seal circle
text_alpha = text_layer.split()[3]
shadow_alpha = shadow_layer.split()[3]
text_clipped = Image.composite(text_alpha, Image.new('L', (sw, sh), 0), seal_mask)
shadow_clipped = Image.composite(shadow_alpha, Image.new('L', (sw, sh), 0), seal_mask)
text_layer.putalpha(text_clipped)
shadow_layer.putalpha(shadow_clipped)

# Composite
result = Image.alpha_composite(seal_pil.convert('RGBA'), shadow_layer)
result = Image.alpha_composite(result, text_layer)

# Paste back
img.paste(result, (sx1, sy1))

# Remove "TAP TO OPEN" text
tap_y1, tap_y2 = 1045, 1125
tap_x1, tap_x2 = 340, 610
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
