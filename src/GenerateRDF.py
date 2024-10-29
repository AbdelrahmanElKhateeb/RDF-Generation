import os
import time
from watchdog.events import FileSystemEventHandler
import re

import tkinter as tk
from tkinter import filedialog



"""Path used to select the directory for all the files to generate the RDF for
If you want to use it, Comment the File Selector Block in the main method""" 
#op_folder = "C:\\...\\...\\...\\..."  

Output_name = "New_Collection.rdf" # Change this name to whatever you want

class NewFileHandler(FileSystemEventHandler):



    def __init__(self):
        self.counter = 0  # Initialize the counter
        self.string_added = False # Initialize the flag for RDF opening strings/tags 






    def on_created(self, event):
        if not event.is_directory:
            time.sleep(3)  # Wait a moment for the file to be fully created
            self.counter += 2  # Increment the counter for each new file
            self.write_RDFString(event.src_path, self.counter)







    def write_RDFString(self, file_path, counter):
        if not (os.path.basename(file_path)).startswith("~$"):
            time.sleep(3)
            rdf_string = self.createEntry(file_path, counter)  # Use counter for unique ID
            with open(Output_name, "a") as f: #Change the name of the file
                f.write(rdf_string + "\n")  # Write the RDF string followed by a newline
            print(f'Generating {file_path} rdf entry with counter {counter}.')







    def createEntry(self, file_path, counter):

        # Gets file path and divides it
        path_name = os.path.splitext(file_path)[0]
        file_name = os.path.basename(file_path)
        file_noExtension = os.path.splitext(file_name)[0]
        file_extension = os.path.splitext(file_name)[1]




        """Splits the file path into tags to be added, Change this part to your criteria for tagging
        This will also keep the word before splitting i.e.(Hello World) => (Hello),(World),(Hello World)"""
        tags_list = remove_basename(file_path).split(os.sep)
        tags_list = split_and_add(tags_list)



        tempcounter = counter  # Use tempcounter based on the current counter value




        # Prepare the RDF components using tempcounter
        resources = """\t\t<link:link rdf:resource="#item_""" + str(tempcounter + 1) + """\"/>\n"""
        tag_subjects = "\n".join(f"\t\t<dc:subject>{tag}</dc:subject>" for tag in tags_list) + "\n"




        desc_head = """\t<rdf:Description rdf:about="#item_""" + str(tempcounter) + """">\n"""
        desc_tail = """\t</rdf:Description>\n"""




        attachment = """\t<z:Attachment rdf:about="#item_""" + str(tempcounter + 1) + """">\n"""
        attachment_file_path = """\t\t<rdf:resource rdf:resource=\"""" + file_path + """\"/>\n"""
        attachment_title = """\t\t<dc:title>""" + file_noExtension + """</dc:title>\n"""
        #Modify the linkMode number for the type of attachment [1 for attaching the file into Zotero storage, and 2 for linking only the path]
        attachment_linktype = """\t\t<z:linkMode>2</z:linkMode>\n""" 
        item_type = """\t\t<z:itemType>document</z:itemType>\n"""
        attachment_close = """\t</z:Attachment>"""

        """ Add any string of the correct zotero rdf format and indentation here then
         add it to the string named combined at the appropriate place"""






        # Determine attachment type based on file extension
        if file_extension == ".xlsx":
            attachment_type = """\t\t<link:type>application/vnd.openxmlformats-officedocument.spreadsheetml.sheet</link:type>\n"""
        elif file_extension == ".pdf":
            attachment_type = """\t\t<link:type>application/pdf</link:type>\n"""
        elif file_extension == ".docx":
            attachment_type = """\t\t<link:type>application/vnd.openxmlformats-officedocument.wordprocessingml.document</link:type>\n"""
        elif file_extension in [".png", ".jpeg", ".jpg"]:
            attachment_type = """\t\t<link:type>image/""" + file_extension.lstrip(".") + """</link:type>\n"""
        else:
            attachment_type = """\t\t<link:type>text/plain</link:type>\n"""

        combined = (
            desc_head + item_type + resources + tag_subjects + attachment_title + desc_tail +
            attachment + item_type + attachment_file_path +
            attachment_title + attachment_linktype + attachment_type + attachment_close
        )

        # Add the initial RDF string block of strings/tags only once
        if not self.string_added:
            string1 = """<rdf:RDF\n"""
            string2 = """ xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n"""
            string3 = """ xmlns:z="http://www.zotero.org/namespaces/export#"\n"""
            string4 = """ xmlns:link="http://purl.org/rss/1.0/modules/link/"\n"""
            string5 = """ xmlns:dc="http://purl.org/dc/elements/1.1/">\n"""
            combined = string1 + string2 + string3 + string4 + string5 + combined
            
            self.string_added = True

        return combined





# Opens a window so user can select a folder
def select_folder():
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open the file explorer dialog to select a folder
    folder_selected = filedialog.askdirectory()
    folder_selected = re.sub(r'/', r'\\', folder_selected)

    # Return the selected folder path
    return folder_selected





# Goes through all files (including all subfolders inside) in the directory
def process_existing_files(folder_path, handler):
    """ Traverse all files in the directory and subdirectories and apply processing """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"Processing existing file: {file_path}")
            handler.counter += 2
            handler.write_RDFString(file_path, handler.counter)





# The Path without the file basename
def remove_basename(file_path):
    return os.path.dirname(file_path)






# Split any item in the list that is composed of two or more words seperated by space without removing it
# i.e. "Hello World" => "Hello" , "World"
def split_and_add(lst):
    # Create a new list to store the results
    result = []

    for item in lst:
        # Add the original string to the result list
        result.append(item)

        # If the string contains space, split it and extend the result
        if ' ' in item:
            result.extend(item.split())  # Split and add the parts to the result list

    return result




# Main
if __name__ == "__main__":

    # File Selector Block : Comment this If you want to use the op_folder variable to enter path instead
    op_folder = select_folder()
    if op_folder:
        print(f"Selected folder: {op_folder}")
    else:
        print("No folder was selected.")
    # End of File Selector Block

    event_handler = NewFileHandler() #creates event handler instance
    process_existing_files(op_folder, event_handler) # First, process all existing files in the folder and subfolders

    with open(Output_name, "a") as f:
        f.write("</rdf:RDF>")  # Writes the closing tag for RDF

    print("done")
