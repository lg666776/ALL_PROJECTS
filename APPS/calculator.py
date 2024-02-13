import tkinter as tk


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("400x500")  # Set window size

        self.entry = tk.Entry(root, width=20, font=("Helvetica", 20))
        self.entry.grid(row=0, column=0, columnspan=4, padx=20, pady=20)
        self.entry.bind("<Return>", self.on_enter_key)  # Bind Enter key

        self.create_buttons()

    def create_buttons(self):
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
            ('<-', 5, 0)  # Backspace button
        ]

        for (text, row, col) in buttons:
            button = tk.Button(self.root, text=text, command=lambda t=text: self.on_button_click(t), width=5, height=2,
                               bg="red", fg="white", font=("Helvetica", 12))
            button.grid(row=row, column=col, padx=3, pady=3)
            if text.isdigit():
                button.bind("<KP_" + text + ">", lambda event, t=text: self.on_button_click(t))  # Bind numeric keypad

    def on_button_click(self, value):
        if value == '=':
            try:
                result = eval(self.entry.get())
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, str(result))
            except Exception as e:
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, "Error")
        elif value == '<-':
            current_text = self.entry.get()
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, current_text[:-1])  # Remove the last character
        else:
            current_text = self.entry.get()
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, current_text + value)

    def on_enter_key(self, event):
        self.on_button_click('=')  # Trigger calculation when Enter key is pressed


if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
100
