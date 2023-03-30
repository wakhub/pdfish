from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image


BASE_COLOR = (0, 0, 255) # G, B, R
COLOR_GAP = 10
PDF_PATH = './resources/document.pdf'


def main():
    lower_color = tuple([max(0, i - COLOR_GAP) for i in BASE_COLOR])
    upper_color = tuple([min(255, i + COLOR_GAP) for i in BASE_COLOR])

    page_images = convert_from_path(PDF_PATH)
    index = 0
    for page_image in page_images:
        np_image = np.array(page_image)
        color_area_image = pickup_color_areas(np_image, BASE_COLOR, COLOR_GAP)
        Image.fromarray(color_area_image).save(f'./var/{index}.png', 'PNG')
        index += 1


def pickup_color_areas(np_image, color, gap):
    lower_color = tuple([max(0, i - gap) for i in color])
    upper_color = tuple([min(255, i + gap) for i in color])

    mask = cv2.inRange(np_image, lower_color, upper_color)
    # マスクを膨張させることで、周辺50pxも含めた矩形領域を抽出する
    kernel = np.ones((51, 51), np.uint8)
    dilated_mask = cv2.dilate(mask, kernel)
    # 抽出された領域を矩形に囲む
    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rectangles = [cv2.boundingRect(cnt) for cnt in contours]

    canvas = np.zeros_like(np_image)
    # 各矩形領域をキャンバスに追加する
    for x, y, w, h in rectangles:
        roi = np_image[y:y+h, x:x+w]
        canvas[y:y+h, x:x+w] = roi
    return canvas


if __name__ == '__main__':
    main()