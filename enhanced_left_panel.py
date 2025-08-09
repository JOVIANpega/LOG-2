#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhanced_left_panel.py
用途：提供增強版左側面板建構，從 main_enhanced.py 抽離。
"""
import tkinter as tk

def build_left_panel(app, parent):
    # 標題 - 使用大方塊淺藍色背景
    title_frame = tk.Frame(parent, bg='#E6F3FF', relief=tk.RAISED, bd=2)
    title_frame.pack(fill=tk.X, padx=10, pady=(10, 20))
    
    title_label = tk.Label(title_frame, text="測試LOG分析器", 
                          font=('Arial', 26, 'bold'), fg='#2E86AB', bg='#E6F3FF')
    title_label.pack(pady=10)
    app.font_scaler.register(title_label)
    
    # 檔案選擇區域
    file_frame = tk.LabelFrame(parent, text="檔案選擇", padx=10, pady=10)
    file_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # 單一檔案選擇
    btn_single = tk.Button(file_frame, text="📁 選擇單一檔案", 
                          command=app._select_file, bg='#4CAF50', fg='white')
    btn_single.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_single)
    
    # 資料夾選擇
    btn_folder = tk.Button(file_frame, text="📂 選擇資料夾", 
                          command=app._select_folder, bg='#2196F3', fg='white')
    btn_folder.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_folder)
    
    # 清除結果按鈕
    btn_clear = tk.Button(file_frame, text="🗑️ 清除結果", 
                         command=app._clear_enhanced_results, bg='#F44336', fg='white')
    btn_clear.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_clear)
    
    # 左三個按鈕：加粗與hover
    try:
        from ui_components import make_bold, apply_button_hover
        make_bold(btn_single)
        make_bold(btn_folder)
        make_bold(btn_clear)
        apply_button_hover(btn_single, hover_bg="#66BB6A", hover_fg='white', normal_bg='#4CAF50', normal_fg='white')
        apply_button_hover(btn_folder, hover_bg="#64B5F6", hover_fg='white', normal_bg='#2196F3', normal_fg='white')
        apply_button_hover(btn_clear,  hover_bg="#EF5350", hover_fg='white', normal_bg='#F44336', normal_fg='white')
    except Exception:
        pass
    
    # 說明文件按鈕
    help_btn = tk.Button(parent, text="📖 查看說明(README)", command=app._open_markdown_help, bg="#607D8B", fg="white")
    help_btn.pack(fill=tk.X, padx=10, pady=(8, 8))
    app.font_scaler.register(help_btn)
    try:
        make_bold(help_btn)
        apply_button_hover(help_btn, hover_bg="#78909C", hover_fg='white', normal_bg='#607D8B', normal_fg='white')
    except Exception:
        pass
    
    # 顯示選擇的檔案
    app.file_info_label = tk.Label(file_frame, text="未選擇檔案", 
                                   fg='#666', wraplength=200)
    app.file_info_label.pack(pady=(5, 0))
    app.font_scaler.register(app.file_info_label)
    
    # 介面設定
    font_frame = tk.LabelFrame(parent, text="介面設定", padx=10, pady=10)
    font_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # 介面文字大小控制
    ui_font_frame = tk.Frame(font_frame)
    ui_font_frame.pack(fill=tk.X, pady=2)
    
    tk.Label(ui_font_frame, text="介面文字：").pack(side=tk.LEFT)
    
    btn_ui_minus = tk.Button(ui_font_frame, text="－", width=3, 
                            command=app._decrease_ui_font)
    btn_ui_minus.pack(side=tk.LEFT, padx=2)
    app.font_scaler.register(btn_ui_minus)
    
    app.ui_font_size_label = tk.Label(ui_font_frame, text=str(app.ui_font_size), 
                                      width=3, relief=tk.SUNKEN, font=('Arial', app.ui_font_size))
    app.ui_font_size_label.pack(side=tk.LEFT, padx=2)
    
    btn_ui_plus = tk.Button(ui_font_frame, text="＋", width=3, 
                          command=app._increase_ui_font)
    btn_ui_plus.pack(side=tk.LEFT, padx=2)
    app.font_scaler.register(btn_ui_plus)
    
    # 內容字體大小控制
    content_font_frame = tk.Frame(font_frame)
    content_font_frame.pack(fill=tk.X, pady=2)
    
    tk.Label(content_font_frame, text="內容字體：").pack(side=tk.LEFT)
    
    btn_content_minus = tk.Button(content_font_frame, text="－", width=3, 
                                command=app._decrease_content_font)
    btn_content_minus.pack(side=tk.LEFT, padx=2)
    app.font_scaler.register(btn_content_minus)
    
    app.content_font_size_label = tk.Label(content_font_frame, text=str(app.content_font_size), 
                                          width=3, relief=tk.SUNKEN, font=('Arial', app.content_font_size))
    app.content_font_size_label.pack(side=tk.LEFT, padx=2)
    
    btn_content_plus = tk.Button(content_font_frame, text="＋", width=3, 
                                 command=app._increase_content_font)
    btn_content_plus.pack(side=tk.LEFT, padx=2)
    app.font_scaler.register(btn_content_plus) 