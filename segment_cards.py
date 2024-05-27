import cv2
import numpy as np

# Test program
# read the input image
img = cv2.imread('data/bonds-thomas.png')

# threshold on white
# lower = (4, 30, 90)
# upper = (120, 120, 120)
lower = (190, 190, 190)
upper = (255, 255, 255)
# lower = (23, 44, 200)
# upper = (73, 94, 246)
thresh = cv2.inRange(img, lower, upper)

# apply morphology
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)

# get largest contour
contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[0] if len(contours) == 2 else contours[1]
# print(len(contours[0]))
big_contour = max(contours, key=cv2.contourArea)

for item in contours:
    if item.size > 400:
        big_contour = item
        # get rotated rectangle
        rotrect = cv2.minAreaRect(big_contour)
        (center), (width,height), angle = rotrect
        box = cv2.boxPoints(rotrect)
        boxpts = np.intp(box)

        # draw rotated rectangle on copy of image
        rotrect_img = img.copy()
        cv2.drawContours(rotrect_img,[boxpts],0,(0,0,255),2)

        # create mask
        mask = np.zeros_like(img, dtype=np.uint8)
        cv2.drawContours(mask,[boxpts],0,(255,255,255),-1)

        # apply mask to input
        result = cv2.bitwise_and(img, mask)


        # ADDITION:
        # get bounding box of rotated rectangle box
        x, y, w, h = cv2.boundingRect(boxpts)

        # crop image to bounding box
        crop = img[y-5:y+h+5, x-10:x+w+5]

        # save images
        cv2.imwrite('data/baseball_card_thresh.png', thresh)
        cv2.imwrite('data/baseball_card_morph.png', morph)
        cv2.imwrite('data/baseball_card_rot_rect.png', rotrect_img)
        cv2.imwrite('data/baseball_card_mask.png', mask)
        cv2.imwrite('data/baseball_card_result.png', result)
        cv2.imwrite('data/baseball_card_crop.png', crop)

        # show results
#        cv2.imshow('thresh', thresh)
#        cv2.imshow('morph', morph)
#        cv2.imshow('rotated rectangle', rotrect_img)
        cv2.imshow('mask', mask)
#        cv2.imshow('result', result)
        cv2.imshow('crop', crop)
        cv2.waitKey(0)
