from PIL import Image, ImageDraw, ImageFont
import numpy as np

img = Image.open('envelope-original.png').convert('RGBA')
arr = np.array(img)

# Seal bounds in original: x=[318-617], y=[690-1025]
# Find the burgundy seal color
seal_region = arr[750:950, 380:550]
dark_mask = (seal_region[:,:,0] < 120) & (seal_region[:,:,1] < 80) & (seal_region[:,:,2] < 80)
seal_colors = seal_region[dark_mask]
seal_r = int(seal_colors[:,0].mean())
seal_g = int(seal_colors[:,1].mean())
seal_b = int(seal_colors[:,2].mean())
print(f"Seal color: RGB({seal_r}, {seal_g}, {seal_b})")

# Find gold text area precisely
gold_mask = (arr[:,:,0] > 150) & (arr[:,:,1] > 110) & (arr[:,:,2] < 130)
bounds_mask = np.zeros_like(gold_mask)
bounds_mask[690:1025, 318:617] = True
text_mask = gold_mask & bounds_mask
ty, tx = np.where(text_mask)
print(f"Gold text in original: x=[{tx.min()}-{tx.max()}], y=[{ty.min()}-{ty.max()}]")

text_cx = (tx.min() + tx.max()) // 2
text_cy = (ty.min() + ty.max()) // 2

# Cover the initials area with seal color
draw = ImageDraw.Draw(img)
seal_color = (seal_r, seal_g, seal_b, 255)

cover_x1 = tx.min() - 5
cover_y1 = ty.min() - 5
cover_x2 = tx.max() + 5
cover_y2 = ty.max() + 5
draw.rectangle([cover_x1, cover_y1, cover_x2, cover_y2], fill=seal_color)

# Also add subtle texture by blending some noise
np.random.seed(42)
noise = np.random.randint(-8, 8, (cover_y2-cover_y1, cover_x2-cover_x1, 3), dtype=np.int16)
patch = np.array(img)[cover_y1:cover_y2, cover_x1:cover_x2].astype(np.int16)
patch[:,:,:3] = np.clip(patch[:,:,:3] + noise, 0, 255)
patch_arr = np.array(img)
patch_arr[cover_y1:cover_y2, cover_x1:cover_x2] = patch.astype(np.uint8)
img = Image.fromarray(patch_arr, 'RGBA')
draw = ImageDraw.Draw(img)

# Draw "C & D" in gold
gold_color = (181, 137, 101, 255)

# Try system fonts
font_paths = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
]
font = None
for fp in font_paths:
    try:
        font = ImageFont.truetype(fp, 85)
        print(f"Using font: {fp}")
        break
    except Exception as e:
        print(f"Failed {fp}: {e}")
        continue

if font is None:
    font = ImageFont.load_default()
    print("Using default font")

text = "C \u0026 D"
bbox = draw.textbbox((0, 0), text, font=font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
tx_pos = text_cx - tw // 2
ty_pos = text_cy - th // 2 - 10

draw.text((tx_pos, ty_pos), text, fill=gold_color, font=font)

img.save('envelope-cd.png')
print("Saved envelope-cd.png")
