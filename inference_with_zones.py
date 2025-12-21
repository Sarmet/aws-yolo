"""
Demo inference YOLO cu monitorizarea zonelor
Detectează persoane și PPE, apoi verifică violările în zone.
"""

import cv2
import argparse
from pathlib import Path
from ultralytics import YOLO
from zone_monitor import ZoneMonitor, Detection
from datetime import datetime


def run_inference_with_zones(
    model_path: str,
    zones_config: str,
    source: str,
    output: str = None,
    conf_threshold: float = 0.5
):
    """Rulează inference YOLO cu monitorizare zone și detecție violări.
    
    Procesează un stream video (webcam, fișier video, imagine) cu un model YOLO,
    verifică dacă detectările sunt în zonele configurate și afișează violările
    regulilor de siguranță în timp real.
    
    Args:
        model_path (str): Calea către modelul YOLO (.pt).
        zones_config (str): Calea către fișierul de configurație JSON cu zone.
        source (str): Sursa video ('0' pentru webcam, path pentru fișier).
        output (str, optional): Calea pentru salvarea video-ului procesat.
        conf_threshold (float): Threshold pentru confidence score (default: 0.5).
    
    Raises:
        ValueError: Dacă sursa video nu poate fi deschisă.
    
    Example:
        >>> run_inference_with_zones(
        ...     model_path='best.pt',
        ...     zones_config='zones.json',
        ...     source='0',  # webcam
        ...     conf_threshold=0.6
        ... )
    
    Note:
        Controale keyboard:
        - 'q': oprește procesarea
        - 'z': toggle afișare zone
        - 's': salvează screenshot
    """
    # Încarcă modelul YOLO
    print(f"📦 Încărcare model: {model_path}")
    model = YOLO(model_path)
    
    # Încarcă zone monitor
    print(f"🗺️  Încărcare configurație zone: {zones_config}")
    zone_monitor = ZoneMonitor(zones_config)
    
    # Deschide sursa video
    if source.isdigit():
        source = int(source)
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"❌ Nu pot deschide sursa: {source}")
        return
    
    # Pregătește writer pentru output (dacă e cazul)
    writer = None
    if output:
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output, fourcc, fps, (width, height))
        print(f"💾 Salvare output: {output}")
    
    print("\n▶️  Pornire inference...")
    print("  • 'q' = oprește")
    print("  • 'z' = toggle afișare zone")
    print("  • 's' = screenshot\n")
    
    show_zones = True
    frame_count = 0
    
    # Mapare clase pentru identificare ușoară
    PERSON_CLASSES = ['person', 'Person', 'NO-Person']
    PPE_CLASSES = ['Hardhat', 'Safety Vest', 'NO-Hardhat', 'NO-Safety Vest',
                   'helmet', 'vest', 'gloves', 'boots']
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            current_time = datetime.now()
            
            # Rulează YOLO
            results = model(frame, conf=conf_threshold, verbose=False)[0]
            
            # Separă detectările în persoane și PPE
            person_detections = []
            ppe_detections = []
            
            for detection in results.boxes.data:
                x1, y1, x2, y2, conf, cls = detection.cpu().numpy()
                class_name = model.names[int(cls)]
                
                det = Detection(
                    bbox=(int(x1), int(y1), int(x2), int(y2)),
                    class_name=class_name,
                    confidence=float(conf),
                    track_id=None  # Poți adăuga tracking aici
                )
                
                # Clasifică
                if any(pc in class_name for pc in PERSON_CLASSES):
                    person_detections.append(det)
                elif any(pc in class_name for pc in PPE_CLASSES):
                    ppe_detections.append(det)
            
            # Verifică violări
            violations = zone_monitor.check_violations(
                person_detections, 
                ppe_detections,
                current_time
            )
            
            # Desenează pe frame
            output_frame = frame.copy()
            
            # 1. Desenează zonele (dacă e activat)
            if show_zones:
                output_frame = zone_monitor.draw_zones(output_frame, alpha=0.2)
            
            # 2. Desenează detectările normale (fără violări)
            for det in person_detections + ppe_detections:
                x1, y1, x2, y2 = det.bbox
                label = f"{det.class_name} {det.confidence:.2f}"
                
                # Verde pentru detectări normale
                cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(output_frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # 3. Desenează violările (override peste detectările normale)
            if violations:
                output_frame = zone_monitor.draw_violations(output_frame, violations)
                
                # Afișează lista cu violări
                y_offset = 30
                for i, violation in enumerate(violations[:5]):  # Max 5
                    text = f"⚠ {violation.message}"
                    cv2.putText(output_frame, text, (10, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    y_offset += 30
            
            # Info în colțul din dreapta
            info_text = [
                f"Frame: {frame_count}",
                f"Persoane: {len(person_detections)}",
                f"Violari: {len(violations)}",
            ]
            
            y_pos = 30
            for text in info_text:
                (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                x_pos = output_frame.shape[1] - tw - 10
                cv2.putText(output_frame, text, (x_pos, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_pos += 30
            
            # Scrie frame-ul
            if writer:
                writer.write(output_frame)
            
            # Afișează
            cv2.imshow('YOLO + Zone Monitor', output_frame)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('z'):
                show_zones = not show_zones
                print(f"Zone afișare: {'ON' if show_zones else 'OFF'}")
            elif key == ord('s'):
                screenshot_path = f"screenshot_{frame_count}.jpg"
                cv2.imwrite(screenshot_path, output_frame)
                print(f"📸 Screenshot salvat: {screenshot_path}")
    
    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        
        # Cleanup
        zone_monitor.tracker.cleanup_old_entries()
        
        print(f"\n✓ Procesare completă. Total frame-uri: {frame_count}")


def main():
    """Entry point pentru scriptul de inference cu monitorizare zone.
    
    Parsează argumentele din linia de comandă și pornește procesarea video
    cu detecție YOLO și verificare reguli zone.
    """
    parser = argparse.ArgumentParser(
        description='Inference YOLO cu monitorizare zone'
    )
    parser.add_argument('--model', '-m', required=True, 
                       help='Calea către modelul YOLO (.pt)')
    parser.add_argument('--zones', '-z', required=True,
                       help='Calea către config JSON cu zone')
    parser.add_argument('--source', '-s', default='0',
                       help='Sursa video (0=webcam, path=video/imagine)')
    parser.add_argument('--output', '-o', default=None,
                       help='Salvează video output (optional)')
    parser.add_argument('--conf', '-c', type=float, default=0.5,
                       help='Confidence threshold (default: 0.5)')
    
    args = parser.parse_args()
    
    # Validări
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"❌ Modelul nu există: {model_path}")
        return
    
    zones_path = Path(args.zones)
    if not zones_path.exists():
        print(f"❌ Config zone nu există: {zones_path}")
        return
    
    run_inference_with_zones(
        model_path=str(model_path),
        zones_config=str(zones_path),
        source=args.source,
        output=args.output,
        conf_threshold=args.conf
    )


if __name__ == "__main__":
    main()
