# SPDX-FileCopyrightText: 2023-present Danny Kim <imbird0312@gmail.com>
#
# SPDX-License-Identifier: Apache License 2.0
import json
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from auto_annotate_web import annotate, p2b

app = FastAPI()

upload_prefix = Path("upload")
upload_prefix.mkdir(exist_ok=True)


class RunItem(BaseModel):
    filename: str
    prompt: dict


class SaveItem(BaseModel):
    filename: str
    annottype: str


@app.post("/upload")
async def upload_photo(file: UploadFile):
    new_name = str(uuid4())
    extension = Path(file.filename).suffix
    content = await file.read()
    path = upload_prefix / new_name / "input"
    path.mkdir(parents=True)
    file_name = f"{new_name}{extension}"
    with open(path / file_name, "wb") as fp:
        fp.write(content)

    return {"filename": file_name, "status": 200}


@app.post("/run")
async def run_annotation(item: RunItem):
    file_name = item.filename
    only_name = Path(file_name).stem
    prompt = item.prompt
    annotate(only_name, prompt)
    p2b(only_name)

    path = Path(f"upload/{only_name}/output/valid/images_det/{file_name}")

    return FileResponse(path)


@app.post("/save")
async def save_annotation(item: SaveItem):
    file_name = item.filename
    annot_type = item.annottype
    only_name = Path(file_name).stem

    path = Path(f"upload/{only_name}/output/annotation.json")
    with open(path) as f:
        annot = json.load(f)

    if annot_type == "rectangle":
        _type = "box_xy"
    elif annot_type == "polygon":
        _type = "poly_xy"
    else:
        return {"status": 405}

    response = {}
    for idx in annot:
        data = " ".join(annot[idx][_type].split()[1:])
        response[idx] = {"cls": annot[idx]["cls"], "annotation": data}

    return response
