from PIL import Image
from selenium import webdriver
from io import BytesIO


def img_scrap(card_id, card_name):
    url = "https://shadowverse-portal.com/card/" + str(card_id) + "?lang=ko"
    driver = webdriver.Chrome("chromedriver.exe")
    driver.get(url)
    # driver.get("https://shadowverse-portal.com/card/118141020?lang=ko")
    driver.execute_script("document.body.style.zoom='125%'")
    element = driver.find_element_by_class_name("card-main-image")
    location = element.location
    size = element.size
    png = driver.get_screenshot_as_png() # saves screenshot of entire page
    driver.quit()

    im = Image.open(BytesIO(png)) # uses PIL library to open image in memory

    left = location['x'] * 1.25
    top = location['y'] * 1.25
    right = (location['x'] + size['width']) * 1.25
    bottom = (location['y'] + size['height']) * 1.25

    im = im.crop((left, top, right, bottom)) # defines crop points

    path = './original/'

    if len(card_name) >= 6:
        area = (113, 49, 248, 75)
    elif len(card_name) >= 4:
        area = (123, 49, 218, 75)
    else:
        area = (133, 49, 208, 75)
    crop = im.crop(area)
    name = path + card_name + '.png'
    crop.save(name)

# im.save('screenshot.png') # saves new cropped image

"""
path = './original/'
imgs = os.listdir(path)


def img_crop(file):
    im = Image.open(path + file)
    area = (143, 49, 218, 75)
    # area = (616, 73, 691, 99)
    crop = im.crop(area)
    fname = str(file).split('.')[0]
    name = './original/' + fname + '_1.png'
    crop.save(name)


for img in imgs:
    img_crop(img)
"""