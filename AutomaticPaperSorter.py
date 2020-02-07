#!/usr/local/bin/python3

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pdfrw import PdfReader

import os, sys, select
import time
import signal
import json

folder_to_track    = "/Users/mattia/Downloads"
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
                
                # Try to isolate papers: check Subject, Author, Keywords and WPS-ARTICLEDOI fields in the metadata
                if not pdf_temp.Subject is None or not pdf_temp.Author is None or not pdf_temp.Keywords is None or not getattr(pdf_temp, "WPS-ARTICLEDOI") is None:
                    
                    # If there is a Title field, rename the PDF file
                    if not pdf_temp.Title is None and pdf_temp.Title != '()':
                        new_filename = pdf_temp.Title[1:len(pdf_temp.Title)-1]
                        new_destination = folder_destination + "/" + new_filename + ".pdf"
                        # Echo message (renamed file)
                        print(">> Paper recognized: ", pdf_temp.Title[1:len(pdf_temp.Title)-1] + ".pdf")
                    else:
                        new_destination = folder_destination + "/" + filename
                        # Echo message
                        print(">> Paper recognized: ", filename)
                        new_filename = filename
                    
                    # Check for forbidden character '-' (OneDrive issue)
                    while new_filename.find('-') > 0:
                        tmp = new_filename.find('-')
                        new_filename = new_filename[0:tmp] + new_filename[tmp+1:len(new_filename)]
                        new_destination = folder_destination + "/" + new_filename
                    # Check for forbidden character ':' (OneDrive issue)
                    while new_filename.find(':') > 0:
                        tmp = new_filename.find(':')
                        new_filename = new_filename[0:tmp] + new_filename[tmp+1:len(new_filename)]
                        new_destination = folder_destination + "/" + new_filename
                        
                    if not new_destination.endswith(".pdf"):
                        new_destination = new_destination + ".pdf"
                    
                    # Move the file
                    os.rename(src, new_destination)
                    
                    # Open File?
                    print("Do you want to open the file? [Y/N]")
                    i, o, e = select.select( [sys.stdin], [], [], 10 ) # Times out in 10 seconds
                    if i:
                        user_input = str(sys.stdin.readline().strip()).lower() 
                        if user_input == 'y' or user_input == 'yes':
                            os.system('open ' + new_destination)
                    
                else: # If it is not an article, break
                    pass;

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
