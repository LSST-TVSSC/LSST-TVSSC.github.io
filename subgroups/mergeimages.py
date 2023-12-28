import sys
from PIL import Image
#Read the two images
image1 = Image.open(sys.argv[1])

image1.show()
image2 = Image.open(sys.argv[2])
image2.show()

#resize, first image
image1 = image1.resize(image2.size)
image1_size = image1.size


box = (0, 0, int(image1_size[0]*0.75), image1_size[1])
image1 = image1.crop(box)


box = (int(image1_size[0]*0.25), 0, image1_size[0], image1_size[1])
image2 = image2.crop(box)

image2 = image2.resize(image1.size)
image1_size = image1.size

print(image1.size)
print(image2.size)

new_image = Image.new('RGB',(image1_size[0]*2, image1_size[1]), (250,250,250))
new_image.paste(image1,(0,0))
new_image.paste(image2,(image1_size[0],0))
new_image.save("merged_image.png","PNG")
new_image.show()
