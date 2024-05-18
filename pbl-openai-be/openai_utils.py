from collections import deque
from typing import Optional

from loguru import logger

from dependencies import chat_client, img_client, follow_up_client
from config import LAN_MODEL, HIST_RDs, IMG_MODEL, IMG_SIZE


class History:
    def __init__(self, max_save_rounds):
        self.max_save_rounds = max_save_rounds
        self.records = deque(maxlen=self.max_save_rounds)

    def get_from_list(self, lst):
        for item in lst[:-1]:
            if item['type'] == 'request':
                self.records.append({'role': 'user', 'content': item['content']})
            else:
                self.records.append({'role': 'assistant', 'content': item['content']})

    def save_history(self, role, content):
        self.records.append({'role': role, 'content': content})

    def clear_history(self):
        self.records.clear()

    def get_histories(self, n=None):
        n = n if n is not None and n < len(self.records) else len(self.records)
        return list(self.records)[-n:]

    def append_to_last_history(self, increment):
        if not self.records:
            raise IndexError('No chat_hist to append to.')
        last_record = self.records[-1]
        last_record['content'] += increment
        self.records[-1] = last_record


def get_generated_txt(sys_prompt, user_prompt, hist, stream=True):
    messages = _get_msg_with_hist(sys_prompt, user_prompt, hist)
    resp = chat_client.chat.completions.create(
        model=LAN_MODEL,
        messages=messages,
        stream=stream,
        temperature=0.8,  # if want more creative, increase this number
        # best_of=1,  # if want better quality, increase this number
    )
    _save_hist(user_prompt, hist)
    if stream:
        for chunk in resp:
            if chunk.choices[0].delta.content is not None:
                hist.append_to_last_history(chunk.choices[0].delta.content)
                yield chunk.choices[0].delta.content
    else:
        hist.append_to_last_history(resp.choices[0].message.content)
        return resp.choices[0].message.content


def get_follow_up_questions(sys_prompt, hist):
    messages = _get_msg_with_hist(sys_prompt, 'give me follow up questions', hist)
    resp = follow_up_client.chat.completions.create(
        model=LAN_MODEL,
        messages=messages,
        n=3,
        temperature=1.2,  # if want more creative, increase this number
        # best_of=3,  # if want better quality, increase this number
    )
    # no need to support stream for this
    responses = []
    for choice in resp.choices:
        if choice.message.content is not None:
            responses.append(choice.message.content)
    return responses
            
            
def get_generated_image(user_prompt, key_words: Optional[list], return_url=True):
    if key_words:
        user_prompt += f'Draw a picture of {user_prompt} which includes the following key words: '
        for i, key_word in enumerate(key_words):
            user_prompt += f'{i}: {key_word}'
            if i < len(key_words) - 1:
                user_prompt += ';'
        logger.debug(f'user_prompt: {user_prompt}')
    response_format = 'url' if return_url else 'b64_json'
    resp = img_client.images.generate(
        model=IMG_MODEL,
        prompt=user_prompt,
        size=IMG_SIZE,
        response_format=response_format,
    )
    return resp.data[0].url if return_url else resp.data[0].b64_json


def get_generated_image_with_ctx(sys_prompt, user_prompt, hist, return_url=True):
    chat_prompt = get_generated_txt(sys_prompt, user_prompt, hist, stream=False)
    logger.debug(f'chat_prompt: {chat_prompt}')
    return get_generated_image(chat_prompt, [], return_url)


def _get_msg_with_hist(sys_prompt, user_prompt, hist):
    return [{'role': 'system', 'content': sys_prompt},
            *hist.get_histories(HIST_RDs),
            {'role': 'user', 'content': user_prompt}]


def _save_hist(user_prompt, hist):
    hist.save_history('user', user_prompt)
    hist.save_history('assistant', '')
