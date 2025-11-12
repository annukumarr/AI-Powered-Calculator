import tkinter as tk
from tkinter import ttk, messagebox
import re, math, ast, operator

_ALLOWED_FUNCS = {
    'abs': abs, 'round': round,
    'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'log': math.log, 'log10': math.log10, 'exp': math.exp,
    'pi': math.pi, 'e': math.e, 'floor': math.floor, 'ceil': math.ceil
}
_ALLOWED_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.UAdd: operator.pos
}

def _eval_node(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)): return node.value
        raise ValueError("Unsupported constant")
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPS: raise ValueError("Operator not allowed")
        return _ALLOWED_OPS[op_type](left, right)
    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPS: raise ValueError("Operator not allowed")
        return _ALLOWED_OPS[op_type](operand)
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name): raise ValueError("Func not allowed")
        fname = node.func.id
        if fname not in _ALLOWED_FUNCS: raise ValueError(f"Function {fname} not allowed")
        args = [_eval_node(a) for a in node.args]
        return _ALLOWED_FUNCS[fname](*args)
    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_FUNCS: return _ALLOWED_FUNCS[node.id]
        raise ValueError(f"Name {node.id} not allowed")
    if isinstance(node, ast.Expr):
        return _eval_node(node.value)
    raise ValueError("Unsupported expression")

def safe_eval(expr: str):
    expr = expr.strip()
    tree = ast.parse(expr, mode='eval')
    return _eval_node(tree.body)

def gcd(a, b):
    return math.gcd(int(a), int(b))

def lcm(a, b):
    a, b = int(a), int(b)
    return abs(a*b)//math.gcd(a,b) if a and b else 0

def parse_nl(query: str):
    q = query.lower().strip()
    q = q.replace(" and ", " & ")

    m = re.search(r'(\d+(\.\d+)?)\s*%\s*of\s*(\d+(\.\d+)?)', q)
    if m:
        p = float(m.group(1)); base = float(m.group(3))
        res = base * p / 100.0
        return res, f"{p}% of {base} = {base} * {p}/100"

    m = re.search(r'(sum|add)\s*(of)?\s*(\d+(\.\d+)?)[^\d]+(\d+(\.\d+)?)', q)
    if m:
        a = float(m.group(3)); b = float(m.group(5))
        return a + b, f"Sum of {a} and {b}"

    m = re.search(r'(subtract|difference)\s*(\d+(\.\d+)?)\s*(from|and|between)\s*(\d+(\.\d+)?)', q)
    if m:
        a = float(m.group(2)); b = float(m.group(5))
        if m.group(4) == 'from':
            return b - a, f"{b} - {a}"
        else:
            return a - b, f"{a} - {b}"

    m = re.search(r'(product|multiply)\s*(\d+(\.\d+)?)\D+(\d+(\.\d+)?)', q)
    if m:
        a = float(m.group(2)); b = float(m.group(4))
        return a * b, f"{a} × {b}"

    m = re.search(r'(divide|quotient)\s*(\d+(\.\d+)?)\s*(by)\s*(\d+(\.\d+)?)', q)
    if m:
        a = float(m.group(2)); b = float(m.group(5))
        if b == 0: raise ZeroDivisionError("Division by zero")
        return a / b, f"{a} ÷ {b}"

    m = re.search(r'(\d+(\.\d+)?)\s*(\^|to the power of|to the power)\s*(\d+(\.\d+)?)', q)
    if m:
        a = float(m.group(1)); b = float(m.group(4))
        return a ** b, f"{a}^{b}"

    m = re.search(r'(square|cube)\s*(of)?\s*(\d+(\.\d+)?)', q)
    if m:
        kind = m.group(1); x = float(m.group(3))
        if kind == 'square':
            return x**2, f"square({x})"
        else:
            return x**3, f"cube({x})"

    m = re.search(r'(square\s*root|sqrt)\s*(of)?\s*(\d+(\.\d+)?)', q)
    if m:
        x = float(m.group(3))
        if x < 0: raise ValueError("Square root of negative not supported")
        return math.sqrt(x), f"√({x})"

    m = re.search(r'(gcd|hcf|lcm)\s*(of)?\s*(\d+)\D+(\d+)', q)
    if m:
        a = int(m.group(3)); b = int(m.group(4))
        if m.group(1) in ('gcd','hcf'):
            return gcd(a,b), f"gcd({a}, {b})"
        else:
            return lcm(a,b), f"lcm({a}, {b})"

    m = re.search(r'(increase|decrease)\s*(\d+(\.\d+)?)\s*by\s*(\d+(\.\d+)?)\s*%', q)
    if m:
        kind = m.group(1); base = float(m.group(2)); p = float(m.group(4))
        if kind == 'increase':
            res = base * (1 + p/100.0)
            return res, f"{base} increased by {p}%"
        else:
            res = base * (1 - p/100.0)
            return res, f"{base} decreased by {p}%"

    return None, None

class AICalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI-Powered Calculator")
        self.geometry("420x560")
        self.configure(bg="#f5f7fb")

        title = tk.Label(self, text="AI-Powered Calculator",
                         bg="#4b9cd3", fg="white",
                         font=("Segoe UI", 16, "bold"), pady=10)
        title.pack(fill="x")

        self.expr_var = tk.StringVar()
        expr_frame = tk.Frame(self, bg="#f5f7fb")
        expr_frame.pack(padx=12, pady=(14,6), fill="x")
        tk.Label(expr_frame, text="Expression:",
                 bg="#f5f7fb", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.expr_entry = ttk.Entry(expr_frame, textvariable=self.expr_var, font=("Consolas", 14))
        self.expr_entry.pack(fill="x", pady=4)

        self.nl_var = tk.StringVar()
        tk.Label(expr_frame, text="Ask in Natural Language:",
                 bg="#f5f7fb", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(8,0))
        self.nl_entry = ttk.Entry(expr_frame, textvariable=self.nl_var, font=("Segoe UI", 12))
        self.nl_entry.pack(fill="x", pady=4)

        btns = tk.Frame(self, bg="#f5f7fb")
        btns.pack(padx=12, pady=8, fill="x")
        ttk.Button(btns, text="Calculate (Expr)", command=self.calculate_expr).grid(row=0, column=0, padx=6, pady=4)
        ttk.Button(btns, text="Ask AI", command=self.calculate_nl).grid(row=0, column=1, padx=6, pady=4)
        ttk.Button(btns, text="Clear", command=self.clear_all).grid(row=0, column=2, padx=6, pady=4)

        res_frame = tk.Frame(self, bg="#f5f7fb")
        res_frame.pack(padx=12, pady=6, fill="both", expand=True)
        tk.Label(res_frame, text="Result:",
                 bg="#f5f7fb", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.result_var = tk.StringVar()
        tk.Label(res_frame, textvariable=self.result_var, bg="#ffffff",
                 relief="groove", font=("Consolas", 16), anchor="w",
                 height=2).pack(fill="x", pady=(4,10))

        tk.Label(res_frame, text="AI Understanding / Steps:",
                 bg="#f5f7fb", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.explain = tk.Text(res_frame, height=8, font=("Consolas", 11), relief="groove")
        self.explain.pack(fill="both", expand=True, pady=4)

        self.build_keypad()
        self.history = []

    def build_keypad(self):
        pad = tk.Frame(self, bg="#eef2f7")
        pad.pack(padx=12, pady=8)
        buttons = [
            ('7','8','9','/','sqrt('),
            ('4','5','6','*','^'),
            ('1','2','3','-','('),
            ('0','.','=','+',' )'),
        ]
        for r,row in enumerate(buttons):
            for c,ch in enumerate(row):
                ttk.Button(pad, text=ch.strip(), width=8,
                           command=lambda ch=ch: self.on_key(ch.strip())).grid(row=r, column=c, padx=4, pady=4)

    def on_key(self, ch):
        if ch == '=':
            self.calculate_expr()
        else:
            if ch == '^': ch = '**'
            cur = self.expr_var.get()
            self.expr_var.set(cur + ch)

    def clear_all(self):
        self.expr_var.set('')
        self.nl_var.set('')
        self.result_var.set('')
        self.explain.delete('1.0','end')

    def calculate_expr(self):
        expr = self.expr_var.get().strip()
        if not expr:
            messagebox.showinfo("Info", "Please type an expression, e.g., 2+3*4 or sqrt(16)")
            return
        try:
            res = safe_eval(expr)
            self.result_var.set(self._fmt(res))
            self._set_explain([f"Expression: {expr}", "Evaluated safely (allowed ops & math functions)."])
            self.history.append((expr, res))
        except Exception as e:
            messagebox.showerror("Error", f"Invalid expression:\n{e}")

    def calculate_nl(self):
        q = self.nl_var.get().strip()
        if not q:
            messagebox.showinfo("Info", "Try: '20% of 150', 'sum of 12 and 5', 'gcd of 24 and 18', 'square root of 49'")
            return
        try:
            res, why = parse_nl(q)
            steps = []
            if res is not None:
                steps.append(f"AI understood: {why}")
                steps.append(f"Computed result = {self._fmt(res)}")
                self.result_var.set(self._fmt(res))
                self._set_explain(steps)
                self.history.append((q, res))
                return
            res = safe_eval(q.replace('^','**'))
            self.result_var.set(self._fmt(res))
            self._set_explain([f"No direct rule matched. Treated as expression:",
                               f"{q}", "Evaluated safely."])
            self.history.append((q, res))
        except ZeroDivisionError:
            messagebox.showerror("Error", "Division by zero.")
        except Exception as e:
            messagebox.showerror("Error", f"Couldn't understand:\n{e}")

    def _fmt(self, x):
        if isinstance(x, float):
            return f"{x:.10g}"
        return str(x)

    def _set_explain(self, lines):
        self.explain.delete('1.0','end')
        self.explain.insert('end', "\n".join(lines))

if __name__ == "__main__":
    app = AICalculator()
    app.mainloop()
