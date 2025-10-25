from fastapi import FastAPI, Request
import os
from fastapi.responses import HTMLResponse

app = FastAPI()

root_dir = os.path.dirname(os.path.abspath(__file__))

file = os.path.join(root_dir, "../frontend", "index.html")


@app.get("/", response_class=HTMLResponse)
async def serve_html(request: Request):
    # 3️⃣ Leer el archivo de forma segura
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return HTMLResponse(content="<h1>Archivo no encontrado</h1>", status_code=404)

@app.get("/request")
def read_item():
    return {"Hello": "World"}