"""Wrapper sobre MediaPipe Tasks HandLandmarker (API nova).

A API legada `mediapipe.solutions.hands` nao esta disponivel em wheels
de mediapipe para Python >= 3.13. Usamos a Tasks API, que precisa de
um arquivo de modelo `.task`. Ele eh baixado automaticamente na primeira
execucao se nao existir.
"""

import os
import time
import urllib.request

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

import config

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")


def _ensure_model():
    if os.path.exists(MODEL_PATH):
        return
    print(f"Baixando modelo HandLandmarker para {MODEL_PATH} ...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Modelo baixado.")


class HandDetector:
    """Detecta uma mao e devolve seus 21 landmarks normalizados."""

    def __init__(self):
        _ensure_model()
        base = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=config.MAX_HANDS,
            min_hand_detection_confidence=config.DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.DETECTION_CONFIDENCE,
            min_tracking_confidence=config.TRACKING_CONFIDENCE,
        )
        self._landmarker = mp_vision.HandLandmarker.create_from_options(options)
        self._t0 = time.perf_counter()

    def process(self, frame_bgr):
        """Recebe frame BGR e retorna lista de 21 NormalizedLandmark
        (com .x, .y, .z em [0,1]), ou None se nao detectar mao."""
        # Tasks API espera SRGB (RGB). Convertemos via numpy slicing.
        frame_rgb = frame_bgr[:, :, ::-1].copy()
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        ts_ms = int((time.perf_counter() - self._t0) * 1000)
        result = self._landmarker.detect_for_video(mp_image, ts_ms)
        if not result.hand_landmarks:
            return None
        return result.hand_landmarks[0]

    def close(self):
        self._landmarker.close()
