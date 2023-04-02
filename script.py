import argparse

from pdf2image import convert_from_path
import img2pdf
import cv2
import numpy as np
from PIL import Image
import logging


logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


INPUT_PDF_PATH = './resources/document.pdf'
OUTPUT_PDF_PATH = './var/output.pdf'
RGB = '0,0,0'
COLOR_GAP = 30
SHADOW = 0.7


def main():    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default=INPUT_PDF_PATH,
                        help='Input PDF file path. (default: ./resources/document.pdf)')
    parser.add_argument('--output', type=str, default=OUTPUT_PDF_PATH,
                        help='Output PDF file path. (default: ./var/output.pdf)')
    parser.add_argument('--rgb', type=str, default=RGB,
                        help='RGB color to highlight. (default: 0,0,0)')
    parser.add_argument('--gap', type=int, default=COLOR_GAP,
                        help='Color gap to highlight. (default: 50)')
    parser.add_argument('--shadow', type=float, default=SHADOW,
                        help='Shadow ratio. (default: 0.7)')

    args = parser.parse_args()
    rgb = tuple([int(i) for i in args.rgb.split(',')])
    assert len(rgb) == 3, 'rgb must be 3 integers separated by comma.'
    assert list(filter(lambda i: i < 0 or i > 255, rgb)) == [], 'rgb must be 3 integers between 0 and 255.'
    
    logger.info('\n'.join([
        f'input: {args.input}',
        f'output: {args.output}',
        f'rgb: {rgb}',
        f'gap: {args.gap}',
        f'shadow: {args.shadow}',
        '-' * 20
    ]))
    page_images = convert_from_path(args.input)
    output_images = []
    page = 1
    for page_image in page_images:
        logger.info(f'Processing page {page}...')
        np_image = np.array(page_image)
        areas = pickup_color_areas(np_image, rgb, args.gap)
        if len(areas) < 1:
            continue
        output_image_path = './var/output_{:03d}.png'.format(page)
        highlight_areas(np_image, areas, output_image_path)
        output_images.append(output_image_path)
        page += 1
    if len(output_images) < 1:
        logger.info('No area found. (No output file is generated.)')
        return
    with open(args.output, 'wb') as f:
        f.write(img2pdf.convert(output_images))
    logger.info(f'Done. (Output file {args.output} is generated.)')

def highlight_areas(np_image, areas, output_image_path):
    canvas = np.clip(np.array(SHADOW * np_image), 0, 255).astype(np.uint8)
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