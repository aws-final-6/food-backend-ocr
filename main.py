from fastapi import FastAPI
from paddleocr import PaddleOCR
import re
import os
import shutil

class MyPaddleOCR:
    def __init__(self, lang: str = "korean", **kwargs):
        self.lang = lang
        self._ocr = PaddleOCR(lang="korean", use_gpu=True, use_angle_cls = True, use_space_char = True,)
        self.img_path = None
        self.ocr_result = {}

    def run_ocr(self, img_path: str):
        self.img_path = img_path
        ocr_text = []
        result = self._ocr.ocr(img_path, cls=False)
        self.ocr_result = result[0]

        if self.ocr_result:
            for r in result[0]:
                ocr_text.append(r[1][0])
        else:
            ocr_text = "No text detected."

        return ocr_text

def filter_coupang(order_list):
    result = []
    current_sublist = []

    i = 0
    while i < len(order_list) - 1:
        if order_list[i] == '장바구니' and order_list[i + 1] == '담기':
            current_sublist.append('장바구니 담기')
            result.append(current_sublist)
            current_sublist = []
            i += 2  # Skip the next item as it's part of the current sequence
        else:
            current_sublist.append(order_list[i])
            i += 1

    if i < len(order_list):  # Catch the last item if it's not part of '장바구니 담기'
        current_sublist.append(order_list[i])
        result.append(current_sublist)
    result.pop()
    food = []
    for x in result:
      if "배송완료" in x:
        num = x.index("배송완료")
        date = x[num+1]
        if '도착' in date:
          date = date[:-2]
          searchList = x[num+2:-4]
          res = [x for x in searchList if "로켓" not in x and not x[0].isdigit() and len(x) > 1]
          food.append(' '.join(res))
          #print(res)
        else:
          searchList = x[num+3:-4]
          res = [x for x in searchList if "로켓" not in x and not x[0].isdigit() and len(x) > 1]
          food.append(' '.join(res))
          #print(res)
      else:
        if x[-3] == '원':
          searchList = x[:-5]
          res = [x for x in searchList if "로켓" not in x and not x[0].isdigit() and len(x) > 1]
          food.append(' '.join(res))
          #print(res)
    return food

def split_string(s):

    match = re.match(r"([^\d]+)(\d+.*)", s)
    if match:
        return match.groups()
    return s, ''

def filter_naver(data):
    result = []
    current_item = []
    capture = False

    for item in data:
        if item.startswith("Opdy+") or item.startswith("Opay+") or item.startswith("Cpay+") or item.startswith("Dpoy+"):
            capture = True
            if current_item:
                
                result.append(' '.join(current_item))
                current_item = []
        elif capture:
            if re.match(r'\d+원', item) or re.match(r'\d+', item):
                if 'g' in current_item[-1]:
                    prev = current_item[-2]
                    curr = current_item.pop(-1)
                    res = split_string(curr)
                    current_item[-1] = prev + res[0]
                 
                capture = False
                result.append(' '.join(current_item))
                current_item = []
            else:
                current_item.append(item)

    if current_item: 
        result.append(' '.join(current_item))
    
    return result

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

ocr = MyPaddleOCR()

@app.get('/')
async def root():
    return {'hello': 'world'}

@app.post('/coupang/')
async def upload_image(file: UploadFile = File(...)):
    try:
        folder_path = "coupang"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_location = f"coupang/{file.filename}"

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ocr_result = ocr.run_ocr(file_location)
        filter_result = filter_coupang(ocr_result)


        return JSONResponse(status_code=200, content={"filename": file.filename, "result":filter_result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post('/naver/')
async def upload_image(file: UploadFile = File(...)):
    try:
        folder_path = "naver"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        file_location = f"naver/{file.filename}"

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ocr_result = ocr.run_ocr(file_location)
        filter_result = filter_naver(ocr_result)


        return JSONResponse(status_code=200, content={"filename": file.filename, "result":filter_result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
