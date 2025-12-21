"""
Script pentru vizualizarea zonelor de monitorizare desenate pe imagine.

Încarcă o imagine și un fișier de configurație JSON cu zone, apoi afișează
zonele desenate pe imagine pentru validare vizuală.

Usage:
    python view_zones.py --image path/to/image.jpg --zones zones_config.json

Example:
    python view_zones.py --image demo_images/frame.jpg --zones my_zones.json --alpha 0.4
"""

import cv2
import argparse
from zone_monitor import ZoneMonitor


def main():
    """Entry point pentru scriptul de vizualizare zone.
    
    Încarcă imaginea și configurația zonelor, apoi afișează zonele desenate
    pe imagine într-o fereastră OpenCV interactivă.
    """
    parser = argparse.ArgumentParser(description='Vizualizează zonele pe imagine')
    parser.add_argument('--image', '-i', required=True, help='Calea către imagine')
    parser.add_argument('--zones', '-z', required=True, help='Calea către JSON cu zone')
    parser.add_argument('--alpha', '-a', type=float, default=0.3, help='Transparență (0-1)')
    args = parser.parse_args()
    
    # Încarcă imaginea
    image = cv2.imread(args.image)
    if image is None:
        print(f"❌ Nu pot încărca imaginea: {args.image}")
        return
    
    # Încarcă zone monitor
    monitor = ZoneMonitor(args.zones)
    
    # Desenează zonele
    output = monitor.draw_zones(image, alpha=args.alpha, show_labels=True)
    
    # Afișează
    cv2.imshow('Zones Preview', output)
    print("\n✓ Zonele sunt afișate pe imagine")
    print("  • 'q' = închide")
    print("  • 's' = salvează imagine\n")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            output_path = 'zones_preview.jpg'
            cv2.imwrite(output_path, output)
            print(f"📸 Salvat în: {output_path}")
    
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
