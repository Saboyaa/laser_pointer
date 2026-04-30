"""Funcoes de desenho sobre o frame.

Nao dependemos de `mediapipe.solutions.drawing_utils` (indisponivel em
wheels de Python >= 3.13). Desenhamos landmarks/conexoes diretamente.
"""

import cv2

import config

# Conexoes entre landmarks da mao (mesma topologia da MediaPipe Hands)
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),           # polegar
    (0, 5), (5, 6), (6, 7), (7, 8),           # indicador
    (5, 9), (9, 10), (10, 11), (11, 12),      # medio
    (9, 13), (13, 14), (14, 15), (15, 16),    # anelar
    (13, 17), (17, 18), (18, 19), (19, 20),   # minimo
    (0, 17),                                  # palma
)

_LM_COLOR = (0, 255, 255)         # amarelo
_CONN_COLOR = (255, 255, 255)     # branco


def _to_px(landmark, w, h):
    return int(landmark.x * w), int(landmark.y * h)


def draw_landmarks(frame, landmarks):
    """Desenha os 21 pontos da mao e suas conexoes."""
    h, w = frame.shape[:2]
    pts = [_to_px(lm, w, h) for lm in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], _CONN_COLOR, 2, cv2.LINE_AA)
    for p in pts:
        cv2.circle(frame, p, 4, _LM_COLOR, -1, cv2.LINE_AA)


def draw_laser(frame, origin, vec_xy, length=config.LASER_LENGTH):
    """Desenha uma linha vermelha a partir de origin, na direcao vec_xy."""
    ox, oy = origin
    ex = int(ox + vec_xy[0] * length)
    ey = int(oy + vec_xy[1] * length)
    cv2.line(
        frame,
        (int(ox), int(oy)),
        (ex, ey),
        config.LASER_COLOR,
        config.LASER_THICKNESS,
        lineType=cv2.LINE_AA,
    )
    cv2.circle(frame, (int(ox), int(oy)), 6, config.LASER_COLOR, -1)


def draw_direction_text(frame, direction):
    cv2.putText(
        frame,
        f"Direcao: {direction}",
        config.TEXT_POSITION,
        cv2.FONT_HERSHEY_SIMPLEX,
        config.TEXT_SCALE,
        config.TEXT_COLOR,
        config.TEXT_THICKNESS,
        cv2.LINE_AA,
    )


def draw_fps(frame, fps):
    h, w = frame.shape[:2]
    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (w - 130, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        config.TEXT_SCALE,
        config.FPS_COLOR,
        config.TEXT_THICKNESS,
        cv2.LINE_AA,
    )


def draw_no_hand(frame):
    cv2.putText(
        frame,
        "Nenhuma mao detectada",
        config.TEXT_POSITION,
        cv2.FONT_HERSHEY_SIMPLEX,
        config.TEXT_SCALE,
        (0, 165, 255),
        config.TEXT_THICKNESS,
        cv2.LINE_AA,
    )


_PANEL_RADIUS = 90
_PANEL_MARGIN = 20
_BAR_WIDTH = 14
_TRAIL_MAX = 30
_trail = []  # historico dos ultimos vetores (vx, vy) para ver jitter


def _zone_highlight_color(direction):
    return {
        config.DIR_UP: (60, 60, 200),
        config.DIR_DOWN: (60, 60, 200),
        config.DIR_LEFT: (60, 60, 200),
        config.DIR_RIGHT: (60, 60, 200),
        config.DIR_FORWARD: (0, 80, 200),
    }.get(direction, (60, 60, 60))


