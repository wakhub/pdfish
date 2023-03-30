from pdf2image import convert_from_path
import img2pdf
import cv2
import numpy as np
from PIL import Image


RED_COLOR = (234, 51, 35)
BLUE_COLOR = (0, 0, 245)
GREEN_COLOR = (0, 255, 0)
BASE_COLOR = BLUE_COLOR
COLOR_GAP = 50
INPUT_PDF_PATH = './resources/document.pdf'
OUTPUT_PDF_PATH = './var/output.pdf'


def main():
    page_images = convert_from_path(INPUT_PDF_PATH)
    output_images = []
    index = 0
    for page_image in page_images:
        np_image = np.array(page_image)
        areas = pickup_color_areas(np_image, BASE_COLOR, COLOR_GAP)
        if len(areas) < 1:
            continue
        canvas = np.clip(np.array(0.7 * np_image), 0, 255).astype(np.uint8)
        # 各矩形領域をキャンバスに追加する
        for x, y, w, h in areas:
            roi = np_image[y:y+h, x:x+w]
            canvas[y:y+h, x:x+w] = roi
        output_image_path = './var/output_{}.png'.format(index)
        Image.fromarray(canvas).save(output_image_path)
        output_images.append(output_image_path)
        index += 1
    if len(output_images) < 1:
        return
    with open(OUTPUT_PDF_PATH, 'wb') as f:
        f.write(img2pdf.convert(output_images))


def pickup_color_areas(np_image, color, gap):
    lower_color = tuple([max(0, i - gap) for i in color])
    upper_color = tuple([min(255, i + gap) for i in color])
    mask = cv2.inRange(np_image, lower_color, upper_color)
    # マスクを膨張させることで、周辺50pxも含めた矩形領域を抽出する
    kernel = np.ones((51, 51), np.uint8)
    dilated_mask = cv2.dilate(mask, kernel)
    # 抽出された領域を矩形に囲む
    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cv2.boundingRect(cnt) for cnt in contours]


if __name__ == '__main__':
    main()