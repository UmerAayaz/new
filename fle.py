import tkinter as tk
from PIL import ImageTk, Image
import mouse  # Assuming mouse.py contains the GestureController class and runvirtualmouse function

def runvirtualmouse():
    global gc1
    gc1 = mouse.GestureController()
    gc1.start()

def close_program():
    if 'gc1' in globals():
        gc1.gc_mode = 0  # Stop gesture recognition
    root.destroy()

root = tk.Tk()
root.geometry("1600x900")
root.title("Gesture Recognition System")

# Load and set the icon image
icon_image = tk.PhotoImage(file="LOGONEW.png")  # Update the path to your icon image
root.iconphoto(True, icon_image)

# Load the background image
bg_image = Image.open("aaaa (5).png")  # Replace "background_image.jpg" with the path to your image

# Calculate the aspect ratio of the image
aspect_ratio = bg_image.width / bg_image.height

# Determine the maximum width and height for the image based on the window size
max_width = root.winfo_width()
max_height = root.winfo_height()

# Calculate the new dimensions for the image while maintaining the aspect ratio
if aspect_ratio > max_width / max_height:
    new_width = max_width
    new_height = int(new_width / aspect_ratio)
else:
    new_height = max_height
    new_width = int(new_height * aspect_ratio)

# Ensure that the new dimensions are positive
if new_width <= 0 or new_height <= 0:
    print("Error: The new dimensions are zero or negative.")
    new_width = bg_image.width
    new_height = bg_image.height

# Resize the image
bg_image = bg_image.resize((new_width, new_height))

# Convert the resized image to a PhotoImage object
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a label to hold the background image
bg_label = tk.Label(root, image=bg_photo)

# Position the label to fill the entire window
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Create other widgets
start_button = tk.Button(root, text="START", fg="blue", bg='light blue',
                         font='Times 20 bold', command=runvirtualmouse,
                         height=4, width=16, activebackground='light pink')
# Position the start button at the bottom center of the window
start_button.place(relx=0.4, rely=0.8, anchor='center')

# Create a button to close the program
close_button = tk.Button(root, text="CLOSE", fg="red", bg='light pink',
                         font='Times 20 bold', command=close_program,
                         height=4, width=16, activebackground='lightblue')
# Position the close button above the start button
close_button.place(relx=0.6, rely=0.8, anchor='center')

root.mainloop()
