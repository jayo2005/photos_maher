import customtkinter as ctk
ctk.set_default_color_theme("dark-blue")
import os
import glob
import datetime
from PIL import Image
from customtkinter import CTkImage
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

class CustomPopup(ctk.CTkToplevel):
    def __init__(self, master, message, title, callback):
        super().__init__(master)
        self.callback = callback
        self.title(title)

        custom_font = ctk.CTkFont(family="Arial", size=12, weight='normal')

        ctk.CTkLabel(self, text=message, font=custom_font).pack(padx=20, pady=20)

        self.yes_button = ctk.CTkButton(self, text="Yes", font=custom_font, command=lambda: self.close(True))
        self.yes_button.pack(side="left", padx=20, pady=20)

        self.no_button = ctk.CTkButton(self, text="No", font=custom_font, command=lambda: self.close(False))
        self.no_button.pack(side="left", padx=20, pady=20)

        self.geometry("+%d+%d" % (master.winfo_rootx() + 50, master.winfo_rooty() + 50))
        
        # Ensure the popup stays in front of the master window
        self.transient(master)
        self.grab_set()

    def close(self, value):
        self.callback(value)
        self.destroy()

folder_path = None

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        global folder_path

        self.title("Maher Property Image Processor")
        self.geometry("1200x400")
        self.update_idletasks()
        self.center_window()

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.property_name_label = ctk.CTkLabel(self, text="Property Name:")
        self.property_name_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.property_name_entry = ctk.CTkEntry(self, width=450)
        self.property_name_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")
        self.browse_button = ctk.CTkButton(self, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=0, column=2, padx=20, pady=10, sticky="ew")

        self.create_folder_button = ctk.CTkButton(self, text="Create Folder", command=self.create_folder, state="normal")
        self.create_folder_button.grid(row=0, column=3, padx=20, pady=10, sticky="ew")
        self.delete_sd_files_button = ctk.CTkButton(self, text="Delete SD Files", command=self.delete_sd_files, state="normal")
        self.delete_sd_files_button.grid(row=0, column=4, padx=20, pady=10, sticky="ew")

        self.process_images_button = ctk.CTkButton(self, text="Process Images", command=self.process_images)
        self.process_images_button.grid(row=1, column=0, columnspan=4, padx=20, pady=10, sticky="ew")

        self.progressbar = ctk.CTkProgressBar(self, orientation="horizontal", width=200, height=20)
        self.progressbar.grid(row=2, column=0, columnspan=4, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.grid(row=3, column=0, columnspan=4, padx=20, pady=10, sticky="ew")

        from PIL import Image
        from customtkinter import CTkImage
        img = Image.open("maher.png")
        img = img.resize((400, 200))  # Resize the image to 800x400 pixels for better quality on HighDPI displays
        self.logo_image = CTkImage(light_image=img, dark_image=img, size=(400, 200))
        self.logo_label = ctk.CTkLabel(self, image=self.logo_image)
        self.logo_label.grid(row=4, column=0, columnspan=4, padx=20, pady=10)

    def center_window(self):
        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Calculate position to center window
        x = (screen_width / 2) - (1000 / 2)
        y = (screen_height / 2) - (250 / 2)
        self.geometry(f"+{int(x)}+{int(y)}")

    def browse_folder(self):
        global base_folder_path
        base_folder_path = filedialog.askdirectory(initialdir="Z:\\")
        self.property_name_entry.delete(0, tk.END)
        self.property_name_entry.insert(0, base_folder_path)
        self.create_folder()

    def create_folder(self):
        global base_folder_path, folder_path
        if base_folder_path is None:
            messagebox.showerror("Error", "Please browse for a base folder first.")
        else:
            property_name = self.property_name_entry.get()
            if not property_name:
                messagebox.showerror("Error", "Please enter a property name.")
            else:
                folder_path = os.path.join(base_folder_path, property_name)
                os.makedirs(folder_path, exist_ok=True)
                response = messagebox.askyesno("Folder created", "Folder created. Do you want to process images?")
                self.create_folder_callback(response)

    def create_folder_callback(self, response):
        if response:
            self.process_images()

    def process_images(self):
        global folder_path
        if folder_path is None:
            messagebox.showerror("Error", "Please select a folder first.")
        else:
            threading.Thread(target=self._process_images_thread, daemon=True).start()

    def _process_images_thread(self):
        self.progressbar.set(0)
        camera_path = "C:\\Property_Images"
        image_files = glob.glob(camera_path + "**/*.jpg", recursive=True)

        for counter, image_file in enumerate(image_files, 1):
            try:
                # Open the image file
                with Image.open(image_file) as img:
                    # Process the image (this is a placeholder, replace with your image processing code)
                    processed_img = img  # Replace this line with your image processing code

                    # Save the processed image to the Z:\\ drive
                    new_file_name = os.path.join(folder_path, f"{os.path.basename(folder_path)}_{datetime.date.today().strftime('%d-%m-%Y')}_{counter}.jpg")
                    processed_img.save(new_file_name)

                # Update the progress bar and status label
                self.progressbar.set(counter / len(image_files))
                self.status_label.configure(text=f"Processing {counter}/{len(image_files)}: {new_file_name}")
            except Exception as e:
                print(f"Error processing image {image_file}: {e}")
                self.status_label.configure(text=f"Error processing image {image_file}: {e}")

        print("All images processed.")
        self.status_label.configure(text="All images processed.")
        response = messagebox.askyesno("Images copied", "Images copied. Do you want to open the location?")
        if response:
            self.open_location_callback(True)  # Open the location

    def open_location_callback(self, response):
        global folder_path
        if response:
            if 'folder_path' in globals():
                os.startfile(folder_path)
            else:
                messagebox.showerror("Error", "No folder has been created yet.")

    def delete_sd_files(self):
        sd_card_path = "C:\\Property_Images"
        response = messagebox.askyesno("Delete SD Files", f"Are you sure you want to delete all files from the folder at {sd_card_path}?")
        if response:
            response = messagebox.askyesno("Last Chance", "Last chance! Are you absolutely sure you want to delete all files from the folder?")
            if response:
                threading.Thread(target=self._delete_sd_files_thread, args=(sd_card_path,), daemon=True).start()

    def _delete_sd_files_thread(self, sd_card_path):
        for root, dirs, files in os.walk(sd_card_path, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except Exception as e:
                    print(f"Error deleting file {os.path.join(root, name)}: {e}")
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except Exception as e:
                    print(f"Error deleting directory {os.path.join(root, name)}: {e}")
        messagebox.showinfo("Files Deleted", "All files and folders have been deleted from the folder.")

app = App()
app.mainloop()
