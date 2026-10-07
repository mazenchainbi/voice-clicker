from PIL import Image

img = Image.open("assets/logo.png").convert("RGBA")
img.save("assets/logo.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])