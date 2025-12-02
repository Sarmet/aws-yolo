# PPE Detection - YOLO11

Detectare echipament de protecție (căști, mănuși, ochelari, etc.) cu YOLO11.

## Quick Start (5 minute)

### 1. Instalare dependențe
```bash
pip install ultralytics opencv-python matplotlib
```

### 2. Rulare notebook
Deschide `validation.ipynb` și rulează toate celulele (Run All).

**Ce vei vedea:**
- Model încărcat: `yolo11_balanced` (antrenat pe 2147 imagini cu căști)
- 5 imagini demo cu detecții
- Rezultate: helmet, no_helmet, goggles, etc.

## Structura

```
ppe_detection_yolo/
├── validation.ipynb          # ← RULEAZĂ ASTA
├── demo_images/              # 5 imagini de test (~150KB)
├── ppe_training/
│   └── yolo11_balanced/
│       └── weights/
│           └── best.pt       # Modelul antrenat (~5MB)
└── README.md
```

## Clase detectate

| ID | Clasă |
|----|-------|
| 0 | glove |
| 1 | goggles |
| 2 | helmet |
| 3 | mask |
| 4 | no_glove |
| 5 | no_goggles |
| 6 | no_helmet |
| 7 | no_mask |
| 8 | no_shoes |
| 9 | shoes |

## Rezultate așteptate

```
005302_jpg...: helmet (0.59)
005315_jpg...: helmet (0.67), helmet (0.45)
005330_jpg...: helmet (0.95), helmet (0.92), helmet (0.51)
005399_jpg...: helmet (0.89), helmet (0.43)
005424_jpg...: no_helmet (0.87), no_helmet (0.87), ...
```