def draw_direction_panel(frame, vec_xy, depth_ratio, direction):
    """Painel grande mostrando o vetor 2D bruto, as 4 zonas, trail e
    a barra de depth_ratio com threshold de FRENTE.

    Permite avaliar a precisao real do apontamento, nao so a zona
    classificada."""
    h, w = frame.shape[:2]
    r = _PANEL_RADIUS
    cx = w - r - _PANEL_MARGIN - _BAR_WIDTH - 10
    cy = h - r - _PANEL_MARGIN

    # --- Fundo semi-transparente do painel ---
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (cx - r - 6, cy - r - 6),
        (cx + r + _BAR_WIDTH + 16, cy + r + 6),
        (30, 30, 30),
        -1,
    )
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    # --- Triangulos das 4 zonas (divididas pelas diagonais) ---
    # cima, direita, baixo, esquerda
    zones = {
        config.DIR_UP:    [(cx, cy), (cx - r, cy - r), (cx + r, cy - r)],
        config.DIR_RIGHT: [(cx, cy), (cx + r, cy - r), (cx + r, cy + r)],
        config.DIR_DOWN:  [(cx, cy), (cx + r, cy + r), (cx - r, cy + r)],
        config.DIR_LEFT:  [(cx, cy), (cx - r, cy + r), (cx - r, cy - r)],
    }
    import numpy as np  # mediapipe ja traz numpy; usado so para cv2.fillPoly
    for name, pts in zones.items():
        color = _zone_highlight_color(name) if name == direction else (50, 50, 50)
        cv2.fillPoly(frame, [np.array(pts, dtype=np.int32)], color)

    # bordas
    cv2.rectangle(frame, (cx - r, cy - r), (cx + r, cy + r), (180, 180, 180), 1, cv2.LINE_AA)
    cv2.line(frame, (cx - r, cy - r), (cx + r, cy + r), (120, 120, 120), 1, cv2.LINE_AA)
    cv2.line(frame, (cx - r, cy + r), (cx + r, cy - r), (120, 120, 120), 1, cv2.LINE_AA)
    cv2.line(frame, (cx - r, cy), (cx + r, cy), (90, 90, 90), 1)
    cv2.line(frame, (cx, cy - r), (cx, cy + r), (90, 90, 90), 1)

    # zona central FRENTE (so visual; ativada via depth_ratio)
    inner = 16
    inner_color = (0, 80, 220) if direction == config.DIR_FORWARD else (70, 70, 70)
    cv2.circle(frame, (cx, cy), inner, inner_color, -1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), inner, (200, 200, 200), 1, cv2.LINE_AA)

    # labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, "C", (cx - 6, cy - r + 14), font, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
    cv2.putText(frame, "B", (cx - 6, cy + r - 4), font, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
    cv2.putText(frame, "E", (cx - r + 4, cy + 5), font, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
    cv2.putText(frame, "D", (cx + r - 14, cy + 5), font, 0.5, (220, 220, 220), 1, cv2.LINE_AA)

    # --- Trail dos ultimos vetores (jitter) ---
    vx, vy = vec_xy
    _trail.append((vx, vy))
    if len(_trail) > _TRAIL_MAX:
        del _trail[0]
    for i, (tx, ty) in enumerate(_trail):
        alpha = (i + 1) / len(_trail)
        px = int(cx + tx * r)
        py = int(cy + ty * r)
        radius = max(1, int(2 + alpha * 2))
        col = (int(200 * alpha), int(200 * alpha), int(255 * alpha))
        cv2.circle(frame, (px, py), radius, col, -1, cv2.LINE_AA)

    # --- Ponto atual (vetor 2D bruto) ---
    px = int(cx + vx * r)
    py = int(cy + vy * r)
    cv2.line(frame, (cx, cy), (px, py), config.LASER_COLOR, 2, cv2.LINE_AA)
    cv2.circle(frame, (px, py), 6, config.LASER_COLOR, -1, cv2.LINE_AA)
    cv2.circle(frame, (px, py), 6, (255, 255, 255), 1, cv2.LINE_AA)

    # --- Barra de depth_ratio ao lado direito ---
    bx = cx + r + 12
    by_top = cy - r
    by_bot = cy + r
    cv2.rectangle(frame, (bx, by_top), (bx + _BAR_WIDTH, by_bot), (60, 60, 60), -1)
    cv2.rectangle(frame, (bx, by_top), (bx + _BAR_WIDTH, by_bot), (180, 180, 180), 1)

    # range de visualizacao da barra: 0..3 (depth_ratio tipico fica nessa faixa)
    bar_max = 3.0
    ratio_clamped = max(0.0, min(depth_ratio, bar_max))
    fill_h = int((ratio_clamped / bar_max) * (by_bot - by_top))
    fill_color = (0, 200, 0) if depth_ratio >= config.DEPTH_RATIO_THRESHOLD else (0, 80, 220)
    cv2.rectangle(
        frame,
        (bx + 1, by_bot - fill_h),
        (bx + _BAR_WIDTH - 1, by_bot - 1),
        fill_color,
        -1,
    )

    # linha do threshold (FRENTE acende abaixo dela)
    th_y = int(by_bot - (config.DEPTH_RATIO_THRESHOLD / bar_max) * (by_bot - by_top))
    cv2.line(frame, (bx - 3, th_y), (bx + _BAR_WIDTH + 3, th_y), (0, 200, 255), 1)

    # texto numerico de depth_ratio
    cv2.putText(
        frame,
        f"{depth_ratio:.2f}",
        (bx - 6, by_top - 6),
        font,
        0.45,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )
