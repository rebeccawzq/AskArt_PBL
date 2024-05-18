from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import traceback

from openai_utils import get_generated_txt, get_generated_image, get_generated_image_with_ctx, History, get_follow_up_questions
from dependencies import unify_logging
from prompt_tmpl.system_prompt import chat_sys_prompt, img_sys_prompt, follow_up_sys_prompt
from config import MAX_SAVE_RDs
from models import PromptRequest, ImgPromptRequest


app = FastAPI()
unify_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all domains, adjust as necessary for production
    allow_credentials=True,
    allow_methods=["*"],  # Allowing all methods
    allow_headers=["*"],
)


chat_hist = History(MAX_SAVE_RDs)
img_hist = History(MAX_SAVE_RDs)


@app.get('/')
async def root():
    return RedirectResponse('/docs')


@app.post('/chat/{stream}')
async def chat_with_ai(stream: bool, request: PromptRequest):
    if stream:
        return StreamingResponse(get_generated_txt(user_prompt=request.user_prompt, sys_prompt=chat_sys_prompt, hist=chat_hist, stream=True), media_type='text/plain')
    else:
        return {'message': ''}
        # return {'message': get_generated_txt(user_prompt=user_prompt, sys_prompt=chat_sys_prompt, hist=chat_hist, stream=False)}


@app.get('/chat/follow-up')
async def get_follow_up():
    try:
        return {'message': get_follow_up_questions(sys_prompt=follow_up_sys_prompt, hist=chat_hist)}
    except Exception as e:
        logger.error(f'traceback: {traceback.format_exc()}')
        return {'message': []}


@app.post('/image/{ctx}')
def generate_image(ctx: bool, request: ImgPromptRequest):
    if not ctx:
        return {'image_url': get_generated_image(user_prompt=request.user_prompt, key_words=request.key_words, return_url=True)}
    else:
        return {'image_url': ''}
        # return {'image_url': get_generated_image_with_ctx(img_sys_prompt, user_prompt, hist=img_hist, return_url=True)}


# todo: prompt optimizer

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8300)
