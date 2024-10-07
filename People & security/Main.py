import datetime
from PeopleRec import detect_people
from BarCode import detect_barcode
from IDgen import create_connection, get_member_by_id, create_table
from FaceRec import perform_face_recognition


def main():
    database_path = r"D:\Spring 2024\GP2\members.db"
    conn = create_connection(database_path)
    create_table(conn)

    current_time = datetime.datetime.now()
    print("Current time:", current_time.strftime("%H:%M:%S"))

    if current_time.hour < 16:
        print("Starting people detection...")
        detect_people()
    else:
        print("Starting ID detection...")
        barcode = detect_barcode()
        if barcode:
            print(f"" f"ID detected: {barcode}")
            member_info = get_member_by_id(conn, barcode)
            if member_info:
                photo_path = member_info[4]
                print(f"Photo path for member: {photo_path}")
                perform_face_recognition(photo_path)
            else:
                print("No member found for this ID")
        else:
            print("No ID detected.")

    if conn:
        conn.close()


if __name__ == "__main__":
    main()
