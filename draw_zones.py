"""
Tool pentru desenarea zonelor de monitorizare (ROI - Regions of Interest)
Permite desenarea poligoanelor pe o imagine și salvarea coordonatelor în JSON.

Usage:
    python draw_zones.py --image path/to/image.jpg --output zones_config.json
"""

import cv2
import numpy as np
import json
import argparse
from pathlib import Path


class ZoneDrawer:
    """Tool interactiv pentru desenarea zonelor de monitorizare pe imagini.
    
    Permite utilizatorului să deseneze poligoane pe o imagine de referință și să
    configureze reguli pentru fiecare zonă (PPE necesar, timp maxim, acces restricționat).
    
    Attributes:
        image (np.ndarray): Imaginea originală.
        display_image (np.ndarray): Imaginea curentă afișată cu zonele desenate.
        zones (list): Lista zonelor finalizate.
        current_zone (list): Lista punctelor pentru zona curentă în curs de desenare.
        drawing (bool): Flag pentru starea de desenare.
        colors (list): Lista culorilor pentru zone.
    
    Example:
        >>> drawer = ZoneDrawer('frame.jpg')
        >>> zones = drawer.draw()
        >>> print(f"Desenate {len(zones)} zone")
    """
    
    def __init__(self, image_path):
        """Inițializează drawer-ul cu o imagine.
        
        Args:
            image_path (str | Path): Calea către imaginea de referință.
            
        Raises:
            ValueError: Dacă imaginea nu poate fi încărcată.
        """
        self.image = cv2.imread(str(image_path))
        if self.image is None:
            raise ValueError(f"Nu pot încărca imaginea: {image_path}")
        
        self.display_image = self.image.copy()
        self.zones = []
        self.current_zone = []
        self.drawing = False
        
        # Culori pentru zone
        self.colors = [
            (0, 255, 0),    # Verde
            (0, 0, 255),    # Roșu
            (255, 0, 0),    # Albastru
            (0, 255, 255),  # Galben
            (255, 0, 255),  # Magenta
        ]
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handler pentru evenimentele mouse-ului.
        
        Procesează click-urile mouse-ului pentru desenarea poligoanelor:
        - Click stânga: adaugă un punct nou în poligonul curent
        - Click dreapta: finalizează poligonul curent
        
        Args:
            event (int): Tipul evenimentului OpenCV.
            x (int): Coordonata X a mouse-ului.
            y (int): Coordonata Y a mouse-ului.
            flags (int): Flag-uri suplimentare OpenCV.
            param: Parametri suplimentari (neutilizați).
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            # Adaugă punct în poligonul curent
            self.current_zone.append([x, y])
            cv2.circle(self.display_image, (x, y), 5, (0, 255, 255), -1)
            
            # Desenează linie între puncte
            if len(self.current_zone) > 1:
                cv2.line(
                    self.display_image,
                    tuple(self.current_zone[-2]),
                    tuple(self.current_zone[-1]),
                    (0, 255, 255),
                    2
                )
            
            cv2.imshow('Zone Drawer', self.display_image)
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Click dreapta = finalizează poligonul curent
            if len(self.current_zone) >= 3:
                self.zones.append({
                    'polygon': self.current_zone.copy(),
                    'name': f'zone_{len(self.zones) + 1}'
                })
                
                # Desenează poligonul final
                color = self.colors[len(self.zones) - 1 % len(self.colors)]
                cv2.polylines(
                    self.display_image,
                    [np.array(self.current_zone)],
                    True,
                    color,
                    2
                )
                cv2.fillPoly(
                    self.display_image,
                    [np.array(self.current_zone)],
                    (*color[:3], 50)  # Semi-transparent
                )
                
                print(f"✓ Zona {len(self.zones)} salvată cu {len(self.current_zone)} puncte")
                self.current_zone = []
                cv2.imshow('Zone Drawer', self.display_image)
    
    def draw(self):
        """Pornește interfața interactivă de desenare.
        
        Afișează fereastra OpenCV și procesează input-ul utilizatorului pentru
        desenarea și configurarea zonelor de monitorizare.
        
        Returns:
            list[dict] | None: Lista cu zonele desenate sau None dacă utilizatorul anulează.
            
        Note:
            Controale disponibile:
            - Click stânga: adaugă punct
            - Click dreapta: finalizează zona
            - 'u': undo ultimul punct
            - 'c': șterge zona curentă
            - 'r': reset toate zonele
            - 's': salvează și ieși
            - 'q': ieși fără salvare
        """
        cv2.namedWindow('Zone Drawer')
        cv2.setMouseCallback('Zone Drawer', self.mouse_callback)
        
        # Afișează instrucțiuni
        print("\n" + "="*60)
        print("INSTRUCȚIUNI:")
        print("  • Click STÂNGA = adaugă punct în poligon")
        print("  • Click DREAPTA = finalizează poligonul curent")
        print("  • 'u' = undo ultimul punct")
        print("  • 'c' = șterge zona curentă")
        print("  • 'r' = reset tot (șterge toate zonele)")
        print("  • 's' = salvează și ieși")
        print("  • 'q' = ieși fără a salva")
        print("="*60 + "\n")
        
        cv2.imshow('Zone Drawer', self.display_image)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                # Quit fără a salva
                print("Închidere fără salvare...")
                cv2.destroyAllWindows()
                return None
                
            elif key == ord('s'):
                # Salvează și ieși
                if len(self.zones) == 0:
                    print("⚠ Nicio zonă desenată! Desenează cel puțin o zonă.")
                    continue
                cv2.destroyAllWindows()
                return self.zones
                
            elif key == ord('u'):
                # Undo ultimul punct
                if len(self.current_zone) > 0:
                    self.current_zone.pop()
                    self.redraw()
                    
            elif key == ord('c'):
                # Clear zona curentă
                self.current_zone = []
                self.redraw()
                print("Zona curentă ștearsă")
                
            elif key == ord('r'):
                # Reset tot
                self.zones = []
                self.current_zone = []
                self.redraw()
                print("Toate zonele șterse")
    
    def redraw(self):
        """Redesenează imaginea cu toate zonele salvate și zona curentă.
        
        Actualizează display_image cu imaginea originală, apoi desenează toate
        zonele finalizate și punctele zonei curente în curs de desenare.
        """
        self.display_image = self.image.copy()
        
        # Redesenează zonele salvate
        for i, zone_data in enumerate(self.zones):
            color = self.colors[i % len(self.colors)]
            polygon = zone_data['polygon']
            cv2.polylines(
                self.display_image,
                [np.array(polygon)],
                True,
                color,
                2
            )
        
        # Redesenează zona curentă
        if len(self.current_zone) > 0:
            for i, point in enumerate(self.current_zone):
                cv2.circle(self.display_image, tuple(point), 5, (0, 255, 255), -1)
                if i > 0:
                    cv2.line(
                        self.display_image,
                        tuple(self.current_zone[i-1]),
                        tuple(point),
                        (0, 255, 255),
                        2
                    )
        
        cv2.imshow('Zone Drawer', self.display_image)


