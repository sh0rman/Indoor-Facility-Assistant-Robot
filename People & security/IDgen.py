import sqlite3
from sqlite3 import Error
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
import os


def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connection is established: Database is created.")
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn


def create_table(conn):
    """Create a table if not exists."""
    sql_create_members_table = """
    CREATE TABLE IF NOT EXISTS members (
        id integer PRIMARY KEY,
        first_name text NOT NULL,
        last_name text NOT NULL,
        id_number text NOT NULL UNIQUE,
        photo_path text NOT NULL
    );"""
    try:
        cursor = conn.cursor()
        cursor.execute(sql_create_members_table)
    except Error as e:
        print(f"Error creating table: {e}")


def add_member(conn, member, department, major, logo_path, output_dir):
    """Add a new member to the members table and create an ID card for them."""
    sql = """ INSERT INTO members(first_name, last_name, id_number, photo_path)
              VALUES(?,?,?,?) """
    try:
        cur = conn.cursor()
        cur.execute(sql, member)
        conn.commit()
        print(f"New member added with id: {cur.lastrowid}")

        # Generate ID card
        first_name, last_name, id_number, photo_path = member
        name = f"{first_name} {last_name}"
        output_path = os.path.join(output_dir, f"{id_number}.png")
        generate_id_card(
            name, id_number, department, major, photo_path, logo_path, output_path
        )
    except Error as e:
        print(f"Error adding new member: {e}")


def get_member_by_id(conn, id_number):
    """Query member by ID number."""
    sql = "SELECT * FROM members WHERE id_number=?"
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_number,))
        member = cur.fetchone()
        return member
    except Error as e:
        print(f"Error querying member by ID: {e}")
        return None


def generate_id_card(
    name, id_number, department, major, photo_path, logo_path, output_path
):
    try:
        # Create a blank white image
        width, height = 800, 450
        card = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(card)

        # Define fonts
        font_path = "C:\\Windows\\Fonts\\times.ttf"  # Update path if necessary
        font_large = ImageFont.truetype(font_path, 36)
        font_medium = ImageFont.truetype(font_path, 28)
        font_small = ImageFont.truetype(font_path, 24)

        # Load and paste the new university logo with transparency handling
        if not os.path.exists(logo_path):
            raise FileNotFoundError(f"Logo file not found at {logo_path}")
        logo = (
            Image.open(logo_path).convert("RGBA").resize((300, 120), Image.LANCZOS)
        )  # Increased size
        logo_bg = Image.new("RGBA", logo.size, (255, 255, 255, 0))
        logo_combined = Image.alpha_composite(logo_bg, logo)
        card.paste(logo_combined, (30, 15), logo_combined)

        # Draw a thick line below the logo
        line_y = 135  # Y-coordinate for the line
        draw.rectangle([0, line_y, 800, line_y + 5], fill="black")

        # Load and paste the photo
        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"Photo file not found at {photo_path}")
        photo = Image.open(photo_path).resize(
            (150, 180), Image.LANCZOS
        )  # Increased size
        photo_position = (600, 30)
        card.paste(photo, photo_position)

        # Draw the border around the photo
        border_thickness = 5
        photo_border_position = [
            photo_position[0] - border_thickness,
            photo_position[1] - border_thickness,
            photo_position[0] + photo.size[0] + border_thickness,
            photo_position[1] + photo.size[1] + border_thickness,
        ]
        draw.rectangle(photo_border_position, outline="black", width=border_thickness)

        # Draw the details text
        draw.text((30, 180), f"Name: {name}", font=font_medium, fill="black")
        draw.text((30, 230), f"ID Num: {id_number}", font=font_medium, fill="black")
        draw.text(
            (30, 280), f"Department: {department}", font=font_medium, fill="black"
        )
        draw.text((30, 330), f"Major: {major}", font=font_medium, fill="black")

        # Generate and save the barcode using python-barcode
        EAN = barcode.get_barcode_class("code128")
        ean = EAN(id_number, writer=ImageWriter())
        barcode_path = os.path.join(os.path.dirname(output_path), "barcode")
        ean.save(barcode_path)
        barcode_path += ".png"
        print(f"Barcode saved at {barcode_path}")

        # Check if the barcode file was created successfully
        if not os.path.exists(barcode_path):
            raise FileNotFoundError(f"Barcode file not created at {barcode_path}")

        # Load and crop the barcode image to fit into a rectangle
        barcode_image = Image.open(barcode_path)
        barcode_width, barcode_height = barcode_image.size
        crop_height = int(barcode_height / 2)
        barcode_cropped = barcode_image.crop((0, 0, barcode_width, crop_height))

        # Resize the cropped barcode image to fit the desired dimensions
        desired_width, desired_height = 300, 120  # Adjust dimensions as needed
        barcode_resized = barcode_cropped.resize(
            (desired_width, desired_height), Image.LANCZOS
        )
        barcode_position = (470, 280)  # Adjust position as needed
        card.paste(barcode_resized, barcode_position)

        # Save the ID card
        card.save(output_path)
        print(f"ID card saved at {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Usage example
database = r"D:\Spring 2024\GP2\ReadyCodes\members.db"
conn = create_connection(database)
create_table(conn)
# The Hashemite University logo
logo_path = r"D:\Spring 2024\GP2\ID template\LOGO_FOOTER.png"
first_name = "Islam"
last_name = "Shorman"
id_number = "1935680"
photo_path = r"D:\Spring 2024\GP2\ID template\Islam.jpg"
department = "Engineering"
major = "Computer engineering"
output_dir = (
    r"D:\Spring 2024\GP2\ReadyCodes\IDs"  # Directory where ID cards will be saved
)

member = (first_name, last_name, id_number, photo_path)
add_member(conn, member, department, major, logo_path, output_dir)

if conn:
    conn.close()
