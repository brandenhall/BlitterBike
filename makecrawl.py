from PIL import ImageDraw, ImageFont, Image
import images2gif

font = ImageFont.truetype('fonts/IMFeENrm28P.ttf', 16)


def draw_text(text, fill, step):
	frames = []
	im = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
	draw = ImageDraw.Draw(im)
	size = draw.textsize(text, font=font)
	count = int((size[0] + 32) / step)
	offset = 32


	for i in range(count):
		im = Image.new('RGBA', (32, 32), (0,0,0,0))
		draw = ImageDraw.Draw(im)
		draw.text((offset, 8), text, font=font, fill=fill)
		offset -= step
		frames.append(im)

	return frames

frames = draw_text('last year was better', (255, 255, 0), 3)
images2gif.writeGif("test.gif", frames)
