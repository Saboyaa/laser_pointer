"""Loop principal do protótipo de hand tracking laser pointer.

Roda a webcam, detecta uma mão, calcula a direção do apontamento (do pulso
até a ponta do indicador) e desenha um "laser virtual" sobre o vídeo.
"""

import sys
import time

import cv2

import config
from direction_calc import classify_direction, pointing_vector
from hand_detector import HandDetector
import visualizer as vis


def main():
    cap = cv2.VideoCapture(config.CAM_INDEX)
    if not cap.isOpened():
        print("Erro: nao foi possivel abrir a camera.", file=sys.stderr)
        return 1

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)

    detector = HandDetector()

    prev_t = time.perf_counter()
    fps = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Falha ao ler frame da camera.", file=sys.stderr)
                break

            # Espelhar para feedback natural (mao direita aparece a direita)
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            landmarks = detector.process(frame)

            if landmarks is not None:
                origin, vec, depth = pointing_vector(landmarks, w, h)
                direction = classify_direction(vec, depth)

                vis.draw_landmarks(frame, landmarks)
                vis.draw_laser(frame, origin, vec)
                vis.draw_direction_text(frame, direction)
                vis.draw_direction_panel(frame, vec, depth, direction)
            else:
                vis.draw_no_hand(frame)
                vis.draw_direction_panel(frame, (0.0, 0.0), 0.0, None)

            # FPS suavizado (média móvel exponencial)
            now = time.perf_counter()
            dt = now - prev_t
            prev_t = now
            if dt > 0:
                inst = 1.0 / dt
                fps = inst if fps == 0.0 else (fps * 0.9 + inst * 0.1)
            vis.draw_fps(frame, fps)

            cv2.imshow("Hand Laser Tracker", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        detector.close()
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    sys.exit(main())
