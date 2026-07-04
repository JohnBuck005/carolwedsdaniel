from PIL import Image, ImageDraw, ImageFont
import numpy as np

img = Image.open('envelope-original.png').convert('RGBA')
arr = np.array(img)

# Seal bounds: x=[318-617], y=[690-1025]
seal_x1, seal_y1 = 318, 690
seal_x2, seal_y2 = 617, 1025
seal_orig = img.crop((seal_x1, seal_y1, seal_x2, seal_y2)).copy()
seal_arr = np.array(seal_orig)
seal_w, seal_h = seal_orig.size
print(f"Seal size: {seal_w}x{seal_h}")

# Find gold text pixels
gold_mask = (seal_arr[:,:,0] > 150) & (seal_arr[:,:,1] > 110) & (seal_arr[:,:,2] < 130)

# Find seal background color from dark non-gold area
seal_dark = (seal_arr[:,:,0] < 100) & (seal_arr[:,:,1] < 50) & (seal_arr[:,:,2] < 50)
dark_pixels = seal_arr[seal_dark]
bg_r, bg_g, bg_b = int(dark_pixels[:,0].mean()), int(dark_pixels[:,1].mean()), int(dark_pixels[:,2].mean())
print(f"Seal bg: RGB({bg_r}, {bg_g}, {bg_b})")

# Only cover center area text pixels (not edge highlights)
cx1, cx2 = int(seal_w * 0.25), int(seal_w * 0.75)
cy1, cy2 = int(seal_h * 0.20), int(seal_h * 0.80)
center_mask = np.zeros_like(gold_mask)
center_mask[cy1:cy2, cx1:cx2] = True
cover_mask = gold_mask & center_mask

# Paint with seal bg + noise (vectorized)
np.random.seed(42)
noise = np.random.randint(-5, 6, seal_arr.shape[:2], dtype=np.int16)
for c in range(3):
    channel = seal_arr[:,:,c].astype(np.int16)
    bg_val = [bg_r, bg_g, bg_b][c]
    channel[cover_mask] = np.clip(bg_val + noise[cover_mask], 0, 255).astype(np.int16)
    seal_arr[:,:,c] = channel.astype(np.uint8)

seal_pil = Image.fromarray(seal_arr, 'RGBA')

# Create circular mask for the seal's inner area
mask = Image.new('L', (seal_w, seal_h), 0)
md = ImageDraw.Draw(mask)
inner_m = 35
md.ellipse([inner_m, inner_m, seal_w - inner_m, seal_h - inner_m], fill=255)

# Draw "C & D" text
text_layer = Image.new('RGBA', (seal_w, seal_h), (0, 0, 0, 0))
td = ImageDraw.Draw(text_layer)

gold_color = (190, 145, 95, 255)

# Find best available font
font = None
for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
           "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]:
    try:
        font = ImageFont.truetype(fp, 72)
        print(f"Font: {fp}")
        break
    except:
        continue

text = "C \u0026 D"
bbox = td.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (seal_w - tw) // 2 - bbox[0]
ty = (seal_h - th) // 2 - bbox[1]
td.text((tx, ty), text, fill=gold_color, font=font)

# Clip text to seal circle
text_alpha = text_layer.split()[3]
clipped_alpha = Image.composite(text_alpha, Image.new('L', (seal_w, seal_h), 0), mask)
text_layer.putalpha(clipped_alpha)

# Composite
seal_pil = Image.alpha_composite(seal_pil, text_layer)

# Paste back
img.paste(seal_pil, (seal_x1, seal_y1))

# Remove "TAP TO OPEN" - cover with envelope color + noise
draw = ImageDraw.Draw(img)
tap_area = img.crop((340, 1040, 600, 1130))
tap_arr = np.array(tap_area).astype(np.int16)
n = np.random.randint(-3, 4, tap_arr.shape, dtype=np.int16)
tap_arr = np.clip(tap_arr + n, 0, 255).astype(np.uint8)
img.paste(Image.fromarray(tap_arr, 'RGBA'), (340, 1040))

# Save
img.save('envelope-cd.png')
print("Saved envelope-cd.png")

img.convert('RGB').save('envelope-cd.jpg', quality=95)
print("Saved envelope-cd.jpg")
