import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox

print("Vysual Python IDE v1\n\nKarac Von Thweatt\n======================\n\n")

class PythonIDE:
    def __init__(self, master):
        print("[Main Window] Initializing ...\n")
        self.master = master
        master.title("Vysual Python v1")

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.bind('<<Modified>>', self.on_modified)

        self.menu = tk.Menu(master)
        master.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_program)

        self.view_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Graph", command=self.show_graph)

        self.run_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Run", menu=self.run_menu)
        self.run_menu.add_command(label="Run", command=self.run_code)

        self.file_path = None
        self.text_modified = False
        print("[Main Window] Done.\n")

    def on_modified(self, event=None):
        self.text_modified = True
        self.text_area.edit_modified(False)

    def new_file(self):
        if self.confirm_save():
            self.text_area.delete(1.0, tk.END)
            self.file_path = None
            self.text_modified = False

    def open_file(self):
        if self.confirm_save():
            file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
            if file_path:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, content)
                self.file_path = file_path
                self.text_modified = False

    def save_file(self):
        if self.file_path:
            # Will update to support other languages in future
            if self.file_path.endswith(".py") == False:
                self.file_path += ".py"
            with open(self.file_path, 'w') as file:
                content = self.text_area.get(1.0, tk.END)
                file.write(content)
                print(f"[Main Window] Saved file to {file_path}")
            self.text_modified = False
            self.master.title(f"Vysual Python v1 - {self.file_path}")
        else:
            self.save_as_file()

    def save_as_file(self):
        print("[Main Window] Saving file ...")
        file_path = filedialog.asksaveasfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            if file_path.endswith(".py") == False:
                file_path += ".py"
            with open(file_path, 'w') as file:
                content = self.text_area.get(1.0, tk.END)
                file.write(content)
                print(f"[Main Window] Saved file to {file_path}")
            self.file_path = file_path
            self.text_modified = False
            self.master.title(f"Vysual Python v1 - {self.file_path}")

    def exit_program(self):
        if self.confirm_save():
            self.master.destroy()

    def confirm_save(self):
        print("[Main Window] Confirming save ...")
        if self.text_modified:
            response = messagebox.askyesnocancel("Save Changes", "You have unsaved changes. Do you want to save before exiting?")
            if response:
                print("[Main Window] Yes selected, saving ...")
                self.save_file()
                return True
            elif response is False: 
                print("[Main Window] No selected.")
                return True
            else:  # Cancel
                print("[Main Window] Cancel selected.")
                return False
        print("[Main Window] Yes selected.")
        return True

    def run_code(self):
        code = self.text_area.get(1.0, tk.END)
        print("[Main Window] Running file ...")
        try:
            exec(code)
        except Exception as e:
            print("[Main Window] Failed.")
            error_msg = f"An error occurred: {e}"
            self.text_area.insert(tk.END, error_msg)

    def show_graph(self):
        print("[Graph Window] Creating window ...")
        graph_window = tk.Toplevel(self.master)
        graph_window.title("Vysual Python Blueprint Node Graph")
        graph_window.geometry("800x600")
        graph_label = tk.Label(graph_window, text="Live code blueprint node graph will be displayed here.")
        graph_label.pack()
        print("[Graph Window] Created blueprint node graph window.")

if __name__ == "__main__":
    root = tk.Tk()
    print("[Info] Successfully declared tkinter window.\n")
    ide = PythonIDE(root)
    print("[Info] Successfully declared window main loop.\n")
    root.mainloop()
