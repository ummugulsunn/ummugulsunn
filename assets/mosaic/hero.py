"""hero.webp: the koi pond with the name set in clean type (baked in, since README text cannot overlay an image)."""
import sys, os
from PIL import Image, ImageSequence, ImageDraw, ImageFont
out = sys.argv[1]
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; Mn = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
f1, f2, f3 = ImageFont.truetype(B, 40), ImageFont.truetype(Mn, 15), ImageFont.truetype(Mn, 12)
frames = []
for f in ImageSequence.Iterator(Image.open(os.path.join(out, "koi.webp"))):
    im = f.convert("RGB"); d = ImageDraw.Draw(im)
    d.text((40, 372), "ümmügülsün türkmen", font=f1, fill=(240, 246, 250))
    d.text((42, 426), "I design experiences, then I ship them.", font=f2, fill=(125, 211, 232))
    d.text((42, 452), "computer engineering · hci · bio-signal interfaces · mobile product", font=f3, fill=(120, 150, 170))
    frames.append(im)
frames[0].save(os.path.join(out, "hero.webp"), save_all=True, append_images=frames[1:], duration=70, loop=0, quality=62, method=6)
frames[9].save("/tmp/claude-0/-home-user-ummugulsunn/4bb2de44-8e39-529a-a9ed-fb343a3e7429/scratchpad/out3/hero_9.png")
print("hero", os.path.getsize(os.path.join(out, "hero.webp")))
