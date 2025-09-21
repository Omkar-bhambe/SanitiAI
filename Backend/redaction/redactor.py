from  PIL import ImageDraw, ImageFilter

def redact_boxes(image, boxes, method='blackbox'):
    """
    Redact regions in image given bounding boxes.
    method: 'blackbox' or 'blur'
    boxes: list of (x, y, w, h)
    """
    img = image.copy()
    draw = ImageDraw.Draw(img)

    for (x, y, w, h) in boxes:
        if method == 'blackbox':
            draw.rectangle([x, y, x + w, y + h], fill='black')
        elif method == 'blur':
            region = img.crop((x, y, x + w, y + h))
            blurred = region.filter(ImageFilter.GaussianBlur(radius=10))
            img.paste(blurred, (x, y))
    return img
