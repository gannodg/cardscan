import cv2
import numpy as np
import os
import argparse

GREEN_BACKGROUND_MIN = (50, 35, 20)
GREEN_BACKGROUND_MAX = (70, 255, 255)

RED_BACKGROUND_MIN = (0, 35, 20)
RED_BACKGROUND_MAX = (10, 255, 255)


def main(args):
    path = args.filename
    if args.red:
        b_min = RED_BACKGROUND_MIN
        b_max = RED_BACKGROUND_MAX
    else:
        bmin = GREEN_BACKGROUND_MIN
        bmax = GREEN_BACKGROUND_MAX
    image_crop = args.img_crop if args.img_crop else 0
    card_border = args.card_border if args.card_border else 10

    find_cards(path, bmin, bmax, image_crop, card_border)


def find_cards(img_path, background_min, background_max, image_crop = 0, card_border = 10):
    # read in image and crop if needed
    image_name = os.path.basename(img_path).split('.')[0]
    img = cv2.imread(img_path)
    img_shape = img.shape
    img = img[image_crop:img_shape[0]-image_crop, image_crop:img_shape[1]-image_crop]
    shape = img.shape

    # convert color to hue, saturation, value (hsv) and create mask based on background color
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, background_min, background_max)
    mask = cv2.bitwise_not(mask) # invert mask to get cards mask

    smal_shape = (shape[1]//3, shape[0]//3) # resize for display
    small_mask = cv2.resize(mask, smal_shape)
    cv2.imshow('mask', small_mask)

    # get contours of card mask
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # copy and resizefor display
    contour_img = img.copy()
    cv2.drawContours(contour_img, contours, contourIdx=-1, color=(255,0,0), thickness=4, lineType=cv2.LINE_AA)
    small_contour = cv2.resize(contour_img, smal_shape)
    cv2.imshow('contours', small_contour)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    inp = input('Save cards? (y/n)')
    if inp.lower() == 'y':
        # go through contours
        i = 0
        for item in contours:
            # get the area
            rect = cv2.minAreaRect(item)
            width, height = rect[1]
            item_area = width * height
            if item_area > 100000: #filter out the small ones
                print(f'Item area {item_area}')
                i += 1
                s = 'found 1 card' if i < 2 else f'found {i} cards'
                print(s)
                # get bounding box
                rect = cv2.minAreaRect(item)
                box = cv2.boxPoints(rect)
                boxpts = np.intp(box)
                x, y, w, h = cv2.boundingRect(boxpts)

                # crop out card
                card_img = img[y-card_border:y+h+card_border, x-card_border:x+w+card_border]

                # save img
                cv2.imwrite(f'outputs/{image_name}-card{i}.png', card_img)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Card Segmenter')
    parser.add_argument('filename')
    parser.add_argument('-r', '--red', action='store_true', help='Whether to use green or red background')
    parser.add_argument('-i', '--img-crop', type=int, help='An integer specifying how much of the input images borders to crop')
    parser.add_argument('-c', '--card-border', type=int, help ='An integer specifying how many pixels to pad out the cards bordersgi')
    args = parser.parse_args()
    main(args)
