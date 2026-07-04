from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

img = Image.open('envelope-original.png').convert('RGBA')
arr = np.array(img)

# Seal bounds
sx1, sy1, sx2, sy2 = 318, 690, 617, 1025
seal = img.crop((sx1, sy1, sx2, sy2)).copy()
seal_arr = np.array(seal)
sw, sh = seal.size

# Create a mask of the seal shape (non-cream pixels)
cream_mask = (seal_arr[:,:,0] > 220) & (seal_arr[:,:,1] > 210) & (seal_arr[:,:,2] > 190)
seal_shape = ~cream_mask  # True where seal exists

# Find ALL gold pixels within seal
gold = (seal_arr[:,:,0] > 150) & (seal_arr[:,:,1] > 100) & (seal_arr[:,:,2] < 130) & seal_shape

# Get average burgundy color from dark seal pixels
dark = (seal_arr[:,:,0] < 120) & (seal_arr[:,:,1] < 60) & (seal_arr[:,:,2] < 60) & seal_shape
dark_px = seal_arr[dark]
bg = [int(dark_px[:,c].mean()) for c in range(3)]
print(f"Seal bg: RGB({bg[0]}, {bg[1]}, {bg[2]})")

# Also find highlight pixels (lighter burgundy on edges)
highlight = (seal_arr[:,:,0] > 100) & (seal_arr[:,:,0] < 180) & (seal_arr[:,:,1] < 80) & (seal_arr[:,:,2] < 80) & seal_shape & ~gold
hi_px = seal_arr[highlight]
if len(hi_px) > 0:
    hi = [int(hi_px[:,c].mean()) for c in range(3)]
    print(f"Highlight: RGB({hi[0]}, {hi[1]}, {hi[2]})")

# Paint over gold with seal colors + noise
np.random.seed(42)
noise = np.random.randint(-6, 7, (sh, sw), dtype=np.int16)
for c in range(3):
    ch = seal_arr[:,:,c].astype(np.int16)
    ch[gold] = np.clip(bg[c] + noise[gold], 0, 255)
    seal_arr[:,:,c] = ch.astype(np.uint8)

seal_pil = Image.fromarray(seal_arr, 'RGBA')

# Blur the patched area slightly to blend
# Create a mask of just the patched area
patch_mask = Image.new('L', (sw, sh), 0)
patch_arr = np.array(patch_mask)
patch_arr[gold] = 255
patch_mask = Image.fromarray(patch_arr)
patch_mask = patch_mask.filter(ImageFilter.GaussianBlur(3))

# Blend original and patched using the mask
original_seal = img.crop((sx1, sy1, sx2, sy2))
seal_pil = Image.composite(seal_pil, original_seal, patch_mask)

# Draw "C & D" in Great Vibes script
text_layer = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
td = ImageDraw.Draw(text_layer)

# Create circular mask for seal interior
seal_mask = Image.new('L', (sw, sh), 0)
md = ImageDraw.Draw(seal_mask)
md.ellipse([25, 25, sw-25, sh-25], fill=255)

# Load Great Vibes font
font = ImageFont.truetype('GreatVibes-Regular.ttf', 90)
print("Font: GreatVibes-Regular.ttf, size 90")

text = "C \u0026 D"
# Get text size
bbox = td.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
# Center in seal
tx = (sw - tw) // 2 - bbox[0]
ty = (sh - th) // 2 - bbox[1] + 5
print(f"Text pos: ({tx}, {ty}), size: {tw}x{th}")

# Gold color matching original
td.text((tx, ty), text, fill=(195, 150, 90, 240), font=font)

# Add a subtle shadow/depth to the text
shadow_layer = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow_layer)
sd.text((tx+1, ty+2), text, fill=(100, 70, 40, 80), font=font)
shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(2))

# Clip to seal circle
text_alpha = text_layer.split()[3]
shadow_alpha = shadow_layer.split()[3]
text_clipped = Image.composite(text_alpha, Image.new('L', (sw, sh), 0), seal_mask)
shadow_clipped = Image.composite(shadow_alpha, Image.new('L', (sw, sh), 0), seal_mask)
text_layer.putalpha(text_clipped)
shadow_layer.putalpha(shadow_clipped)

# Composite: seal + shadow + text
result = Image.alpha_composite(seal_pil.convert('RGBA'), shadow_layer)
result = Image.alpha_composite(result, text_layer)

# Paste back
img.paste(result, (sx1, sy1))

# Remove "TAP TO OPEN" text below envelope
draw = ImageDraw.Draw(img)
# Sample cream color around the text area
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
