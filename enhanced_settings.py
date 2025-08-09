#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhanced_settings.py
用途：提供增強版設定頁面內容建構函式，從 main_enhanced.py 抽離以降低主檔案行數。
"""
import tkinter as tk
from tkinter import ttk

def build_settings_content(app, parent):
    """建立設定內容（從 app._build_settings_content 抽出）"""
    # 標題
    title_label = tk.Label(parent, text="應用程式設定", 
                          font=('Arial', 16, 'bold'), fg='#2E86AB')
    title_label.pack(pady=(20, 30))
    
    # 視窗大小設定區域
    window_frame = tk.LabelFrame(parent, text="視窗大小設定", padx=20, pady=20)
    window_frame.pack(fill=tk.X, padx=20, pady=10)
    
    # 左側面板寬度控制
    pane_frame = tk.Frame(window_frame)
    pane_frame.pack(fill=tk.X, pady=10)
    
    tk.Label(pane_frame, text="左側面板寬度：", font=('Arial', 12)).pack(side=tk.LEFT)
    
    # 獲取當前左側面板寬度
    current_pane_width = app.settings.get('pane_width', 250)
    
    # 減少按鈕
    btn_pane_minus = tk.Button(pane_frame, text="－", width=3, 
                              command=app._decrease_pane_width)
    btn_pane_minus.pack(side=tk.LEFT, padx=5)
    
    # 顯示當前寬度
    app.pane_width_label = tk.Label(pane_frame, text=f"{current_pane_width}px", 
                                    width=8, relief=tk.SUNKEN, font=('Arial', 12))
    app.pane_width_label.pack(side=tk.LEFT, padx=5)
    
    # 增加按鈕
    btn_pane_plus = tk.Button(pane_frame, text="＋", width=3, 
                             command=app._increase_pane_width)
    btn_pane_plus.pack(side=tk.LEFT, padx=5)
    
    # 重置按鈕
    btn_pane_reset = tk.Button(pane_frame, text="重置", 
                              command=app._reset_pane_width)
    btn_pane_reset.pack(side=tk.LEFT, padx=10)
    
    # 說明文字
    info_label = tk.Label(window_frame, text="調整左側面板的寬度，影響檔案選擇區域的大小", 
                         fg='#666', font=('Arial', 10))
    info_label.pack(pady=(10, 0))
    
    # 分隔線
    separator = ttk.Separator(parent, orient='horizontal')
    separator.pack(fill=tk.X, padx=20, pady=20)
    
    # 字體設定區域
    font_frame = tk.LabelFrame(parent, text="字體設定", padx=20, pady=20)
    font_frame.pack(fill=tk.X, padx=20, pady=10)
    
    # 介面文字大小控制
    ui_font_frame = tk.Frame(font_frame)
    ui_font_frame.pack(fill=tk.X, pady=5)
    
    tk.Label(ui_font_frame, text="介面文字大小：", font=('Arial', 12)).pack(side=tk.LEFT)
    
    btn_ui_minus = tk.Button(ui_font_frame, text="－", width=3, 
                            command=app._decrease_ui_font)
    btn_ui_minus.pack(side=tk.LEFT, padx=5)
    
    app.settings_ui_font_size_label = tk.Label(ui_font_frame, text=str(app.ui_font_size), 
                                      width=3, relief=tk.SUNKEN, font=('Arial', 12))
    app.settings_ui_font_size_label.pack(side=tk.LEFT, padx=5)
    
    btn_ui_plus = tk.Button(ui_font_frame, text="＋", width=3, 
                          command=app._increase_ui_font)
    btn_ui_plus.pack(side=tk.LEFT, padx=5)
    
    # 內容字體大小控制
    content_font_frame = tk.Frame(font_frame)
    content_font_frame.pack(fill=tk.X, pady=5)
    
    tk.Label(content_font_frame, text="內容字體大小：", font=('Arial', 12)).pack(side=tk.LEFT)
    
    btn_content_minus = tk.Button(content_font_frame, text="－", width=3, 
                                command=app._decrease_content_font)
    btn_content_minus.pack(side=tk.LEFT, padx=5)
    
    app.settings_content_font_size_label = tk.Label(content_font_frame, text=str(app.content_font_size), 
                                          width=3, relief=tk.SUNKEN, font=('Arial', 12))
    app.settings_content_font_size_label.pack(side=tk.LEFT, padx=5)
    
    btn_content_plus = tk.Button(content_font_frame, text="＋", width=3, 
                                 command=app._increase_content_font)
    btn_content_plus.pack(side=tk.LEFT, padx=5)
    
    # 分隔線
    separator2 = ttk.Separator(parent, orient='horizontal')
    separator2.pack(fill=tk.X, padx=20, pady=20)
    
    # 其他設定區域
    other_frame = tk.LabelFrame(parent, text="其他設定", padx=20, pady=20)
    other_frame.pack(fill=tk.X, padx=20, pady=10)
    
    # 自動分析設定
    app.auto_analyze_var = tk.BooleanVar(value=app.settings.get('auto_analyze', True))
    auto_analyze_check = tk.Checkbutton(other_frame, text="選擇檔案後自動開始分析", 
                                       variable=app.auto_analyze_var, 
                                       font=('Arial', 12))
    auto_analyze_check.pack(anchor=tk.W, pady=5)
    
    # 路徑記憶設定
    app.remember_path_var = tk.BooleanVar(value=app.settings.get('remember_path', True))
    remember_path_check = tk.Checkbutton(other_frame, text="記住上次選擇的路徑", 
                                        variable=app.remember_path_var, 
                                        font=('Arial', 12))
    remember_path_check.pack(anchor=tk.W, pady=5)
    
    # 分隔線
    separator3 = ttk.Separator(parent, orient='horizontal')
    separator3.pack(fill=tk.X, padx=20, pady=20)
    
    # 按鈕區域
    button_frame = tk.Frame(parent)
    button_frame.pack(fill=tk.X, padx=20, pady=20)
    
    # 保存設定按鈕
    save_btn = tk.Button(button_frame, text="保存設定", 
                        command=app._save_settings,
                        bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'))
    save_btn.pack(side=tk.RIGHT, padx=5) 