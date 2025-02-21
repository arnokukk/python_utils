import cv2
from pathlib import Path
import sys


class Frames:
    def __init__(self, path: str):
        capture = cv2.VideoCapture(path)
        self.frames = []
        for i in range(int(capture.get(cv2.CAP_PROP_FRAME_COUNT))):
            res, img = capture.read()
            if res:
                self.frames.append(img)

    def size(self):
        s = 0
        for f in self.frames:
            s += sys.getsizeof(f)
        return s


def test_video(path: str):
    _MB = 1024 * 1024
    video = Path(path)
    assert video.is_file()
    frames = Frames(path)
    print(f'Video size on disk: {int(video.stat().st_size / _MB)} MB')
    print(f'Frames object size: {sys.getsizeof(frames)} B')
    print(f'Video size as all frames: {int(frames.size() / _MB)} MB')


if __name__ == '__main__':
    test_video(r'D:\record_test\success\2025-02-17\18-48-18_0.7151 0.1472 0.0000.mp4')

