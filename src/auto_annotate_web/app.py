# SPDX-FileCopyrightText: 2023-present Danny Kim <imbird0312@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
import json
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pbaa import inference, model_init
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_prefix = Path("upload")
upload_prefix.mkdir(exist_ok=True)
model_init()


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
    extension = Path(file_name).suffix
    prompt = item.prompt
    inference(f"upload/{only_name}/input/{file_name}", prompt, output_dir=f"upload/{only_name}/output/")

    path = Path(f"upload/{only_name}/output/{only_name}_seg{extension}")

    return FileResponse(path)


@app.post("/save")
async def save_annotation(item: SaveItem):
    file_name = item.filename
    only_name = Path(file_name).stem

    path = Path(f"upload/{only_name}/output/{only_name}.json")
    with open(path) as f:
        annot = json.load(f)

    return annot
