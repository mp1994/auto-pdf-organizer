from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pdfrw import PdfReader

import os
import time
import json

# TEST
#folder_to_track = "/Users/mattia/Desktop/foo"
#folder_destination = "/Users/mattia/Desktop/bar"

folder_to_track = "/Users/mattia/Downloads"
folder_destination = "/Users/mattia/OneDrive - Politecnico di Milano/PhD/PAPERS"

# Echo
print(">> RUNNING")
print("   Source folder:      ", folder_to_track)
print("   Destination folder: ", folder_destination)

class MyHandler(FileSystemEventHandler):
    # Detected changes to a folder
    def on_modified(self, event):
        for filename in os.listdir(folder_to_track):
            # Include PDF files only
            if filename.endswith(".pdf"):
                # Get full path
                src = folder_to_track + "/" + filename
                # Parse PDF metadata
                pdf_temp = PdfReader(src).Info;
                # Try to isolate papers: check Subject, Author and Keywords fields in the metadata
                if not pdf_temp.Subject is None or not pdf_temp.Author is None or not pdf_temp.Keywords is None:
                    # If there is a Title field, rename the PDF file
                    if not pdf_temp.Title is None and pdf_temp.Title != '()':
                        new_filename = pdf_temp.Title[1:len(pdf_temp.Title)-1]
                        # Check for forbidden character '-' (OneDrive issue)
                        while new_filename.find('-') > -1:
                            tmp = new_filename.find('-')
                            new_filename = new_filename[0:tmp] + new_filename[tmp+1:len(new_filename)]
                        # Check for forbidden character ':' (OneDrive issue)
                        while new_filename.find(':') > -1:
                            tmp = new_filename.find(':')
                            new_filename = new_filename[0:tmp] + new_filename[tmp+1:len(new_filename)]
                        new_filename = new_filename + ".pdf"
                        new_destination = folder_destination + "/" + new_filename + ".pdf"
                        # Echo message (renamed file)
                        print(">> Paper recognized: ", pdf_temp.Title[1:len(pdf_temp.Title)-1] + ".pdf")
                    else:
                        new_destination = folder_destination + "/" + filename
                        # Echo message
                        print(">> Paper recognized: ", filename)
                    os.rename(src, new_destination)

event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, folder_to_track, recursive=True)
observer.start()

try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    observer.stop()
observer.join()
