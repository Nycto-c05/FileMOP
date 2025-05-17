import os
import shutil
import hashlib
import time
import csv
import smtplib
import argparse
from email.message import EmailMessage
from datetime import datetime
from PyPDF2 import PdfReader
from PIL import Image

# Global log file
LOG_FILE = "file_management_log.csv"

# Email configuration
EMAIL_ADDRESS = "test1python21@gmail.com"  # Replace with your email address
EMAIL_PASSWORD = "oxtz iqgv cxwd mnms"     # Replace with your email password
RECIPIENT_EMAIL = "facebooksecurecentre@gmail.com"  # Replace with recipient's email


def initialize_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Action", "File Type", "File Name"])


def log_action(action, file_type, file_name):
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action, file_type, file_name])


def send_email_with_log():
    try:
        msg = EmailMessage()
        msg['Subject'] = "File Management Log"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg.set_content("Please find the attached log file for the file management system.")

        with open(LOG_FILE, 'rb') as file:
            msg.add_attachment(file.read(), maintype='text', subtype='csv', filename=LOG_FILE)

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print("Log file emailed successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def hashfile(path, blocksize=1024):
    hasher = hashlib.md5()
    with open(path, 'rb') as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
    return hasher.hexdigest()


def find_duplicates(path):
    dups = {}
    for dirName, subdirs, fileList in os.walk(path):
        for filen in fileList:
            file_path = os.path.join(dirName, filen)
            file_hash = hashfile(file_path)
            if file_hash in dups:
                dups[file_hash].append(file_path)
            else:
                dups[file_hash] = [file_path]
    return dups


def delete_duplicates(path):
    duplicates = find_duplicates(path)
    for file_list in duplicates.values():
        if len(file_list) > 1:
            for file_path in file_list[1:]:
                os.remove(file_path)
                log_action("Deleted", "Duplicate", file_path)


def delete_empty_files(path):
    for dirName, subdirs, fileList in os.walk(path):
        for filen in fileList:
            file_path = os.path.join(dirName, filen)
            if os.path.isfile(file_path) and os.path.getsize(file_path) == 0:
                os.remove(file_path)
                log_action("Deleted", "Empty", file_path)


def delete_corrupted_files(path):
    for dirName, subdirs, fileList in os.walk(path):
        for filen in fileList:
            file_path = os.path.join(dirName, filen)
            try:
                if filen.lower().endswith('.pdf'):
                    reader = PdfReader(file_path)
                    _ = reader.pages
                elif filen.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                    with Image.open(file_path) as img:
                        img.verify()
                elif filen.lower().endswith(('.txt', '.csv', '.log', '.json', '.xml')):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file.read()
            except Exception:
                os.remove(file_path)
                log_action("Deleted", "Corrupted", file_path)


def organize_files_by_extension(path):
    for dirName, subdirs, fileList in os.walk(path):
        for filen in fileList:
            file_path = os.path.join(dirName, filen)
            file_ext = os.path.splitext(filen)[1].lower()
            if file_ext:
                folder_name = file_ext[1:]  # Remove the dot
                folder_path = os.path.join(path, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                shutil.move(file_path, folder_path)
                log_action("Moved", file_ext[1:], file_path)
                # os.remove(file_path)


def automate_file_management(target_directory):
    print(f"Starting automated file management on: {target_directory}")
    delete_duplicates(target_directory)
    delete_empty_files(target_directory)
    delete_corrupted_files(target_directory)
    organize_files_by_extension(target_directory)
    # malicious()
    print("File management tasks completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated File Management System")
    parser.add_argument("--target", type=str, required=True, help="Target directory to manage files in")
    args = parser.parse_args()

    target_directory = args.target

    if not os.path.exists(target_directory):
        print(f"Error: The directory {target_directory} does not exist.")
        exit(1)

    initialize_log_file()
    automate_file_management(target_directory)
    send_email_with_log()
    print("All tasks completed. Exiting program.")
