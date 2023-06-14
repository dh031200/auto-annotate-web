import os
import json
from pathlib import Path

import cv2
import yaml
import numpy as np

def get_colors(num):
    return [[int(j) for j in np.random.randint(256, size=3)] for i in range(num)]
    

def denormalize(box, _width, _height):
    coords = box.split(' ')
    x = float(coords[1]) * _width
    y = float(coords[2]) * _height
    width = float(coords[3]) * _width
    height = float(coords[4]) * _height

    min_x = int(x - width / 2)
    min_y = int(y - height / 2)
    width = int(width)
    height = int(height)

    max_x = min_x + width
    max_y = min_y + height

    return int(coords[0]), min_x, min_y, max_x, max_y
    
def normalize(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[2]) / 2.0
    y = (box[1] + box[3]) / 2.0
    w = box[2] - box[0]
    h = box[3] - box[1]
    x = round(x * dw,6)
    w = round(w * dw,6)
    y = round(y * dh,6)
    h = round(h * dh,6)
    R = [x, y, w, h]
    return ' '.join(map(str, R))


def p2b(src):
    with open(f'upload/{src}/output/data.yaml', 'r') as f:
        data = yaml.safe_load(f)

    phases = ['train', 'val']
    img_extensions = ['png', 'jpg', 'ERROR']
    colors = get_colors(int(data['nc']))
    names = data['names']

    for phase in phases:
        root = Path(data[phase]).parent
        labels = root / 'labels'
        labels_bbox = root / 'labels_bbox'
        images = root / 'images'
        output = root / 'images_det'
        output.mkdir(exist_ok=True)
        labels_bbox.mkdir(exist_ok=True)

        for label in os.listdir(labels):
            extension = None
            name = (labels / label).stem
            print(f'img : {name}')
            for extension in img_extensions:
                if (images / f'{name}.{extension}').exists():
                    break
            img_path = images / f'{name}.{extension}'
            img = cv2.imread(str(img_path))
            height, width, _ = img.shape
            canvas = np.zeros_like(img)
            with open(labels / label, 'r') as f:
                lines = f.readlines()
            XY_POLYS = []
            XYN_POLYS = []
            new_lines = []
            new_boxes = []
            for line in lines:
                cls, *_line = map(float, line.split())
                cls = int(cls)
                _line = np.array(_line).reshape(-1,2)
                _line[:, 0] *= width
                _line[:, 1] *= height
                _line = _line.astype(int)
                __line = [list(x) for x in _line]
                str_line = [' '.join(map(str,x)) for x in _line]
                new_lines.append([cls, __line])
                XY_POLYS.append(f'{cls} {" ".join(str_line)}')
                XYN_POLYS.append(line.strip())
                new_boxes.append([cls, _line[:,0].min(), _line[:,1].min(), _line[:,0].max(), _line[:,1].max()])
            for idx in range(len(new_lines)):
                cls = new_lines[idx][0]
                line = new_lines[idx][1]
                boxes = new_boxes[idx]
                cv2.fillPoly(canvas, [np.int32(line)], colors[cls])
                cv2.rectangle(img, np.int32(boxes[1:3]), np.int32(boxes[3:]), colors[cls], 3)
    
            canvas = cv2.addWeighted(img,1,canvas,0.6,0)
            cv2.imwrite(f'{output}/{name}.{extension}', canvas)
            for box in new_boxes:
                cls = names[box[0]]
                left_top = [*map(int, box[1:])]
            CLASSES = [names[box[0]] for box in new_boxes]
            XY_BOXES = [[*map(int, box)] for box in new_boxes]
            XYN_BOXES = [normalize((width,height),box) for box in XY_BOXES]

            annotation = dict()
            for i in range(len(CLASSES)):
                annotation[i]=(dict(cls=CLASSES[i], box_xy=' '.join(map(str,XY_BOXES[i])), box_xyn=XYN_BOXES[i], poly_xy=XY_POLYS[i], poly_xyn=XYN_POLYS[i]))

            with open(f'upload/{src}/output/annotation.json', 'w') as f:
                json.dump(annotation, f)

