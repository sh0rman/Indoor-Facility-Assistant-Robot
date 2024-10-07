import cv2
import numpy as np

def detect_people(display=True):
    # Loading YOLO Model
    net = cv2.dnn.readNet(r'D:\Spring 2024\GP2\yolo-cfg\weights.weights', r'D:\Spring 2024\GP2\yolo-cfg\config.cfg')
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

    # Load classes
    classes = []
    with open(r'D:\Spring 2024\GP2\yolo-cfg\names.names', 'r') as f:
        classes = [line.strip() for line in f.readlines()]

    # Video capture
    cap = cv2.VideoCapture(r"D:\Spring 2024\GP2\Samples\Park-Mid.mp4")
    font = cv2.FONT_HERSHEY_COMPLEX
    new_width, new_height = 1280, 720

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the frame for processing
        frame = cv2.resize(frame, (new_width, new_height))
        height, width, _ = frame.shape

        # Prepare the frame for YOLO detection
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        class_ids, confidences, boxes = [], [], []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x, center_y = int(detection[0] * width), int(detection[1] * height)
                    w, h = int(detection[2] * width), int(detection[3] * height)
                    x, y = int(center_x - w / 2), int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        people_count = 0

        for i in range(len(boxes)):
            if i in indexes and class_ids[i] == 0:  # Class ID 0 is a person
                x, y, w, h = boxes[i]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                people_count += 1

        if display:
            cv2.putText(frame, f'People detected: {people_count}', (20, 50), font, 1, (255, 255, 255), 2)
            cv2.imshow("People Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_people()
