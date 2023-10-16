import os
import pathlib
import traceback
from time import sleep
from typing import Dict, Any, List, Tuple

from loguru import logger

from summarizer import Summarizer


def _create_dir(dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


class App:
    DEFAULT_APP_DIR = "/root/doc-sum"

    def __init__(self, summarizer: Summarizer,
                 options: Dict[str, Any] = None):
        if summarizer is None:
            raise ValueError("summarizer cannot be None")

        self._summarizer = summarizer
        self._logger = logger
        self._options = options or {}

    def run(self):
        self._initialize_directories()

        file_to_skip = []
        while True:
            file_name_list = self._list_files()
            file_name_list = [name for name in file_name_list if name not in file_to_skip]  # remove skipped files
            if len(file_name_list) == 0:
                if self._options.get("test_mode", False):
                    break  # exit loop if test_mode is enabled
                else:
                    sleep(3)  # sleep for 1 second and continue
                    continue
            file_to_process = file_name_list[0] or [-1]  # get the first file in the list
            success = self._process_file(file_to_process)
            if not success:
                file_to_skip.append(file_to_process)

    def _initialize_directories(self):
        _create_dir(self._get_path(["in"]))
        _create_dir(self._get_path(["out"]))
        _create_dir(self._get_path(["process"]))
        _create_dir(self._get_path(["error"]))

    def _process_file(self, file_path: str) -> bool:
        self._logger.info("Processing file: {0}", file_path)
        file_name = pathlib.Path(file_path).stem
        file_extension = pathlib.Path(file_path).suffix
        raw_file_name = file_name + file_extension

        process_file_path = self._get_path(["process", raw_file_name])
        error_file_path = self._get_path(["error", raw_file_name])

        try:
            if not self._try_move_file(file_path, process_file_path):
                return False

            with open(process_file_path) as f:
                raw_text = f.read()

            result_file_name = file_name + "_result" + file_extension
            (success, summary) = self._try_summarize(file_path, raw_text)
            if not success:
                self._try_move_file(process_file_path, error_file_path)
                return False

            # write summary to result file
            out_result_file_path = self._get_path(["out", result_file_name])
            with open(out_result_file_path, 'w') as f:
                f.write(summary)

            # move raw file to output directory
            out_raw_file_path = self._get_path(["out", raw_file_name])
            os.rename(process_file_path, out_raw_file_path)
            self._logger.info("Successfully processed file: {0}", file_path)
        except:
            self._logger.exception("An error occurred while processing file: {0}", file_path)
            self._try_move_file(process_file_path, error_file_path)  # move process file to error_dir
            return False
        return True

    def _get_path(self, segments: List[str]) -> str:
        return os.path.join(self._options.get("app_dir", App.DEFAULT_APP_DIR), *segments)

    def _try_summarize(self, file_path: str, raw_text: str) -> Tuple[bool, str | None]:
        try:
            result = self._summarizer.summarize(raw_text)
            return True, result
        except:
            self._logger.exception("An error occurred while summarizing file: {0}", file_path)
            return False, None

    def _try_move_file(self, file_path: str, target_dir: str, retries: int = 0, max_retries: int = 1) -> bool:
        if retries > max_retries:
            self._logger.warning("Max retries exceeded while moving file: {0}", file_path)
            return False
        try:
            os.rename(file_path, target_dir)
            return True
        except:
            # log exception stacktrace
            self._logger.exception("An error occurred while moving file: {0}. Retrying it in 1 second...",
                                   file_path)
            sleep(1)
            return self._try_move_file(file_path, target_dir, retries=retries + 1, max_retries=max_retries)

    def _list_files(self) -> List[str]:
        # get all file paths
        file_paths = []
        in_dir = self._get_path(["in"])
        for root, dirs, files in os.walk(in_dir):
            for file in files:
                file_paths.append(os.path.join(root, file))

        # sort file paths by modification time
        sorted_file_paths = sorted(file_paths, key=os.path.getmtime)

        # convert sorted_file_paths to Array[str]
        return [item.decode('utf-8') if isinstance(item, bytes) else str(item) for item in sorted_file_paths]
