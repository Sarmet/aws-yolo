# Zone Monitoring System - README

Sistem de monitorizare a zonelor de interes (ROI) pentru detecția YOLO PPE.

## 📋 Componente

### 1. `draw_zones.py` - Tool pentru desenat zone
Aplicație interactivă pentru desenarea poligoanelor pe imagini.

**Usage:**
```powershell
python draw_zones.py --image demo_images/frame.jpg --output zones_config.json
```

**Controale:**
- **Click stânga** = adaugă punct în poligon
- **Click dreapta** = finalizează poligonul curent
- **'u'** = undo ultimul punct
- **'c'** = șterge zona curentă
- **'r'** = reset tot
- **'s'** = salvează și ieși
- **'q'** = ieși fără salvare

După ce desenezi fiecare zonă, îți cere:
- Nume zonă
- PPE necesar (helmet, vest, gloves, boots)
- Timp maxim de staționare (secunde)
- Acces restricționat (da/nu)

### 2. `zone_monitor.py` - Modul de monitorizare
Biblioteca cu logica pentru verificarea zonelor și regulilor.

**Clase principale:**
- `Detection` - Reprezintă o detecție YOLO
- `ZoneViolation` - Reprezintă o violare
- `ZoneTracker` - Tracking timp petrecut în zone
- `ZoneMonitor` - Logică verificare zone și reguli

**Verificări automate:**
- ✅ PPE necesar în zonă
- ✅ Timp maxim de staționare
- ✅ Acces restricționat

### 3. `inference_with_zones.py` - Inference cu zone
Script complet care combină YOLO cu monitorizarea zonelor.

**Usage:**
```powershell
# Webcam
python inference_with_zones.py --model best.pt --zones zones_config.json --source 0

# Video
python inference_with_zones.py --model best.pt --zones zones_config.json --source video.mp4 --output output.mp4

# Imagine
python inference_with_zones.py --model best.pt --zones zones_config.json --source image.jpg
```

**Controale:**
- **'q'** = oprește
- **'z'** = toggle afișare zone
- **'s'** = screenshot

### 4. `zones_config_example.json` - Exemplu de configurație
Template cu 3 zone pre-configurate.

## 🚀 Workflow

### Pas 1: Desenează zonele
```powershell
# Extrage un frame din video pentru referință
python -c "import cv2; cap=cv2.VideoCapture('video.mp4'); cap.read(); cv2.imwrite('frame.jpg', cap.read()[1])"

# Desenează zonele
python draw_zones.py --image frame.jpg --output my_zones.json
```

### Pas 2: Configurează regulile
Editează `my_zones.json` sau setează regulile când desenezi:

```json
{
  "zones": [
    {
      "id": "zone_1",
      "name": "Zona Periculoasă",
      "polygon": [[x1,y1], [x2,y2], ...],
      "rules": {
        "ppe_required": ["helmet", "vest"],
        "max_dwell_time": 180,
        "restricted_access": false
      }
    }
  ]
}
```

**Reguli disponibile:**
- `ppe_required` - Lista cu PPE necesar: `["helmet", "vest", "gloves", "boots"]`
- `max_dwell_time` - Secunde maxime în zonă (null = nelimitat)
- `restricted_access` - Dacă zona e complet interzisă (true/false)

### Pas 3: Rulează inference
```powershell
python inference_with_zones.py --model best.pt --zones my_zones.json --source video.mp4 --output output.mp4
```

## 📊 Output

### Violări detectate:
- **Missing PPE** (Severity: HIGH) - Roșu
  - "PPE lipsă în Zona X: helmet, vest"
  
- **Dwell time exceeded** (Severity: MEDIUM) - Portocaliu
  - "Timp depășit în Zona X: 200s / 180s"
  
- **Restricted access** (Severity: HIGH) - Roșu
  - "Acces neautorizat în Zona X"

### Vizualizare:
- Zone desenate cu transparență
- Bounding boxes pentru detectări
- Highlight roșu pentru violări
- Text cu descrierea violării
- Statistici în colț (frame, persoane, violări)

## 🎯 Use Cases

### 1. Zonă periculoasă - PPE obligatoriu
```json
{
  "rules": {
    "ppe_required": ["helmet", "vest"],
    "max_dwell_time": null,
    "restricted_access": false
  }
}
```
→ Alarma dacă cineva intră fără PPE

### 2. Zonă temporară - Timp limitat
```json
{
  "rules": {
    "ppe_required": [],
    "max_dwell_time": 180,
    "restricted_access": false
  }
}
```
→ Alarma dacă cineva stă > 3 minute

### 3. Zonă interzisă
```json
{
  "rules": {
    "ppe_required": ["helmet", "vest", "gloves"],
    "max_dwell_time": null,
    "restricted_access": true
  }
}
```
→ Alarma instant la intrare

### 4. Combinat - PPE + Timp
```json
{
  "rules": {
    "ppe_required": ["helmet"],
    "max_dwell_time": 300,
    "restricted_access": false
  }
}
```
→ Alarma pentru PPE SAU timp depășit

## 🔧 Integrare în sistem existent

### Cod minimal:
```python
from zone_monitor import ZoneMonitor, Detection

# Setup
monitor = ZoneMonitor('zones_config.json')

# În loop-ul de inference
violations = monitor.check_violations(
    person_detections=person_list,
    ppe_detections=ppe_list
)

# Handle violations
for v in violations:
    if v.severity == 'high':
        send_alarm(v.message)
```

## 📝 Notes

- Poligoanele pot avea orice formă (3+ puncte)
- Tracking-ul timpului necesită track_id (ex: DeepSORT, ByteTrack)
- Verificarea PPE se bazează pe overlap între bbox persoană și bbox PPE
- Cleanup automat al tracking-ului după 5 minute

## 🎨 Customizare

### Adaugă noi tipuri de PPE:
```python
# În zone_monitor.py
PPE_CLASSES = {
    'helmet': ['Hardhat', 'helmet', 'hard-hat'],
    'vest': ['Safety Vest', 'vest', 'hi-vis'],
    'mask': ['face-mask', 'respirator'],  # NOU
}
```

### Schimbă culori:
```python
# În draw_zones.py
self.colors = [
    (255, 0, 0),  # Albastru
    (0, 255, 0),  # Verde
    # ...
]
```

## 📚 Dependencies

```
opencv-python
numpy
ultralytics
```

Instalare:
```powershell
pip install opencv-python numpy ultralytics
```
