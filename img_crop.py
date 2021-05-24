from PIL import Image
from selenium import webdriver
from io import BytesIO
from pyautogui import locate

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
# https://shadowverse-portal.com/image/card/phase2/common/C/C_119713010.png
# https://shadowverse-portal.com/image/card/phase2/ko/N/N_119141010.png


def capture():
    import win32gui
    import win32ui
    from ctypes import windll
    from PIL import ImageGrab
    import sys
    import cv2
    import numpy as np

    while 1:
        hwnd = win32gui.FindWindow(None, 'Shadowverse')
        try:
            left, top, right, bot = win32gui.GetClientRect(hwnd)
        except:
            print('창을 찾을 수 없습니다.')
            sys.exit()

        w = right - left
        h = bot - top

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

        saveDC.SelectObject(saveBitMap)

        result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)

        try:
            im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        except ValueError:
            print('창이 최소화되어있습니다.')
            sys.exit()

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        area = (480, 140, 550, 210)
        im = im.crop(area).convert('RGB')
        cv_im = np.array(im)
        cv_im = cv2.cvtColor(cv_im, cv2.COLOR_RGB2BGR)

        cv2.imshow('test', cv_im)
        key = cv2.waitKey(10)
        if key == 27:
            break


def test_f(image):
    test_img = Image.open('./test/test2.png')
    c = 0.90
    if not locate(test_img, image, grayscale=True, confidence=c) is None:
        print('ok, c=', c)


if __name__ == "__main__":
    capture()
