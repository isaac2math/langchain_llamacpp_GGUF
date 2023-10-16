import os.path

from loguru import logger

from app import App
from summarizer import Summarizer

from decouple import config

APP_DIR = config('APP_DIR', default="/root/doc-sum")
MODEL_NAME = config("MODEL_NAME")
SKIP_INFERENCE = config("SKIP_INFERENCE", default=False, cast=bool)

if MODEL_NAME is None:
    raise ValueError("MODEL_NAME cannot be None")

# initialize logger
os.makedirs(os.path.join(APP_DIR, "log"), exist_ok=True)
logger.add(os.path.join(APP_DIR, "log", "{time:YYYY-MM-DD_HH-mm}.log"), rotation="20 MB")

if __name__ == '__main__':
    logger.info("Starting application...")
    logger.info("Application directory is: {0}", APP_DIR)
    logger.info("Selected model is: {0}", MODEL_NAME)
    if SKIP_INFERENCE:
        logger.info("Inference is skipped")

    # you can use the code below to test but do change the paths to your local paths
    # the `./local` folder is already in the .gitignore file so you can create them
    # without worrying about having them pushed to github accidentally

    model_dir = os.path.join(APP_DIR, "model")

    try:
        app = App(Summarizer(MODEL_NAME, model_dir, skip_inference=SKIP_INFERENCE),
                  options=
                  {
                      "app_dir": APP_DIR,
                  })
        app.run()
    except:
        logger.exception("An exception occurred while running the application.")
        raise
