"""Constantes globais do protótipo de hand tracking laser pointer."""

# Câmera
CAM_INDEX = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480

# MediaPipe Hands
MAX_HANDS = 1
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.5

# Índices dos landmarks usados (MediaPipe Hands)
WRIST = 0
INDEX_MCP = 5
INDEX_TIP = 8

# Thresholds de classificação de direção
# Quão dominante um eixo precisa ser sobre o outro (em fração 0..1)
DIRECTION_THRESHOLD = 0.3
# Razão dist(wrist,tip)/dist(wrist,mcp) abaixo da qual consideramos "FRENTE".
# Em pose neutra (mão de lado para a câmera) essa razão fica ~2.5–3.0.
# Quando a mão aponta para a câmera, ela cai bastante.
DEPTH_RATIO_THRESHOLD = 1.2

# Visual
LASER_COLOR = (0, 0, 255)        # Vermelho (BGR)
LASER_THICKNESS = 3
LASER_LENGTH = 200               # Comprimento da linha do laser em pixels

TEXT_COLOR = (0, 255, 0)         # Verde (BGR)
TEXT_POSITION = (10, 30)
TEXT_SCALE = 0.8
TEXT_THICKNESS = 2

FPS_COLOR = (255, 255, 0)        # Ciano (BGR)

# Direções possíveis
DIR_UP = "CIMA"
DIR_DOWN = "BAIXO"
DIR_LEFT = "ESQUERDA"
DIR_RIGHT = "DIREITA"
DIR_FORWARD = "FRENTE"
