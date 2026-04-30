"""Cálculo do vetor de apontamento e classificação de direção."""

import math

import config


def _lm_xy(landmarks, idx, frame_w, frame_h):
    """Converte um landmark normalizado em coordenadas de pixel (x, y).

    `landmarks` eh uma lista de NormalizedLandmark (Tasks API)."""
    lm = landmarks[idx]
    return (lm.x * frame_w, lm.y * frame_h)


def pointing_vector(landmarks, frame_w, frame_h):
    """Calcula o vetor de apontamento.

    Retorna (origin_xy, vec_xy_norm, depth_ratio):
      origin_xy: pixel (x, y) da ponta do indicador (landmark 8)
      vec_xy_norm: vetor unitário 2D (vx, vy) do pulso até a ponta do indicador
      depth_ratio: dist(wrist, tip) / dist(wrist, mcp). Cai quando a mão
                   aponta para a câmera (encurtamento por perspectiva).
    """
    wrist = _lm_xy(landmarks, config.WRIST, frame_w, frame_h)
    mcp = _lm_xy(landmarks, config.INDEX_MCP, frame_w, frame_h)
    tip = _lm_xy(landmarks, config.INDEX_TIP, frame_w, frame_h)

    vx = tip[0] - wrist[0]
    vy = tip[1] - wrist[1]
    length = math.hypot(vx, vy)

    if length < 1e-6:
        vec_norm = (0.0, 0.0)
    else:
        vec_norm = (vx / length, vy / length)

    mcp_dist = math.hypot(mcp[0] - wrist[0], mcp[1] - wrist[1])
    if mcp_dist < 1e-6:
        depth_ratio = 0.0
    else:
        depth_ratio = length / mcp_dist

    return tip, vec_norm, depth_ratio


def classify_direction(vec_xy, depth_ratio):
    """Classifica a direção em CIMA/BAIXO/ESQUERDA/DIREITA/FRENTE.

    No OpenCV, Y cresce para baixo:
      vy < 0 → CIMA
      vy > 0 → BAIXO
      vx < 0 → ESQUERDA
      vx > 0 → DIREITA
    Se o vetor 2D ficou curto em relação à largura da palma, a mão está
    apontando para a câmera → FRENTE.
    """
    if depth_ratio < config.DEPTH_RATIO_THRESHOLD:
        return config.DIR_FORWARD

    vx, vy = vec_xy
    ax, ay = abs(vx), abs(vy)

    # Eixo dominante precisa exceder o outro pelo threshold para evitar
    # oscilação em direções diagonais.
    if ay > ax and (ay - ax) > config.DIRECTION_THRESHOLD:
        return config.DIR_UP if vy < 0 else config.DIR_DOWN
    if ax > ay and (ax - ay) > config.DIRECTION_THRESHOLD:
        return config.DIR_LEFT if vx < 0 else config.DIR_RIGHT

    # Diagonal / indefinido: escolhe o eixo levemente dominante mesmo assim
    if ay >= ax:
        return config.DIR_UP if vy < 0 else config.DIR_DOWN
    return config.DIR_LEFT if vx < 0 else config.DIR_RIGHT
