"""hero.webp: name in clean type on the left, the lily bouquet growing on the right (text is baked in,
since README text cannot overlay an image). Run: python3 assets/mosaic/hero.py assets"""
import sys, os
from PIL import Image, ImageSequence, ImageDraw, ImageFont
out = sys.argv[1]
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; Mn = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
f1, f3 = ImageFont.truetype(B, 44), ImageFont.truetype(Mn, 13)
W, H = 950, 430
src = Image.open(os.path.join(out, "lily.webp"))
frames, durs = [], []
for f in ImageSequence.Iterator(src):
    durs.append(f.info.get("duration", 90))
    l = f.convert("RGB").resize((int(680*H/696), H), Image.LANCZOS)
    im = Image.new("RGB", (W, H), (13, 17, 23)); im.paste(l, (W - l.width - 30, 0))
    d = ImageDraw.Draw(im)
    d.text((44, 168), "ümmügülsün", font=f1, fill=(240, 246, 250)); d.text((44, 222), "türkmen", font=f1, fill=(240, 246, 250))
    d.rectangle([46, 290, 96, 292], fill=(34, 211, 238))
    d.text((46, 306), "computer engineering · hci", font=f3, fill=(139, 148, 158))
    d.text((46, 326), "bio-signal interfaces · mobile product", font=f3, fill=(139, 148, 158))
    frames.append(im)
frames[0].save(os.path.join(out, "hero.webp"), save_all=True, append_images=frames[1:], duration=durs, loop=0, quality=60, method=6)
print("hero", os.path.getsize(os.path.join(out, "hero.webp")))
