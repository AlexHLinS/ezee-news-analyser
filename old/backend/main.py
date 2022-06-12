from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware


class News(BaseModel):
    url: Optional[str]
    text: Optional[str]


app = FastAPI(redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/')
async def get_news(news: News) -> dict[str, News]:
    print(news)
    return {'result': news}
