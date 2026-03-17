
import uvicorn
from fastapi import FastAPI, UploadFile, File
import httpx
app = FastAPI()
@app.post('/upload')
async def test_upload(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        files = {'file': (file.filename, file_bytes, file.content_type)}
        async with httpx.AsyncClient() as client:
            resp = await client.post('http://127.0.0.1:8004/files/upload', files=files, headers={'X-User-Id': 'test'})
            return resp.json()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

if __name__ == '__main__':
    uvicorn.run(app, port=8005)