def main():
    """Entry point pentru tool-ul de desenare zone.
    
    Parsează argumentele din linia de comandă, încarcă imaginea, permite
    desenarea zonelor, colectează configurația regulilor și salvează rezultatul în JSON.
    """
    parser = argparse.ArgumentParser(description='Desenează zone de monitorizare pe imagine')
    parser.add_argument('--image', '-i', required=True, help='Calea către imagine')
    parser.add_argument('--output', '-o', default='zones_config.json', help='Fișier output JSON')
    args = parser.parse_args()
    
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"❌ Imaginea nu există: {image_path}")
        return
    
    drawer = ZoneDrawer(image_path)
    zones = drawer.draw()
    
    if zones is None:
        print("Operație anulată.")
        return
    
    # Pregătește configurația
    config = {
        "image_reference": str(image_path),
        "image_size": {
            "width": drawer.image.shape[1],
            "height": drawer.image.shape[0]
        },
        "zones": []
    }
    
    # Adaugă informații pentru fiecare zonă
    for i, zone_data in enumerate(zones):
        zone_name = input(f"\nNumele pentru zona {i+1} (default: {zone_data['name']}): ").strip()
        if not zone_name:
            zone_name = zone_data['name']
        
        print(f"\nReguli pentru zona '{zone_name}':")
        print("  1. PPE necesar (helmet, vest, gloves, boots)")
        print("  2. Timp maxim de staționare (secunde)")
        print("  3. Acces restricționat (da/nu)")
        
        ppe_input = input("PPE necesar (ex: helmet,vest sau enter pentru nimic): ").strip()
        ppe_required = [x.strip() for x in ppe_input.split(',')] if ppe_input else []
        
        dwell_input = input("Timp maxim staționare în secunde (enter pentru nelimitat): ").strip()
        max_dwell_time = int(dwell_input) if dwell_input.isdigit() else None
        
        restricted = input("Acces restricționat? (y/n, default=n): ").strip().lower() == 'y'
        
        zone_config = {
            "id": f"zone_{i+1}",
            "name": zone_name,
            "polygon": zone_data['polygon'],
            "rules": {
                "ppe_required": ppe_required,
                "max_dwell_time": max_dwell_time,
                "restricted_access": restricted
            }
        }
        
        config["zones"].append(zone_config)
    
    # Salvează în JSON
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Configurație salvată în: {output_path}")
    print(f"  Total zone: {len(zones)}")


if __name__ == "__main__":
    main()
