"""
Modul pentru monitorizarea zonelor de interes (ROI)
Verifică dacă detectările sunt în poligoane și aplică reguli specifice.
"""

import cv2
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Detection:
    """Reprezintă o detecție YOLO cu informații despre locație și clasă.
    
    Attributes:
        bbox (Tuple[int, int, int, int]): Bounding box (x1, y1, x2, y2).
        class_name (str): Numele clasei detectate.
        confidence (float): Scor de încredere (0-1).
        track_id (Optional[int]): ID-ul de tracking (dacă este disponibil).
    
    Example:
        >>> det = Detection(bbox=(100, 100, 200, 200), class_name='person', confidence=0.95)
        >>> print(det.center)  # (150, 150)
    """
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    class_name: str
    confidence: float
    track_id: Optional[int] = None
    
    @property
    def center(self) -> Tuple[int, int]:
        """Calculează și returnează centrul bounding box-ului.
        
        Returns:
            Tuple[int, int]: Coordonatele (x, y) ale centrului.
        """
        x1, y1, x2, y2 = self.bbox
        return (int((x1 + x2) / 2), int((y1 + y2) / 2))


@dataclass
class ZoneViolation:
    """Reprezintă o violare a regulilor unei zone de monitorizare.
    
    Attributes:
        zone_id (str): ID-ul unic al zonei.
        zone_name (str): Numele zonei.
        violation_type (str): Tipul violării ('missing_ppe', 'dwell_time_exceeded', 'restricted_access').
        detection (Detection): Detecția care a cauzat violarea.
        message (str): Mesaj descriptiv pentru violarea.
        timestamp (datetime): Momentul în care a fost detectată violarea.
        severity (str): Severitatea violării ('low', 'medium', 'high').
    """
    zone_id: str
    zone_name: str
    violation_type: str
    detection: Detection
    message: str
    timestamp: datetime
    severity: str  # 'low', 'medium', 'high'


class ZoneTracker:
    """Tracking pentru timpul petrecut de obiecte în zone.
    
    Menține evidența momentului în care fiecare obiect tracked a intrat într-o zonă
    și calculează timpul de staționare.
    
    Attributes:
        zone_entries (dict): Dicționar {(track_id, zone_id): entry_time}.
    
    Example:
        >>> tracker = ZoneTracker()
        >>> dwell_time = tracker.update(track_id=5, zone_id='zone_1', current_time=datetime.now())
        >>> print(f"Timp în zonă: {dwell_time:.1f}s")
    """
    
    def __init__(self):
        """Inițializează tracker-ul cu un dicționar gol."""
        self.zone_entries = {}  # {(track_id, zone_id): entry_time}
    
    def update(self, track_id: int, zone_id: str, current_time: datetime) -> Optional[float]:
        """Actualizează tracking-ul și returnează timpul petrecut în zonă.
        
        Args:
            track_id (int): ID-ul obiectului tracked.
            zone_id (str): ID-ul zonei.
            current_time (datetime): Timestamp-ul curent.
            
        Returns:
            Optional[float]: Timpul petrecut în zonă în secunde, sau 0 la prima intrare.
        """
        key = (track_id, zone_id)
        
        if key not in self.zone_entries:
            self.zone_entries[key] = current_time
            return 0.0
        
        dwell_time = (current_time - self.zone_entries[key]).total_seconds()
        return dwell_time
    
    def remove(self, track_id: int, zone_id: str):
        """Elimină tracking-ul când obiectul părăsește zona.
        
        Args:
            track_id (int): ID-ul obiectului tracked.
            zone_id (str): ID-ul zonei.
        """
        key = (track_id, zone_id)
        if key in self.zone_entries:
            del self.zone_entries[key]
    
    def cleanup_old_entries(self, max_age_seconds: int = 300):
        """Curăță entry-urile vechi pentru a elibera memorie.
        
        Args:
            max_age_seconds (int): Vechimea maximă în secunde (default: 300 = 5 minute).
        """
        current_time = datetime.now()
        to_remove = []
        
        for key, entry_time in self.zone_entries.items():
            age = (current_time - entry_time).total_seconds()
            if age > max_age_seconds:
                to_remove.append(key)
        
        for key in to_remove:
            del self.zone_entries[key]


