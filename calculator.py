#!/usr/bin/env python3
"""
Advanced Calculator Application
A comprehensive calculator with GUI built using tkinter, featuring basic arithmetic,
advanced mathematical functions, memory operations, and calculation history.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import decimal
from decimal import Decimal, getcontext
import re
from typing import List, Tuple, Optional, Union
import logging

# Configure decimal precision for high accuracy
getcontext().prec = 50

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CalculatorEngine:
    """Core calculation engine handling mathematical operations and expression parsing."""
    
    def __init__(self):
        self.angle_mode = 'DEG'  # 'DEG' or 'RAD'
        self.memory = Decimal('0')
        self.history: List[Tuple[str, str]] = []  # (expression, result)
        
    def set_angle_mode(self, mode: str) -> None:
        """Set angle mode to DEG or RAD."""
        if mode in ['DEG', 'RAD']:
            self.angle_mode = mode
            logger.info(f"Angle mode set to {mode}")
    
    def deg_to_rad(self, degrees: float) -> float:
        """Convert degrees to radians."""
        return math.radians(degrees)
    
    def rad_to_deg(self, radians: float) -> float:
        """Convert radians to degrees."""
        return math.degrees(radians)
    
    def safe_eval(self, expression: str) -> Union[Decimal, str]:
        """
        Safely evaluate mathematical expressions with comprehensive error handling.
        Returns Decimal result or error message string.
        """
        try:
            # Clean and validate expression
            expression = expression.strip()
            if not expression:
                return "Error: Empty expression"
            
            # Replace common mathematical symbols and functions
            expression = self._preprocess_expression(expression)
            
            # Validate expression for security
            if not self._is_safe_expression(expression):
                return "Error: Invalid expression"
            
            # Evaluate using decimal for high precision
            result = self._evaluate_expression(expression)
            
            # Check for special cases
            if isinstance(result, (float, int)):
                if math.isnan(result):
                    return "Error: Not a number"
                if math.isinf(result):
                    return "Error: Infinity"
            
            return Decimal(str(result))
            
        except ZeroDivisionError:
            return "Error: Division by zero"
        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in safe_eval: {e}")
            return "Error: Invalid expression"
    
    def _preprocess_expression(self, expression: str) -> str:
        """Preprocess expression to handle mathematical functions and constants."""
        # Replace constants
        expression = expression.replace('π', str(math.pi))
        expression = expression.replace('pi', str(math.pi))
        expression = expression.replace('e', str(math.e))
        
        # Replace power operator
        expression = expression.replace('^', '**')
        
        # Handle trigonometric functions with angle mode conversion
        trig_functions = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh']
        
        for func in trig_functions:
            pattern = rf'{func}\s*\(([^)]+)\)'
            matches = re.finditer(pattern, expression)
            
            for match in reversed(list(matches)):  # Reverse to avoid index issues
                arg = match.group(1)
                start, end = match.span()
                
                if func in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']:
                    # Convert to radians if in degree mode
                    if self.angle_mode == 'DEG':
                        replacement = f'{func}(math.radians({arg}))'
                    else:
                        replacement = f'{func}({arg})'
                else:
                    replacement = f'math.{func}({arg})'
                
                expression = expression[:start] + replacement + expression[end:]
        
        # Handle other mathematical functions
        expression = re.sub(r'sqrt\s*\(([^)]+)\)', r'math.sqrt(\1)', expression)
        expression = re.sub(r'log\s*\(([^)]+)\)', r'math.log10(\1)', expression)
        expression = re.sub(r'ln\s*\(([^)]+)\)', r'math.log(\1)', expression)
        expression = re.sub(r'abs\s*\(([^)]+)\)', r'abs(\1)', expression)
        expression = re.sub(r'factorial\s*\(([^)]+)\)', r'math.factorial(\1)', expression)
        
        return expression
    
    def _is_safe_expression(self, expression: str) -> bool:
        """Validate that expression contains only safe mathematical operations."""
        # Allowed characters and patterns
        allowed_pattern = r'^[0-9+\-*/().\s,math\.\w]+$'
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'__',  # Double underscores
            r'import',  # Import statements
            r'exec',  # Exec statements
            r'eval',  # Eval statements
            r'open',  # File operations
            r'file',  # File operations
        ]
        
        if not re.match(allowed_pattern, expression):
            return False
        
        for pattern in dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return False
        
        return True
    
    def _evaluate_expression(self, expression: str) -> Union[float, int]:
        """Evaluate the preprocessed expression safely."""
        # Create a safe namespace for evaluation
        safe_dict = {
            'math': math,
            'abs': abs,
            'Decimal': Decimal,
        }
        
        return eval(expression, {"__builtins__": {}}, safe_dict)
    
    def calculate_percentage(self, value: str, percentage: str) -> Union[Decimal, str]:
        """Calculate percentage (e.g., 100 + 10% = 110)."""
        try:
            val = Decimal(value)
            pct = Decimal(percentage)
            result = val + (val * pct / 100)
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    def memory_store(self, value: Union[Decimal, str]) -> None:
        """Store value in memory."""
        try:
            if isinstance(value, str):
                if value.startswith("Error:"):
                    return
                self.memory = Decimal(value)
            else:
                self.memory = value
            logger.info(f"Memory stored: {self.memory}")
        except Exception as e:
            logger.error(f"Error storing in memory: {e}")
    
    def memory_recall(self) -> Decimal:
        """Recall value from memory."""
        return self.memory
    
    def memory_clear(self) -> None:
        """Clear memory."""
        self.memory = Decimal('0')
        logger.info("Memory cleared")
    
    def memory_add(self, value: Union[Decimal, str]) -> None:
        """Add value to memory."""
        try:
            if isinstance(value, str):
                if value.startswith("Error:"):
                    return
                val = Decimal(value)
            else:
                val = value
            self.memory += val
            logger.info(f"Memory add: {self.memory}")
        except Exception as e:
            logger.error(f"Error adding to memory: {e}")
    
    def memory_subtract(self, value: Union[Decimal, str]) -> None:
        """Subtract value from memory."""
        try:
            if isinstance(value, str):
                if value.startswith("Error:"):
                    return
                val = Decimal(value)
            else:
                val = value
            self.memory -= val
            logger.info(f"Memory subtract: {self.memory}")
        except Exception as e:
            logger.error(f"Error subtracting from memory: {e}")
    
    def add_to_history(self, expression: str, result: str) -> None:
        """Add calculation to history."""
        self.history.append((expression, result))
        # Keep only last 100 calculations
        if len(self.history) > 100:
            self.history.pop(0)
        logger.info(f"Added to history: {expression} = {result}")
    
    def get_history(self) -> List[Tuple[str, str]]:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()
        logger.info("History cleared")


class CalculatorGUI:
    """Main GUI class for the calculator application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.engine = CalculatorEngine()
        self.current_expression = ""
        self.current_result = "0"
        self.is_new_calculation = True
        self.dark_theme = False
        
        self.setup_gui()
        self.setup_keyboard_bindings()
        
    def setup_gui(self):
        """Initialize the GUI components."""
        self.root.title("Advanced Calculator")
        self.root.geometry("450x700")
        self.root.resizable(True, True)
        self.root.configure(bg='#2b2b2b')
        
        # Set window icon and styling
        self.root.configure(relief='flat', bd=0)
        
        # Configure style
        self.setup_styles()
        
        # Create main frame with modern styling
        main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create display frame
        self.create_display_frame(main_frame)
        
        # Create control frame
        self.create_control_frame(main_frame)
        
        # Create button frame
        self.create_button_frame(main_frame)
        
        # Create status bar
        self.create_status_bar(main_frame)
        
    def setup_styles(self):
        """Setup custom styles for the calculator."""
        style = ttk.Style()
        
        # Configure modern dark theme
        style.theme_use('clam')
        
        # Configure button styles with modern colors
        style.configure('Number.TButton', 
                       font=('Segoe UI', 14, 'bold'),
                       background='#404040',
                       foreground='#ffffff',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(10, 10))
        
        style.map('Number.TButton',
                 background=[('active', '#505050'),
                           ('pressed', '#606060')])
        
        style.configure('Operator.TButton',
                       font=('Segoe UI', 14, 'bold'),
                       background='#ff6b35',
                       foreground='#ffffff',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(10, 10))
        
        style.map('Operator.TButton',
                 background=[('active', '#ff7b45'),
                           ('pressed', '#ff8b55')])
        
        style.configure('Function.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       background='#4a90e2',
                       foreground='#ffffff',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(8, 8))
        
        style.map('Function.TButton',
                 background=[('active', '#5aa0f2'),
                           ('pressed', '#6ab0ff')])
        
        style.configure('Memory.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       background='#7b68ee',
                       foreground='#ffffff',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(6, 6))
        
        style.map('Memory.TButton',
                 background=[('active', '#8b78fe'),
                           ('pressed', '#9b88ff')])
        
        style.configure('Equals.TButton',
                       font=('Segoe UI', 16, 'bold'),
                       background='#32cd32',
                       foreground='#ffffff',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(10, 15))
        
        style.map('Equals.TButton',
                 background=[('active', '#42dd42'),
                           ('pressed', '#52ed52')])
        
    def create_display_frame(self, parent):
        """Create the display area for expressions and results."""
        display_frame = tk.Frame(parent, bg='#2b2b2b')
        display_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Create rounded display container
        display_container = tk.Frame(display_frame, bg='#1a1a1a', relief='flat', bd=0)
        display_container.pack(fill=tk.X, ipady=15)
        
        # Expression display (smaller, top)
        self.expression_var = tk.StringVar(value="")
        self.expression_display = tk.Label(
            display_container,
            textvariable=self.expression_var,
            font=('Segoe UI', 14),
            fg='#888888',
            bg='#1a1a1a',
            anchor='e',
            padx=25,
            pady=15
        )
        self.expression_display.pack(fill=tk.X)
        
        # Result display (larger, bottom)
        self.result_var = tk.StringVar(value="0")
        self.result_display = tk.Label(
            display_container,
            textvariable=self.result_var,
            font=('Segoe UI', 28, 'bold'),
            fg='#ffffff',
            bg='#1a1a1a',
            anchor='e',
            padx=25,
            pady=15
        )
        self.result_display.pack(fill=tk.X)
        
    def create_control_frame(self, parent):
        """Create control buttons (clear, memory, etc.)."""
        control_frame = tk.Frame(parent, bg='#2b2b2b')
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # First row of controls
        control_row1 = tk.Frame(control_frame, bg='#2b2b2b')
        control_row1.pack(fill=tk.X, pady=(0, 8))
        
        # Clear buttons
        ttk.Button(control_row1, text="C", command=self.clear_entry, style='Operator.TButton').pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        ttk.Button(control_row1, text="AC", command=self.clear_all, style='Operator.TButton').pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        ttk.Button(control_row1, text="DEL", command=self.backspace, style='Operator.TButton').pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        
        # Memory buttons
        ttk.Button(control_row1, text="MS", command=self.memory_store, style='Memory.TButton').pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        ttk.Button(control_row1, text="MR", command=self.memory_recall, style='Memory.TButton').pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Second row of controls
        control_row2 = tk.Frame(control_frame, bg='#2b2b2b')
        control_row2.pack(fill=tk.X)
        
        ttk.Button(control_row2, text="MC", command=self.memory_clear, style='Memory.TButton').pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        ttk.Button(control_row2, text="M+", command=self.memory_add, style='Memory.TButton').pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        ttk.Button(control_row2, text="M-", command=self.memory_subtract, style='Memory.TButton').pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        ttk.Button(control_row2, text="HIST", command=self.show_history, style='Function.TButton').pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        ttk.Button(control_row2, text="DEG/RAD", command=self.toggle_angle_mode, style='Function.TButton').pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def create_button_frame(self, parent):
        """Create the main button grid."""
        button_frame = tk.Frame(parent, bg='#2b2b2b')
        button_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create button rows
        self.create_button_row(button_frame, [
            ("sin", lambda: self.add_function("sin("), "Function.TButton"),
            ("cos", lambda: self.add_function("cos("), "Function.TButton"),
            ("tan", lambda: self.add_function("tan("), "Function.TButton"),
            ("log", lambda: self.add_function("log("), "Function.TButton"),
            ("ln", lambda: self.add_function("ln("), "Function.TButton")
        ])
        
        self.create_button_row(button_frame, [
            ("√", lambda: self.add_function("sqrt("), "Function.TButton"),
            ("x²", lambda: self.add_function("^2"), "Function.TButton"),
            ("x^y", lambda: self.add_function("^"), "Function.TButton"),
            ("1/x", lambda: self.add_function("1/"), "Function.TButton"),
            ("|x|", lambda: self.add_function("abs("), "Function.TButton")
        ])
        
        self.create_button_row(button_frame, [
            ("π", lambda: self.add_number("π"), "Function.TButton"),
            ("e", lambda: self.add_number("e"), "Function.TButton"),
            ("n!", lambda: self.add_function("factorial("), "Function.TButton"),
            ("%", lambda: self.add_operator("%"), "Function.TButton"),
            ("(", lambda: self.add_operator("("), "Function.TButton")
        ])
        
        self.create_button_row(button_frame, [
            ("7", lambda: self.add_number("7"), "Number.TButton"),
            ("8", lambda: self.add_number("8"), "Number.TButton"),
            ("9", lambda: self.add_number("9"), "Number.TButton"),
            ("/", lambda: self.add_operator("/"), "Operator.TButton"),
            (")", lambda: self.add_operator(")"), "Function.TButton")
        ])
        
        self.create_button_row(button_frame, [
            ("4", lambda: self.add_number("4"), "Number.TButton"),
            ("5", lambda: self.add_number("5"), "Number.TButton"),
            ("6", lambda: self.add_number("6"), "Number.TButton"),
            ("*", lambda: self.add_operator("*"), "Operator.TButton"),
            ("±", self.toggle_sign, "Operator.TButton")
        ])
        
        self.create_button_row(button_frame, [
            ("1", lambda: self.add_number("1"), "Number.TButton"),
            ("2", lambda: self.add_number("2"), "Number.TButton"),
            ("3", lambda: self.add_number("3"), "Number.TButton"),
            ("-", lambda: self.add_operator("-"), "Operator.TButton"),
            ("=", self.calculate, "Equals.TButton")
        ])
        
        # Bottom row with wider 0 button
        bottom_row = tk.Frame(button_frame, bg='#2b2b2b')
        bottom_row.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Button(bottom_row, text="0", command=lambda: self.add_number("0"), style='Number.TButton').pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        ttk.Button(bottom_row, text="0", command=lambda: self.add_number("0"), style='Number.TButton').pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        ttk.Button(bottom_row, text=".", command=self.add_decimal, style='Number.TButton').pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        ttk.Button(bottom_row, text="+", command=lambda: self.add_operator("+"), style='Operator.TButton').pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_button_row(self, parent, buttons):
        """Create a row of buttons with consistent spacing."""
        row_frame = tk.Frame(parent, bg='#2b2b2b')
        row_frame.pack(fill=tk.X, pady=(0, 8))
        
        for i, (text, command, style) in enumerate(buttons):
            if i < len(buttons) - 1:
                ttk.Button(row_frame, text=text, command=command, style=style).pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
            else:
                ttk.Button(row_frame, text=text, command=command, style=style).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_status_bar(self, parent):
        """Create status bar showing angle mode and memory indicator."""
        status_frame = tk.Frame(parent, bg='#2b2b2b')
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Status info
        self.status_var = tk.StringVar(value="DEG | M: 0")
        status_label = tk.Label(
            status_frame, 
            textvariable=self.status_var, 
            font=('Segoe UI', 10),
            fg='#888888',
            bg='#2b2b2b'
        )
        status_label.pack(side=tk.LEFT)
        
        # Theme toggle button
        theme_btn = tk.Button(
            status_frame,
            text="🌙",
            command=self.toggle_theme,
            font=('Segoe UI', 12),
            bg='#404040',
            fg='#ffffff',
            relief='flat',
            bd=0,
            padx=10,
            pady=5
        )
        theme_btn.pack(side=tk.RIGHT)
    
    def setup_keyboard_bindings(self):
        """Setup keyboard shortcuts."""
        self.root.bind('<Key>', self.on_key_press)
        self.root.focus_set()
        
    def on_key_press(self, event):
        """Handle keyboard input."""
        key = event.char
        keysym = event.keysym
        
        # Numbers
        if key.isdigit():
            self.add_number(key)
        # Decimal point
        elif key == '.':
            self.add_decimal()
        # Operators
        elif key in ['+', '-', '*', '/']:
            self.add_operator(key)
        # Equals
        elif key in ['=', '\r', '\n']:
            self.calculate()
        # Clear
        elif keysym == 'Escape':
            self.clear_all()
        # Backspace
        elif keysym == 'BackSpace':
            self.backspace()
        # Special functions
        elif key.lower() == 's':
            self.add_function("sin(")
        elif key.lower() == 'c':
            self.add_function("cos(")
        elif key.lower() == 't':
            self.add_function("tan(")
        elif key == '^':
            self.add_operator("^")
        elif key == '(':
            self.add_operator("(")
        elif key == ')':
            self.add_operator(")")
    
    def add_number(self, number: str):
        """Add a number to the current expression."""
        if self.is_new_calculation:
            self.current_expression = number
            self.is_new_calculation = False
        else:
            self.current_expression += number
        
        self.update_display()
    
    def add_operator(self, operator: str):
        """Add an operator to the current expression."""
        if self.is_new_calculation and operator in ['+', '-']:
            self.current_expression = operator
            self.is_new_calculation = False
        else:
            self.current_expression += operator
        
        self.update_display()
    
    def add_function(self, function: str):
        """Add a mathematical function to the current expression."""
        self.current_expression += function
        self.is_new_calculation = False
        self.update_display()
    
    def add_decimal(self):
        """Add decimal point to the current expression."""
        if self.is_new_calculation:
            self.current_expression = "0."
            self.is_new_calculation = False
        else:
            # Check if current number already has decimal point
            if not self.current_expression or self.current_expression[-1] in '+-*/^(':
                self.current_expression += "0."
            elif '.' not in self.current_expression.split()[-1] if ' ' in self.current_expression else '.' not in self.current_expression:
                self.current_expression += "."
        
        self.update_display()
    
    def toggle_sign(self):
        """Toggle the sign of the current number."""
        if self.current_expression and not self.is_new_calculation:
            if self.current_expression.startswith('-'):
                self.current_expression = self.current_expression[1:]
            else:
                self.current_expression = '-' + self.current_expression
            self.update_display()
    
    def clear_entry(self):
        """Clear the current entry."""
        self.current_expression = ""
        self.current_result = "0"
        self.is_new_calculation = True
        self.update_display()
    
    def clear_all(self):
        """Clear everything."""
        self.current_expression = ""
        self.current_result = "0"
        self.is_new_calculation = True
        self.engine.clear_history()
        self.update_display()
        self.update_status()
    
    def backspace(self):
        """Remove the last character from the current expression."""
        if self.current_expression:
            self.current_expression = self.current_expression[:-1]
            if not self.current_expression:
                self.is_new_calculation = True
            self.update_display()
    
    def calculate(self):
        """Calculate the current expression."""
        if not self.current_expression:
            return
        
        try:
            result = self.engine.safe_eval(self.current_expression)
            
            if isinstance(result, str) and result.startswith("Error:"):
                self.current_result = result
                self.expression_var.set(self.current_expression)
            else:
                # Format result for display
                if isinstance(result, Decimal):
                    if result == int(result):
                        self.current_result = str(int(result))
                    else:
                        self.current_result = str(result)
                else:
                    self.current_result = str(result)
                
                # Add to history
                self.engine.add_to_history(self.current_expression, self.current_result)
                
                # Update expression display
                self.expression_var.set(f"{self.current_expression} =")
            
            self.is_new_calculation = True
            self.update_display()
            self.update_status()
            
        except Exception as e:
            logger.error(f"Error in calculate: {e}")
            self.current_result = "Error: Calculation failed"
            self.update_display()
    
    def memory_store(self):
        """Store current result in memory."""
        if not self.current_result.startswith("Error:"):
            self.engine.memory_store(self.current_result)
            self.update_status()
    
    def memory_recall(self):
        """Recall value from memory."""
        memory_value = self.engine.memory_recall()
        self.current_expression = str(memory_value)
        self.is_new_calculation = True
        self.update_display()
    
    def memory_clear(self):
        """Clear memory."""
        self.engine.memory_clear()
        self.update_status()
    
    def memory_add(self):
        """Add current result to memory."""
        if not self.current_result.startswith("Error:"):
            self.engine.memory_add(self.current_result)
            self.update_status()
    
    def memory_subtract(self):
        """Subtract current result from memory."""
        if not self.current_result.startswith("Error:"):
            self.engine.memory_subtract(self.current_result)
            self.update_status()
    
    def toggle_angle_mode(self):
        """Toggle between degree and radian mode."""
        if self.engine.angle_mode == 'DEG':
            self.engine.set_angle_mode('RAD')
        else:
            self.engine.set_angle_mode('DEG')
        self.update_status()
    
    def show_history(self):
        """Show calculation history in a new window."""
        history = self.engine.get_history()
        
        if not history:
            messagebox.showinfo("History", "No calculations in history.")
            return
        
        # Create history window with modern styling
        history_window = tk.Toplevel(self.root)
        history_window.title("Calculation History")
        history_window.geometry("600x500")
        history_window.configure(bg='#2b2b2b')
        history_window.resizable(True, True)
        
        # Create header
        header_frame = tk.Frame(history_window, bg='#1a1a1a', height=50)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="📊 Calculation History",
            font=('Segoe UI', 16, 'bold'),
            fg='#ffffff',
            bg='#1a1a1a'
        )
        title_label.pack(expand=True)
        
        # Create frame with scrollbar
        frame = tk.Frame(history_window, bg='#2b2b2b')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create listbox with modern styling
        listbox = tk.Listbox(
            frame, 
            font=('Segoe UI', 11),
            bg='#1a1a1a',
            fg='#ffffff',
            selectbackground='#4a90e2',
            selectforeground='#ffffff',
            relief='flat',
            bd=0,
            highlightthickness=0
        )
        
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview, bg='#404040')
        listbox.configure(yscrollcommand=scrollbar.set)
        
        # Add history items
        for i, (expression, result) in enumerate(history, 1):
            listbox.insert(tk.END, f"{i:3d}. {expression} = {result}")
        
        # Pack widgets
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add buttons with modern styling
        button_frame = tk.Frame(history_window, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear History",
            command=lambda: self.clear_history(history_window),
            font=('Segoe UI', 10, 'bold'),
            bg='#ff6b35',
            fg='#ffffff',
            relief='flat',
            bd=0,
            padx=20,
            pady=8
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(
            button_frame,
            text="❌ Close",
            command=history_window.destroy,
            font=('Segoe UI', 10, 'bold'),
            bg='#404040',
            fg='#ffffff',
            relief='flat',
            bd=0,
            padx=20,
            pady=8
        )
        close_btn.pack(side=tk.RIGHT)
    
    def clear_history(self, window):
        """Clear calculation history."""
        self.engine.clear_history()
        window.destroy()
        messagebox.showinfo("History", "History cleared.")
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.dark_theme = not self.dark_theme
        
        if self.dark_theme:
            # Already in dark theme, show message
            messagebox.showinfo("Theme", "Already using dark theme! 🌙")
        else:
            # This is a placeholder for light theme switching
            messagebox.showinfo("Theme", "Light theme coming soon! ☀️")
    
    def update_display(self):
        """Update the display with current expression and result."""
        self.expression_var.set(self.current_expression)
        self.result_var.set(self.current_result)
    
    def update_status(self):
        """Update the status bar."""
        memory_value = self.engine.memory_recall()
        status_text = f"{self.engine.angle_mode} | M: {memory_value}"
        self.status_var.set(status_text)
    
    def run(self):
        """Start the calculator application."""
        self.update_status()
        self.root.mainloop()


def main():
    """Main function to run the calculator."""
    try:
        calculator = CalculatorGUI()
        calculator.run()
    except Exception as e:
        logger.error(f"Failed to start calculator: {e}")
        messagebox.showerror("Error", f"Failed to start calculator: {e}")


if __name__ == "__main__":
    main()
