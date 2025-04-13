import tkinter as tk

def on_click():
    label.config(text="Hello from Docker!")

root = tk.Tk()
root.title("Docker GUI Demo")
root.geometry("300x150")

label = tk.Label(root, text="Press the button", font=("Arial", 14))
label.pack(pady=20)

button = tk.Button(root, text="Click me", command=on_click)
button.pack()

root.mainloop()