class ZoneMonitor:
    """Monitorizează zonele de interes și aplică reguli de siguranță.
    
    Verifică dacă detectările YOLO se află în zonele configurate și validează
    respectarea regulilor (PPE necesar, timp de staționare, acces restricționat).
    
    Attributes:
        config_path (Path): Calea către fișierul de configurație JSON.
        config (dict): Configurația încărcată.
        zones (list): Lista zonelor din configurație.
        tracker (ZoneTracker): Tracker pentru timpul de staționare.
        PPE_CLASSES (dict): Mapare între tipuri PPE și clasele YOLO.
    
    Example:
        >>> monitor = ZoneMonitor('zones_config.json')
        >>> violations = monitor.check_violations(person_detections, ppe_detections)
        >>> for v in violations:
        ...     print(f"Violare: {v.message}")
    """
    
    # Mapare clase PPE
    PPE_CLASSES = {
        'helmet': ['Hardhat', 'helmet'],
        'vest': ['Safety Vest', 'vest'],
        'gloves': ['gloves'],
        'boots': ['boots', 'safety-boots']
    }
    
    def __init__(self, config_path: str):
        """
        Args:
            config_path: Calea către fișierul JSON cu configurația zonelor
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.zones = self.config.get('zones', [])
        self.tracker = ZoneTracker()
        
        # Pre-convertește poligoanele în numpy arrays
        for zone in self.zones:
            zone['polygon_np'] = np.array(zone['polygon'], dtype=np.int32)
    
    def _load_config(self) -> Dict:
        """Încarcă configurația din JSON"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config nu există: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def point_in_polygon(self, point: Tuple[int, int], polygon: np.ndarray) -> bool:
        """
        Verifică dacă un punct este în poligon folosind OpenCV
        """
        result = cv2.pointPolygonTest(polygon, point, False)
        return result >= 0  # >= 0 înseamnă interior sau pe contur
    
    def get_zone_for_point(self, point: Tuple[int, int]) -> Optional[Dict]:
        """
        Returnează zona în care se află punctul (sau None)
        """
        for zone in self.zones:
            if self.point_in_polygon(point, zone['polygon_np']):
                return zone
        return None
    
    def check_ppe_requirements(self, 
                               person_detection: Detection,
                               ppe_detections: List[Detection],
                               required_ppe: List[str]) -> List[str]:
        """
        Verifică ce PPE lipsește
        
        Returns:
            Lista cu PPE-uri care lipsesc
        """
        if not required_ppe:
            return []
        
        # Verifică ce PPE este detectat în apropierea persoanei
        px1, py1, px2, py2 = person_detection.bbox
        person_area = (px1, py1, px2, py2)
        
        detected_ppe = set()
        
        for ppe in ppe_detections:
            # Verifică overlap între persoană și PPE
            ppx1, ppy1, ppx2, ppy2 = ppe.bbox
            
            # IoU simplu sau verificare că PPE e în bbox persoană
            if self._boxes_overlap(person_area, (ppx1, ppy1, ppx2, ppy2)):
                # Identifică tipul PPE
                for ppe_type, class_names in self.PPE_CLASSES.items():
                    if any(cn.lower() in ppe.class_name.lower() for cn in class_names):
                        detected_ppe.add(ppe_type)
        
        # Ce lipsește?
        missing = [ppe for ppe in required_ppe if ppe not in detected_ppe]
        return missing
    
    def _boxes_overlap(self, box1: Tuple, box2: Tuple) -> bool:
        """Verifică dacă două bounding boxes se suprapun"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        return not (x2_1 < x1_2 or x2_2 < x1_1 or y2_1 < y1_2 or y2_2 < y1_1)
    
    def check_violations(self,
                        person_detections: List[Detection],
                        ppe_detections: List[Detection],
                        current_time: Optional[datetime] = None) -> List[ZoneViolation]:
        """Verifică toate violările pentru frame-ul curent.
        
        Analizează fiecare persoană detectată și verifică:
        - Dacă se află într-o zonă monitorizată
        - Dacă poartă PPE-ul necesar pentru zona respectivă
        - Dacă a depășit timpul maxim de staționare
        - Dacă are acces în zona restricționată
        
        Args:
            person_detections (List[Detection]): Lista cu detectări de persoane.
            ppe_detections (List[Detection]): Lista cu detectări de PPE.
            current_time (Optional[datetime]): Timestamp-ul curent (default: datetime.now()).
            
        Returns:
            List[ZoneViolation]: Lista cu toate violările detectate în frame.
        """
        if current_time is None:
            current_time = datetime.now()
        
        violations = []
        
        for person in person_detections:
            center = person.center
            zone = self.get_zone_for_point(center)
            
            if zone is None:
                continue  # Persoana nu e în nicio zonă
            
            rules = zone.get('rules', {})
            zone_id = zone['id']
            zone_name = zone['name']
            
            # 1. Verifică PPE necesar
            required_ppe = rules.get('ppe_required', [])
            if required_ppe:
                missing_ppe = self.check_ppe_requirements(
                    person, ppe_detections, required_ppe
                )
                if missing_ppe:
                    violations.append(ZoneViolation(
                        zone_id=zone_id,
                        zone_name=zone_name,
                        violation_type='missing_ppe',
                        detection=person,
                        message=f"PPE lipsă în {zone_name}: {', '.join(missing_ppe)}",
                        timestamp=current_time,
                        severity='high'
                    ))
            
            # 2. Verifică timp de staționare
            max_dwell = rules.get('max_dwell_time')
            if max_dwell and person.track_id is not None:
                dwell_time = self.tracker.update(person.track_id, zone_id, current_time)
                
                if dwell_time > max_dwell:
                    violations.append(ZoneViolation(
                        zone_id=zone_id,
                        zone_name=zone_name,
                        violation_type='dwell_time_exceeded',
                        detection=person,
                        message=f"Timp depășit în {zone_name}: {int(dwell_time)}s / {max_dwell}s",
                        timestamp=current_time,
                        severity='medium'
                    ))
            
            # 3. Verifică acces restricționat
            if rules.get('restricted_access', False):
                violations.append(ZoneViolation(
                    zone_id=zone_id,
                    zone_name=zone_name,
                    violation_type='restricted_access',
                    detection=person,
                    message=f"Acces neautorizat în {zone_name}",
                    timestamp=current_time,
                    severity='high'
                ))
        
        return violations
    
    def draw_zones(self, image: np.ndarray, 
                   alpha: float = 0.3,
                   show_labels: bool = True) -> np.ndarray:
        """Desenează zonele de monitorizare pe imagine.
        
        Args:
            image (np.ndarray): Imaginea pe care să deseneze zonele.
            alpha (float): Transparența fill-ului (0-1, default: 0.3).
            show_labels (bool): Dacă să afișeze numele zonelor (default: True).
            
        Returns:
            np.ndarray: Imaginea cu zonele desenate.
        """
        overlay = image.copy()
        output = image.copy()
        
        colors = [
            (0, 255, 0),    # Verde
            (0, 0, 255),    # Roșu
            (255, 0, 0),    # Albastru
            (0, 255, 255),  # Galben
            (255, 0, 255),  # Magenta
        ]
        
        for i, zone in enumerate(self.zones):
            color = colors[i % len(colors)]
            polygon = zone['polygon_np']
            
            # Fill semi-transparent
            cv2.fillPoly(overlay, [polygon], color)
            
            # Contur
            cv2.polylines(output, [polygon], True, color, 2)
            
            # Label
            if show_labels:
                # Calculează centroid pentru text
                M = cv2.moments(polygon)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    text = zone['name']
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(output, text, (cx - 50, cy),
                              font, 0.6, (255, 255, 255), 2)
        
        # Blend
        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        
        return output
    
    def draw_violations(self, image: np.ndarray, 
                       violations: List[ZoneViolation]) -> np.ndarray:
        """Desenează violările pe imagine cu bounding boxes și text.
        
        Args:
            image (np.ndarray): Imaginea pe care să deseneze.
            violations (List[ZoneViolation]): Lista cu violările de desenat.
            
        Returns:
            np.ndarray: Imaginea cu violările vizualizate.
            
        Note:
            Culoarea bounding box-ului depinde de severity:
            - high: roșu
            - medium: portocaliu
            - low: galben
        """
        output = image.copy()
        
        for violation in violations:
            bbox = violation.detection.bbox
            x1, y1, x2, y2 = bbox
            
            # Culoare în funcție de severity
            if violation.severity == 'high':
                color = (0, 0, 255)  # Roșu
            elif violation.severity == 'medium':
                color = (0, 165, 255)  # Portocaliu
            else:
                color = (0, 255, 255)  # Galben
            
            # Desenează bbox
            cv2.rectangle(output, (x1, y1), (x2, y2), color, 3)
            
            # Text cu violarea
            text = violation.message
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            # Background pentru text
            (text_w, text_h), _ = cv2.getTextSize(text, font, 0.5, 2)
            cv2.rectangle(output, (x1, y1 - text_h - 10), 
                         (x1 + text_w, y1), color, -1)
            cv2.putText(output, text, (x1, y1 - 5),
                       font, 0.5, (255, 255, 255), 2)
        
        return output


def load_zone_monitor(config_path: str) -> ZoneMonitor:
    """Helper function pentru încărcarea unui ZoneMonitor.
    
    Args:
        config_path (str): Calea către fișierul de configurație JSON.
        
    Returns:
        ZoneMonitor: Instanță configurată de ZoneMonitor.
        
    Example:
        >>> monitor = load_zone_monitor('zones_config.json')
    """
    return ZoneMonitor(config_path)
