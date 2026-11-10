"""Shared character-mosaic renderer: a small RGB image (one pixel per cell) becomes glyphs with bloom."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

class Mosaic:
    def __init__(self, cols, rows, cw, ch, fsize, chars, seed=1):
        self.cols, self.rows, self.cw, self.ch = cols, rows, cw, ch
        self.chars = chars
        font = ImageFont.truetype(FONT, fsize)
        gl = []
        for c in chars:
            im = Image.new("L", (cw, ch), 0)
            ImageDraw.Draw(im).text((0, -1), c, fill=255, font=font)
            gl.append(np.asarray(im, np.float32)/255)
        self.gl = np.stack(gl)
        self.rand = np.random.RandomState(seed).randint(0, 10_000, (rows, cols))
        self.W, self.H = cols*cw, rows*ch

    def _compose(self, idx, col, bloom, bg):
        g = self.gl[idx]                                             # (R, C, ch, cw)
        out = g[..., None]*col[:, :, None, None, :]
        out = out.transpose(0, 2, 1, 3, 4).reshape(self.H, self.W, 3)
        im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
        res = np.asarray(im, np.float32)
        if bloom:
            res = res + bloom*np.asarray(im.filter(ImageFilter.GaussianBlur(3.5)), np.float32)
        if bg is not None:
            res = np.maximum(res, 0) + bg*(1-np.clip(res.max(-1, keepdims=True)/255*1.4, 0, 1))
        return Image.fromarray(np.clip(res, 0, 255).astype(np.uint8))

    def ramp(self, small, gamma=0.75, bloom=0.5, bg=None, boost=1.3):
        """chars is a density ramp (dark -> bright); colour follows the cell."""
        small = np.asarray(small, np.float32)
        lum = small.max(-1)/255
        n = len(self.chars)
        idx = np.clip((lum**gamma*n).astype(int), 0, n-1)
        col = small/np.maximum(lum, 0.2)[..., None]*np.clip(lum*boost+0.15, 0, 1)[..., None]
        return self._compose(idx, col, bloom, bg)

    def letters(self, bright, tint, classes, bloom=0.45, reveal=None):
        """bright: (R,C) 0..1. classes: list of (threshold, 'glyphs') ascending; glyph per cell is fixed-random."""
        bright = np.asarray(bright, np.float32)
        idx = np.zeros((self.rows, self.cols), int)
        for th, glyphs in classes:
            ids = np.array([self.chars.index(c) for c in glyphs])
            pick = ids[self.rand % len(ids)]
            idx = np.where(bright >= th, pick, idx)
        if reveal is not None: idx = np.where(reveal, idx, 0)
        col = np.asarray(tint, np.float32)[None, None, :]*np.clip(bright*1.15+0.1, 0, 1)[..., None]
        return self._compose(idx, col, bloom, None)

def save_webp(path, frames, durations, quality=55):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations, loop=0, quality=quality, method=6)
