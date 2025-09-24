import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
import re

class EngineeringCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Инженерный калькулятор")
        self.root.geometry("500x700")
        self.root.resizable(True, True)
        
        # Настраиваем стиль для кнопок
        self.setup_styles()
        
        # Переменные
        self.display_var = tk.StringVar()
        self.angle_mode = tk.StringVar(value="rad")
        self.memory = 0
        self.last_result = 0
        self.history = []
        self.auto_bracket = True  # Автоматическое добавление скобок
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Бинд на полноэкранный режим
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)
        self.root.bind('<Return>', lambda e: self.calculate())
        self.root.bind('<BackSpace>', lambda e: self.clear_entry())
        
    def setup_styles(self):
        # Создаем стиль для кнопок в стандартных цветах ОС
        style = ttk.Style()
        
        # Стиль для обычных кнопок
        style.configure("TButton", 
                       font=("Arial", 14),
                       padding=(10, 8))
        
        # Стиль для кнопки равно (акцентная) - исправляем цвета
        style.configure("Accent.TButton", 
                       font=("Arial", 14, "bold"),
                       background="#0078d4", 
                       foreground="white")
        
        # Стиль для цифровых кнопок
        style.configure("Number.TButton",
                       font=("Arial", 14, "bold"))
        
        # Стиль для функциональных кнопок
        style.configure("Function.TButton",
                       font=("Arial", 12))
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Display
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(fill=tk.X, pady=5)
        
        self.display = tk.Entry(display_frame, textvariable=self.display_var, 
                               font=("Arial", 20, "bold"), justify="right",
                               bd=2, relief="sunken", bg="#f8f8f8")
        self.display.pack(fill=tk.X, ipady=12)
        self.display_var.set("0")
        
        # Mode indicator
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(mode_frame, text="Режим углов:", font=("Arial", 10)).pack(side=tk.LEFT)
        mode_label = ttk.Label(mode_frame, textvariable=self.angle_mode, 
                              font=("Arial", 10, "bold"), foreground="blue")
        mode_label.pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        for i in range(7):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(6):
            buttons_frame.grid_columnconfigure(i, weight=1)
        
        # Button definitions with styles
        buttons = [
            # Row 0: Memory and Clear
            [("MC", self.memory_clear, "Function.TButton"), 
             ("MR", self.memory_recall, "Function.TButton"), 
             ("M+", self.memory_add, "Function.TButton"), 
             ("MS", self.memory_store, "Function.TButton"),
             ("CE", self.clear_entry, "Function.TButton"), 
             ("C", self.clear, "Function.TButton")],
            
            # Row 1: Numbers and basic operations
            [("7", lambda: self.button_click("7"), "Number.TButton"), 
             ("8", lambda: self.button_click("8"), "Number.TButton"),
             ("9", lambda: self.button_click("9"), "Number.TButton"), 
             ("÷", lambda: self.button_click("/"), "TButton"),
             ("sin", lambda: self.add_function("sin"), "Function.TButton"), 
             ("cos", lambda: self.add_function("cos"), "Function.TButton")],
            
            # Row 2: Numbers and operations
            [("4", lambda: self.button_click("4"), "Number.TButton"), 
             ("5", lambda: self.button_click("5"), "Number.TButton"),
             ("6", lambda: self.button_click("6"), "Number.TButton"), 
             ("×", lambda: self.button_click("*"), "TButton"),
             ("tan", lambda: self.add_function("tan"), "Function.TButton"), 
             ("cot", lambda: self.add_function("cot"), "Function.TButton")],
            
            # Row 3: Numbers and operations
            [("1", lambda: self.button_click("1"), "Number.TButton"), 
             ("2", lambda: self.button_click("2"), "Number.TButton"),
             ("3", lambda: self.button_click("3"), "Number.TButton"), 
             ("-", lambda: self.button_click("-"), "TButton"),
             ("asin", lambda: self.add_function("asin"), "Function.TButton"), 
             ("acos", lambda: self.add_function("acos"), "Function.TButton")],
            
            # Row 4: Numbers and operations
            [("0", lambda: self.button_click("0"), "Number.TButton"), 
             (".", lambda: self.button_click("."), "Number.TButton"),
             ("π", lambda: self.button_click("π"), "Function.TButton"), 
             ("+", lambda: self.button_click("+"), "TButton"),
             ("atan", lambda: self.add_function("atan"), "Function.TButton"), 
             ("acot", lambda: self.add_function("acot"), "Function.TButton")],
            
            # Row 5: Advanced functions
            [("(", lambda: self.button_click("("), "Function.TButton"), 
             (")", lambda: self.button_click(")"), "Function.TButton"),
             ("^", lambda: self.button_click("^"), "Function.TButton"), 
             ("√", lambda: self.add_function("sqrt"), "Function.TButton"),
             ("ln", lambda: self.add_function("ln"), "Function.TButton"), 
             ("log", lambda: self.add_function("log"), "Function.TButton")],
            
            # Row 6: Equal and special functions
            [("Deg/Rad", self.toggle_angle_mode, "Function.TButton"), 
             ("e", lambda: self.button_click("e"), "Function.TButton"),
             ("±", self.negate, "Function.TButton"), 
             ("1/x", self.reciprocal, "Function.TButton"),
             ("x²", self.square, "Function.TButton"), 
             ("=", self.calculate, "Accent.TButton")]
        ]
        
        # Create buttons
        for i, row in enumerate(buttons):
            for j, (text, command, style_name) in enumerate(row):
                if text == "=":
                    btn = ttk.Button(buttons_frame, text=text, command=command,
                                   style=style_name)
                    btn.grid(row=i, column=j, columnspan=2, sticky="nsew", padx=2, pady=2)
                else:
                    btn = ttk.Button(buttons_frame, text=text, command=command,
                                   style=style_name)
                    btn.grid(row=i, column=j, sticky="nsew", padx=2, pady=2)
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Полный экран (F11)", 
                  command=self.toggle_fullscreen, style="Function.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="История", 
                  command=self.show_history, style="Function.TButton").pack(side=tk.LEFT, padx=5)
        
        # Checkbutton for auto bracket
        self.auto_bracket_var = tk.BooleanVar(value=True)
        auto_bracket_cb = ttk.Checkbutton(control_frame, text="Авто скобки", 
                                         variable=self.auto_bracket_var,
                                         command=self.toggle_auto_bracket)
        auto_bracket_cb.pack(side=tk.LEFT, padx=5)
    
    def toggle_auto_bracket(self):
        self.auto_bracket = self.auto_bracket_var.get()
    
    def button_click(self, char):
        current = self.display_var.get()
        if current == "0" or current == "Error":
            self.display_var.set(char)
        else:
            self.display_var.set(current + char)
    
    def clear(self):
        self.display_var.set("0")
    
    def clear_entry(self):
        current = self.display_var.get()
        if len(current) > 1:
            self.display_var.set(current[:-1])
        else:
            self.display_var.set("0")
    
    def add_function(self, func):
        current = self.display_var.get()
        if current == "0" or current == "Error":
            if self.auto_bracket:
                new_text = f"{func}()"
                self.display_var.set(new_text)
                # Устанавливаем курсор между скобками
                self.display.focus_set()
                self.display.icursor(len(func) + 1)
            else:
                self.display_var.set(f"{func}(")
        else:
            if self.auto_bracket:
                new_text = current + f"{func}()"
                self.display_var.set(new_text)
                # Устанавливаем курсор между скобками
                self.display.focus_set()
                self.display.icursor(len(current) + len(func) + 1)
            else:
                self.display_var.set(current + f"{func}(")
    
    def toggle_angle_mode(self):
        if self.angle_mode.get() == "rad":
            self.angle_mode.set("deg")
        else:
            self.angle_mode.set("rad")
    
    def negate(self):
        try:
            current = float(self.display_var.get())
            self.display_var.set(str(-current))
        except:
            self.display_var.set("Error")
    
    def reciprocal(self):
        try:
            current = float(self.display_var.get())
            if current != 0:
                self.display_var.set(str(1/current))
            else:
                self.display_var.set("Error")
        except:
            self.display_var.set("Error")
    
    def square(self):
        try:
            current = float(self.display_var.get())
            self.display_var.set(str(current**2))
        except:
            self.display_var.set("Error")
    
    def memory_store(self):
        try:
            self.memory = float(self.display_var.get())
        except:
            self.memory = 0
    
    def memory_recall(self):
        self.display_var.set(str(self.memory))
    
    def memory_clear(self):
        self.memory = 0
    
    def memory_add(self):
        try:
            self.memory += float(self.display_var.get())
        except:
            pass
    
    def toggle_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
    
    def exit_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)
    
    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("История вычислений")
        history_window.geometry("400x300")
        
        text_area = scrolledtext.ScrolledText(history_window, wrap=tk.WORD, font=("Arial", 10))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if self.history:
            for i, (expr, result) in enumerate(self.history, 1):
                text_area.insert(tk.END, f"{i}. {expr} = {result}\n")
        else:
            text_area.insert(tk.END, "История пуста")
        
        text_area.config(state=tk.DISABLED)
    
    def calculate(self):
        try:
            expression = self.display_var.get()
            original_expression = expression
            
            # Автоматически добавляем закрывающие скобки если нужно
            if self.auto_bracket:
                open_count = expression.count('(')
                close_count = expression.count(')')
                if open_count > close_count:
                    expression += ')' * (open_count - close_count)
            
            # Replace symbols and constants
            expression = expression.replace('×', '*').replace('÷', '/').replace('^', '**')
            expression = expression.replace('π', str(math.pi)).replace('e', str(math.e))
            
            # Improved function parsing to handle expressions like "6*sin(60)"
            if self.angle_mode.get() == "deg":
                # Convert degrees to radians for trigonometric functions
                expression = self.convert_deg_to_rad(expression)
            else:
                # Ensure radian functions
                expression = self.replace_math_functions(expression)
            
            # Evaluate the expression
            result = eval(expression, {"math": math, "self": self})
            self.display_var.set(str(result))
            self.last_result = result
            
            # Add to history
            self.history.append((original_expression, result))
            if len(self.history) > 10:  # Keep only last 10 calculations
                self.history.pop(0)
            
        except ZeroDivisionError:
            self.display_var.set("Error")
            messagebox.showerror("Ошибка", "Деление на ноль!")
        except Exception as e:
            self.display_var.set("Error")
            messagebox.showerror("Ошибка", f"Некорректное выражение: {e}")
    
    def replace_math_functions(self, expression):
        """Replace function names with math module equivalents"""
        # Use a dictionary to map function names to their math equivalents
        function_map = {
            'sin': 'math.sin',
            'cos': 'math.cos', 
            'tan': 'math.tan',
            'cot': 'self.cot',
            'asin': 'math.asin',
            'acos': 'math.acos',
            'atan': 'math.atan',
            'acot': 'self.acot',
            'sqrt': 'math.sqrt',
            'ln': 'math.log',
            'log': 'math.log10'
        }
        
        # Replace functions in the expression
        for func, replacement in function_map.items():
            # Use regex to replace only function calls (function name followed by parenthesis)
            pattern = r'\b' + re.escape(func) + r'\('
            expression = re.sub(pattern, replacement + '(', expression)
        
        return expression
    
    def convert_deg_to_rad(self, expression):
        """Convert trigonometric functions from degrees to radians"""
        # Use a dictionary to map function names to their math equivalents with degree conversion
        function_map = {
            'sin': 'math.sin',
            'cos': 'math.cos', 
            'tan': 'math.tan',
            'cot': 'self.cot',
            'asin': 'math.asin',
            'acos': 'math.acos',
            'atan': 'math.atan',
            'acot': 'self.acot'
        }
        
        # First, replace function names with math equivalents
        for func, replacement in function_map.items():
            # Use regex to replace only function calls (function name followed by parenthesis)
            pattern = r'\b' + re.escape(func) + r'\('
            expression = re.sub(pattern, replacement + '(', expression)
        
        # Now convert degrees to radians for direct trigonometric functions
        # and radians to degrees for inverse functions
        trig_pattern = r'(math\.(sin|cos|tan|cot|asin|acos|atan|acot))\(([^()]+)\)'
        
        def deg_to_rad_replacement(match):
            full_func = match.group(1)  # e.g., "math.sin"
            func_name = match.group(2)  # e.g., "sin"
            content = match.group(3)    # e.g., "60"
            
            # For direct trigonometric functions, convert argument to radians
            if func_name in ['sin', 'cos', 'tan', 'cot']:
                return f'{full_func}(math.radians({content}))'
            # For inverse trigonometric functions, convert result to degrees
            elif func_name in ['asin', 'acos', 'atan', 'acot']:
                if func_name.startswith('a'):
                    base_func = func_name[1:]  # Remove 'a' prefix
                    if base_func == 'cot':
                        return f'math.degrees(self.{base_func}({content}))'
                    else:
                        return f'math.degrees(math.{base_func}({content}))'
            
            return match.group(0)  # Return original if no conversion needed
        
        # Apply the replacement
        expression = re.sub(trig_pattern, deg_to_rad_replacement, expression)
        
        # Replace other functions
        expression = expression.replace('sqrt(', 'math.sqrt(')
        expression = expression.replace('ln(', 'math.log(')
        expression = expression.replace('log(', 'math.log10(')
        
        return expression
    
    # Additional trigonometric functions
    def cot(self, x):
        try:
            return 1 / math.tan(x)
        except:
            return float('inf')
    
    def acot(self, x):
        return math.pi/2 - math.atan(x)

def main():
    root = tk.Tk()
    calculator = EngineeringCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()