# Hand Laser Tracker

Protótipo em Python que detecta uma mão pela webcam, calcula a direção para
onde o dedo indicador aponta e desenha um "laser virtual" sobre o vídeo em
tempo real. É a base para um projeto futuro com **ESP32-CAM + Arduino + servos**,
em que um laser físico replicará o movimento da mão da pessoa.

## Como funciona

1. `MediaPipe Hands` detecta os 21 landmarks da mão.
2. O vetor de apontamento é calculado do **pulso (landmark 0)** até a
   **ponta do indicador (landmark 8)**.
3. A razão `dist(pulso, ponta) / dist(pulso, base do indicador)` serve para
   detectar quando a mão aponta para a câmera (encurtamento por perspectiva
   → direção `FRENTE`).
4. O componente dominante do vetor 2D classifica em `CIMA`, `BAIXO`,
   `ESQUERDA` ou `DIREITA`.
5. O OpenCV desenha os landmarks, uma linha vermelha (laser virtual), o texto
   da direção atual, FPS e uma bússola.

## Estrutura

```
laser_pointer/
├── main.py            # Loop principal: câmera + render
├── hand_detector.py   # Wrapper fino sobre MediaPipe Hands
├── direction_calc.py  # Vetor de apontamento e classificação de direção
├── visualizer.py      # Funções de desenho (landmarks, laser, texto, bússola)
├── config.py          # Constantes (câmera, thresholds, cores)
├── requirements.txt
└── README.md
```

## Instalação

> **Atenção sobre versão do Python:** o MediaPipe ainda **não** publica wheels
> para Python 3.13+. Se o seu `python3 --version` for ≥ 3.13, use um Python
> 3.11 ou 3.12 em um virtualenv dedicado.

```bash
# se necessário, criar venv com Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Como rodar

```bash
python main.py
```

Aponte sua mão para a câmera com o indicador estendido. A direção classificada
aparece no canto superior esquerdo e o laser vermelho sai da ponta do dedo.
Sair com a tecla **`q`**.

## Ajuste de thresholds

Edite `config.py`:

- `DIRECTION_THRESHOLD` (padrão `0.3`) — quão dominante um eixo precisa ser
  para evitar oscilação em direções diagonais. Aumente se a classificação
  pular muito entre direções.
- `DEPTH_RATIO_THRESHOLD` (padrão `1.2`) — abaixo desse valor, a mão é
  considerada apontando para a câmera (`FRENTE`). Diminua se ele acionar
  cedo demais; aumente se nunca acionar.
- `LASER_LENGTH` — comprimento da linha do laser em pixels.
- `CAM_WIDTH` / `CAM_HEIGHT` — resolução. 640x480 já é suficiente.

## Próximos passos (porte para ESP32-CAM)

1. **Modelo enxuto:** trocar MediaPipe (CPU) por um modelo TFLite Micro de
   detecção de mão rodando no próprio ESP32-CAM, ou enviar frames JPEG via
   Wi-Fi para um host fazendo a inferência.
2. **Comunicação com Arduino:** mapear a direção classificada em ângulos de
   dois servos (pan/tilt) e enviar via UART/I2C.
3. **Laser físico:** módulo laser de 5 mW controlado por GPIO; ligar apenas
   quando uma mão é detectada (segurança).
4. **Calibração:** rotina inicial em que a pessoa aponta nas 4 direções para
   ajustar `DIRECTION_THRESHOLD` e o range dos servos.
# laser_pointer
