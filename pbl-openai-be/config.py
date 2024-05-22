import os


LAN_MODEL = os.getenv('LAN_MODEL', 'gpt-4')
HIST_RDs = int(os.getenv('HIST_ROUNDS', 20))
MAX_SAVE_RDs = int(os.getenv('MAX_HIST_SAVE_ROUNDS', 50))
IMG_MODEL = os.getenv('IMG_MODEL', 'dall-e-3')
IMG_SIZE = os.getenv('IMG_SIZE', '1024x1024')
