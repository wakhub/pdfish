from pdf2image import convert_from_path
import img2pdf
import cv2
import numpy as np
from PIL import Image
import logging


logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


RED_COLOR = (234, 51, 35)
BLUE_COLOR = (0, 0, 245)
GREEN_COLOR = (0, 255, 0)
BASE_COLOR = BLUE_COLOR
COLOR_GAP = 50
ALPHA = 0.7
INPUT_PDF_PATH = './resources/document.pdf'
OUTPUT_PDF_PATH = './var/output.pdf'


def main():
    logger.info(f'''
    INPUT_PDF_PATH: {INPUT_PDF_PATH}
    OUTPUT_PDF_PATH: {OUTPUT_PDF_PATH}
    BASE_COLOR: {BASE_COLOR}
    COLOR_GAP: {COLOR_GAP}
    ''')
    page_images = convert_from_path(INPUT_PDF_PATH)
    output_images = []
    index = 1
    for page_image in page_images:
        logger.info(f'Processing page {index}...')
        np_image = np.array(page_image)
        areas = pickup_color_areas(np_image, BASE_COLOR, COLOR_GAP)
        if len(areas) < 1:
            continue
        output_image_path = './var/output_{:03d}.png'.format(index)
        highlight_areas(np_image, areas, output_image_path)
        output_images.append(output_image_path)
        index += 1
    if len(output_images) < 1:
        logger.info('No area found. (No output file is generated.)')
        return
    with open(OUTPUT_PDF_PATH, 'wb') as f:
        f.write(img2pdf.convert(output_images))
    logger.info(f'Done. (Output file {OUTPUT_PDF_PATH} is generated.)')

def highlight_areas(np_image, areas, output_image_path):
    canvas = np.clip(np.array(ALPHA * np_image), 0, 255).astype(np.uint8)
        # 各矩形領域をキャンバスに追加する
    for x, y, w, h in areas:
        roi = np_image[y:y+h, x:x+w]
        canvas[y:y+h, x:x+w] = roi
    Image.fromarray(canvas).save(output_image_path)
    return output_image_path

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