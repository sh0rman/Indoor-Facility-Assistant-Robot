import face_recognition
import cv2
import time
import os

def perform_face_recognition(photo_path):
    # Load the known image and encode it
    known_image = face_recognition.load_image_file(photo_path)
    known_encodings = face_recognition.face_encodings(known_image)

    if not known_encodings:
        print(f"Error: No faces found in the image {photo_path}")
        return None, None

    known_encoding = known_encodings[0]

    # Capture a video frame
    video_capture = cv2.VideoCapture(0)
    match_start_time = None
    no_match_start_time = None
    match_duration = 3  # Match duration in seconds
    no_match_duration = 3  # No match duration in seconds

    while True:
        ret, frame = video_capture.read()
        if not ret:
            continue

        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find all faces and face encodings in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        match_found = False

        # Check each face in the frame
        for face_encoding, face_location in zip(face_encodings, face_locations):
            match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.6)
            distance = face_recognition.face_distance([known_encoding], face_encoding)

            top, right, bottom, left = face_location
            match_percentage = (1 - distance[0]) * 100

            if match[0]:
                if match_start_time is None:
                    match_start_time = time.time()
                elapsed_time = time.time() - match_start_time
                if elapsed_time >= match_duration:  # Match found for at least match_duration seconds
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, f'Match - {match_percentage:.2f}%', (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 0), 2)
                    print("Match found, stopping recognition.")
                    video_capture.release()
                    cv2.destroyAllWindows()
                    return
                match_found = True
                no_match_start_time = None  # Reset no match timer
            else:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, f'No Match - {match_percentage:.2f}%', (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 0, 255), 2)
                match_start_time = None  # Reset match timer

        if match_found:
            no_match_start_time = None
        else:
            if no_match_start_time is None:
                no_match_start_time = time.time()
            elapsed_time = time.time() - no_match_start_time
            if elapsed_time >= no_match_duration:
                # Save the frame as no match found for the specified duration
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                output_path = os.path.join(r"D:\Spring 2024\GP2\ID template", f"NoMatch_{timestamp}.jpg")
                cv2.imwrite(output_path, frame)
                print(f"No match found, image saved to {output_path}")
                no_match_start_time = None  # Reset timer after saving
                # Optionally break the loop after saving the image
                video_capture.release()
                cv2.destroyAllWindows()
                return

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()


