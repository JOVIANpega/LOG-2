# ui_components.py
# 用途：提供GUI元件輔助函式，支援字體大小調整、分割視窗、Tab等
import tkinter as tk
from tkinter import ttk

class FontScaler:
    def __init__(self, root, min_size=10, max_size=15, default_size=11):
        self.root = root
        self.min_size = min_size
        self.max_size = max_size
        self.font_size = default_size
        self.widgets = []

    def register(self, widget):
        self.widgets.append(widget)

    def set_font_size(self, size):
        self.font_size = max(self.min_size, min(self.max_size, size))
        for w in self.widgets:
            try:
                w.configure(font=(None, self.font_size))
            except Exception:
                pass

    def apply_to_treeview(self, tree):
        style = ttk.Style()
        style.configure("Treeview", font=(None, self.font_size))
        style.configure("Treeview.Heading", font=(None, self.font_size)) 