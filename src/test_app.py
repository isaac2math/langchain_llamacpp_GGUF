import os.path
import shutil
import unittest
import uuid
from unittest.mock import Mock

from app import App


class TestApp(unittest.TestCase):
    TEST_APP_DIR = os.path.join("fixtures", "test_app")
    TEST_IN_DIR = os.path.join(TEST_APP_DIR, "in")
    TEST_PROCESS_DIR = os.path.join(TEST_APP_DIR, "process")
    TEST_OUT_DIR = os.path.join(TEST_APP_DIR, "out")
    TEST_ERROR_DIR = os.path.join(TEST_APP_DIR, "error")

    def test_run(self):
        """
        Test run method which should process all files in the in_dir
        and move them to the out_dir and generate a summary file per file in out_dir
        """
        # arrange
        summarizer = Mock()
        summarizer.summarize.return_value = "summary"
        sut = App(summarizer, {
            "app_dir": TestApp.TEST_APP_DIR,
            "test_mode": True
        })
        self._create_empty_file(os.path.join(TestApp.TEST_IN_DIR, f"{uuid.uuid4().hex}.txt"))
        self._create_empty_file(os.path.join(TestApp.TEST_IN_DIR, f"{uuid.uuid4().hex}.txt"))
        self._create_empty_file(os.path.join(TestApp.TEST_IN_DIR, f"{uuid.uuid4().hex}.txt"))

        # act
        sut.run()

        # assert
        self.assertEqual(0, len(os.listdir(TestApp.TEST_IN_DIR)))
        self.assertEqual(6, len(os.listdir(TestApp.TEST_OUT_DIR)))  # 3 raw, 3 result
        self.assertEqual(0, len(os.listdir(TestApp.TEST_PROCESS_DIR)))
        self.assertEqual(0, len(os.listdir(TestApp.TEST_ERROR_DIR)))

    @staticmethod
    def _create_empty_file(file_path: str):
        f = open(file_path, 'w')
        f.write(uuid.uuid4().hex)
        f.close()

    @classmethod
    def setUpClass(cls):
        """
        Create test directories
        """
        os.makedirs(TestApp.TEST_IN_DIR, exist_ok=True)
        os.makedirs(TestApp.TEST_PROCESS_DIR, exist_ok=True)
        os.makedirs(TestApp.TEST_OUT_DIR, exist_ok=True)
        os.makedirs(TestApp.TEST_ERROR_DIR, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """
        Remove test directories and their temporary files
        """
        shutil.rmtree("fixtures")


if __name__ == '__main__':
    unittest.main()
