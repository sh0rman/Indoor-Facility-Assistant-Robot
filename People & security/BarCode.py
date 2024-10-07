import cv2
from pyzbar import pyzbar

def detect_barcode():
    video_capture = cv2.VideoCapture(0)
    barcode_data = None

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                continue

            # Displaying "Show your ID" text on the screen
            cv2.putText(frame, "Show your ID", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                barcode_data = barcode.data.decode("utf-8")
                barcode_type = barcode.type
                text = f"{barcode_data} ({barcode_type})"
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                print(f"ID detected: {barcode_data} [{barcode_type}]")

                # Return the detected barcode data to the main script
                return barcode_data

            cv2.imshow('Barcode Scanner', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    barcode = detect_barcode()
    if barcode:
        print(f"ID detected: {barcode}")
    else:
        print("No ID detected.")
