#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器GUI應用程式 - 增強版
提供現代化的圖形使用者介面來分析測試log檔案
支援雙字體控制、視窗大小記憶、預覽視窗等功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import json
from settings_loader import load_settings, save_settings
from log_parser import LogParser
from ui_components import FontScaler
from ui_enhanced_fixed import EnhancedTreeview, EnhancedText, FailDetailsPanel

class EnhancedLogAnalyzerApp:
    """增強版LOG分析器應用程式"""
    
    def __init__(self, root):
        """初始化增強版應用程式"""
        self.root = root
        self.root.title("測試Log分析器 - 增強版")
        
        # 載入設定
        self.settings = load_settings()
        self.ui_font_size = self.settings.get('ui_font_size', 11)
        self.content_font_size = self.settings.get('content_font_size', 11)
        
        # 設定視窗大小
        window_width = self.settings.get('window_width', 1400)
        window_height = self.settings.get('window_height', 900)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # 初始化模組
        self.font_scaler = FontScaler(root, default_size=self.ui_font_size)
        self.log_parser = LogParser()
        
        # 狀態變數
        self.current_mode = 'single'
        self.current_log_path = ''
        
        # 建立UI
        self._build_enhanced_ui()
        self._apply_font_size()
        
        # 綁定視窗關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _on_closing(self):
        """處理視窗關閉事件"""
        try:
            # 保存視窗大小
            self.settings['window_width'] = self.root.winfo_width()
            self.settings['window_height'] = self.root.winfo_height()
            
            # 保存左側面板寬度
            if hasattr(self, 'left_frame'):
                left_width = self.left_frame.winfo_width()
                if left_width > 0:  # 確保寬度有效
                    self.settings['pane_width'] = left_width
            
            # 保存字體設定
            self.settings['ui_font_size'] = self.ui_font_size
            self.settings['content_font_size'] = self.content_font_size
            
            # 保存其他設定
            if hasattr(self, 'auto_analyze_var'):
                self.settings['auto_analyze'] = self.auto_analyze_var.get()
            if hasattr(self, 'remember_path_var'):
                self.settings['remember_path'] = self.remember_path_var.get()
            
            save_settings(self.settings)
            print("設定已保存")
        except Exception as e:
            print(f"保存設定失敗: {e}")
        
        self.root.destroy()
    
    def _build_enhanced_ui(self):
        """建立增強版UI"""
        # 主要分割視窗
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned.pack(fill=tk.BOTH, expand=1)
        
        # 左側控制面板
        pane_width = self.settings.get('pane_width', 250)
        self.left_frame = tk.Frame(self.paned, width=pane_width)
        self._build_enhanced_left_panel(self.left_frame)
        self.paned.add(self.left_frame, minsize=200)
        
        # 右側結果顯示區域
        self.right_frame = tk.Frame(self.paned)
        self._build_enhanced_right_panel(self.right_frame)
        self.paned.add(self.right_frame, minsize=800)
        
        # 綁定分割視窗調整事件
        self.paned.bind('<ButtonRelease-1>', self._on_pane_adjust)
        self.paned.bind('<B1-Motion>', self._on_pane_adjust)  # 拖動時也保存
        
        # 設定初始面板寬度（使用after確保UI已建立）
        self.root.after(100, lambda: self._set_initial_pane_width(pane_width))
    
    def _set_initial_pane_width(self, width):
        """設定初始面板寬度"""
        try:
            if hasattr(self, 'paned') and hasattr(self, 'left_frame'):
                # 使用configure方法設定寬度
                self.left_frame.configure(width=width)
                # 強制更新
                self.paned.update_idletasks()
        except Exception as e:
            print(f"設定初始面板寬度失敗: {e}")
    
    def _on_pane_adjust(self, event):
        """處理分割視窗調整事件"""
        try:
            # 獲取左側面板的當前寬度
            if hasattr(self, 'left_frame'):
                left_width = self.left_frame.winfo_width()
                if left_width > 0:  # 確保寬度有效
                    self.settings['pane_width'] = left_width
                    # 更新設定標籤頁中的顯示
                    if hasattr(self, 'pane_width_label'):
                        self.pane_width_label.config(text=f"{left_width}px")
                    # 立即保存設定
                    save_settings(self.settings)
        except Exception as e:
            print(f"保存面板寬度失敗: {e}")
    
    def _build_enhanced_left_panel(self, parent):
        """建立增強版左側面板"""
        # 標題 - 使用大方塊淺藍色背景
        title_frame = tk.Frame(parent, bg='#E6F3FF', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 20))
        
        title_label = tk.Label(title_frame, text="測試LOG分析器", 
                              font=('Arial', 26, 'bold'), fg='#2E86AB', bg='#E6F3FF')
        title_label.pack(pady=10)
        self.font_scaler.register(title_label)
        
        # 檔案選擇區域
        file_frame = tk.LabelFrame(parent, text="檔案選擇", padx=10, pady=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 單一檔案選擇
        btn_single = tk.Button(file_frame, text="📁 選擇單一檔案", 
                              command=self._select_file, bg='#4CAF50', fg='white')
        btn_single.pack(fill=tk.X, pady=2)
        self.font_scaler.register(btn_single)
        
        # 資料夾選擇
        btn_folder = tk.Button(file_frame, text="📂 選擇資料夾", 
                              command=self._select_folder, bg='#2196F3', fg='white')
        btn_folder.pack(fill=tk.X, pady=2)
        self.font_scaler.register(btn_folder)
        
        # 清除結果按鈕
        btn_clear = tk.Button(file_frame, text="🗑️ 清除結果", 
                             command=self._clear_enhanced_results, bg='#F44336', fg='white')
        btn_clear.pack(fill=tk.X, pady=2)
        self.font_scaler.register(btn_clear)
        
        # 左三個按鈕：加粗與hover
        try:
            from ui_components import make_bold, apply_button_hover
            make_bold(btn_single)
            make_bold(btn_folder)
            make_bold(btn_clear)
            # 針對彩色底按鈕，hover 時略微變亮
            apply_button_hover(btn_single, hover_bg="#66BB6A", hover_fg='white', normal_bg='#4CAF50', normal_fg='white')
            apply_button_hover(btn_folder, hover_bg="#64B5F6", hover_fg='white', normal_bg='#2196F3', normal_fg='white')
            apply_button_hover(btn_clear,  hover_bg="#EF5350", hover_fg='white', normal_bg='#F44336', normal_fg='white')
        except Exception:
            pass
        
        # 說明文件按鈕
        help_btn = tk.Button(parent, text="📖 查看說明(README)", command=self._open_markdown_help, bg="#607D8B", fg="white")
        help_btn.pack(fill=tk.X, padx=10, pady=(8, 8))
        self.font_scaler.register(help_btn)
        try:
            make_bold(help_btn)
            apply_button_hover(help_btn, hover_bg="#78909C", hover_fg='white', normal_bg='#607D8B', normal_fg='white')
        except Exception:
            pass
        
        # 顯示選擇的檔案
        self.file_info_label = tk.Label(file_frame, text="未選擇檔案", 
                                       fg='#666', wraplength=200)
        self.file_info_label.pack(pady=(5, 0))
        self.font_scaler.register(self.file_info_label)
        
        # 如果有上次選擇的路徑，顯示出來
        if self.settings.get('last_log_path') and os.path.exists(self.settings.get('last_log_path')):
            filename = os.path.basename(self.settings.get('last_log_path'))
            self.file_info_label.config(text=f"上次選擇：{filename}", fg='#666')
        elif self.settings.get('last_folder_path') and os.path.exists(self.settings.get('last_folder_path')):
            foldername = os.path.basename(self.settings.get('last_folder_path'))
            self.file_info_label.config(text=f"上次選擇資料夾：{foldername}", fg='#666')
        
        # 移除開始分析按鈕 - 改為自動分析
        
        # 字體控制
        font_frame = tk.LabelFrame(parent, text="介面設定", padx=10, pady=10)
        font_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 介面文字大小控制
        ui_font_frame = tk.Frame(font_frame)
        ui_font_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(ui_font_frame, text="介面文字：").pack(side=tk.LEFT)
        
        btn_ui_minus = tk.Button(ui_font_frame, text="－", width=3, 
                                command=self._decrease_ui_font)
        btn_ui_minus.pack(side=tk.LEFT, padx=2)
        self.font_scaler.register(btn_ui_minus)
        
        self.ui_font_size_label = tk.Label(ui_font_frame, text=str(self.ui_font_size), 
                                          width=3, relief=tk.SUNKEN, font=('Arial', self.ui_font_size))
        self.ui_font_size_label.pack(side=tk.LEFT, padx=2)
        
        btn_ui_plus = tk.Button(ui_font_frame, text="＋", width=3, 
                              command=self._increase_ui_font)
        btn_ui_plus.pack(side=tk.LEFT, padx=2)
        self.font_scaler.register(btn_ui_plus)
        
        # 內容字體大小控制
        content_font_frame = tk.Frame(font_frame)
        content_font_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(content_font_frame, text="內容字體：").pack(side=tk.LEFT)
        
        btn_content_minus = tk.Button(content_font_frame, text="－", width=3, 
                                    command=self._decrease_content_font)
        btn_content_minus.pack(side=tk.LEFT, padx=2)
        self.font_scaler.register(btn_content_minus)
        
        self.content_font_size_label = tk.Label(content_font_frame, text=str(self.content_font_size), 
                                              width=3, relief=tk.SUNKEN, font=('Arial', self.content_font_size))
        self.content_font_size_label.pack(side=tk.LEFT, padx=2)
        
        btn_content_plus = tk.Button(content_font_frame, text="＋", width=3, 
                                     command=self._increase_content_font)
        btn_content_plus.pack(side=tk.LEFT, padx=2)
        self.font_scaler.register(btn_content_plus)
    
    def _build_enhanced_right_panel(self, parent):
        """建立增強版右側面板"""
        # 建立標籤頁
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=1)
        
        # 設定標籤頁樣式
        self._setup_tab_styles()
        
        # 建立各標籤頁
        self._build_enhanced_pass_tab()
        self._build_enhanced_fail_tab()
        self._build_enhanced_log_tab()
        self._build_enhanced_settings_tab()
    
    def _setup_tab_styles(self):
        """設定標籤頁樣式"""
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Arial', self.ui_font_size))
        # 鼠標靠近標籤頁時顯示綠色背景，黑色文字
        style.map('TNotebook.Tab', background=[('active', '#00FF00')], foreground=[('active', 'black')])
    
    def _build_enhanced_pass_tab(self):
        """建立PASS標籤頁"""
        self.tab_pass = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pass, text="✅ PASS測項")
        
        # 使用增強型TreeView
        pass_columns = ("Step Name", "指令", "回應", "結果")
        self.pass_tree_enhanced = EnhancedTreeview(self.tab_pass, pass_columns)
        self.pass_tree_enhanced.pack_with_scrollbars(fill=tk.BOTH, expand=1)
    
    def _build_enhanced_fail_tab(self):
        """建立FAIL標籤頁 - 分割成上下兩個視窗"""
        self.tab_fail = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_fail, text="❌ FAIL測項")
        
        # 創建上下分割視窗
        self.fail_paned = tk.PanedWindow(self.tab_fail, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        self.fail_paned.pack(fill=tk.BOTH, expand=1)
        
        # 上半部 - FAIL測項列表
        self.fail_upper_frame = tk.Frame(self.fail_paned)
        fail_columns = ("Step Name", "指令", "錯誤回應", "Retry次數", "錯誤原因")
        self.fail_tree_enhanced = EnhancedTreeview(self.fail_upper_frame, fail_columns)
        self.fail_tree_enhanced.pack_with_scrollbars(fill=tk.BOTH, expand=1)
        self.fail_paned.add(self.fail_upper_frame, minsize=200)
        
        # 下半部 - FAIL錯誤詳細資訊
        self.fail_lower_frame = tk.Frame(self.fail_paned, bg='white')
        
        # 錯誤標題
        self.fail_error_title = tk.Label(self.fail_lower_frame, text="選擇FAIL項目查看詳細錯誤", 
                                        font=('Arial', 16, 'bold'), fg='red', bg='white')
        self.fail_error_title.pack(pady=10)
        
        # 錯誤內容文字框
        error_text_frame = tk.Frame(self.fail_lower_frame)
        error_text_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)
        
        self.fail_error_text = tk.Text(error_text_frame, wrap=tk.WORD, 
                                      bg='white', fg='black', font=('Consolas', 12))
        self.fail_error_text.grid(row=0, column=0, sticky='nsew')
        
        # 滾動條
        error_scrollbar = tk.Scrollbar(error_text_frame, command=self.fail_error_text.yview)
        error_scrollbar.grid(row=0, column=1, sticky='ns')
        self.fail_error_text.config(yscrollcommand=error_scrollbar.set)
        
        error_text_frame.grid_rowconfigure(0, weight=1)
        error_text_frame.grid_columnconfigure(0, weight=1)
        
        self.fail_paned.add(self.fail_lower_frame, minsize=150)
        
        # 載入FAIL分割視窗設定
        fail_pane_position = self.settings.get('fail_pane_position', 300)
        self.root.after(100, lambda: self._set_fail_pane_position(fail_pane_position))
        
        # 綁定分割視窗調整事件
        self.fail_paned.bind('<ButtonRelease-1>', self._on_fail_pane_adjust)
        
        # 綁定選擇事件
        self.fail_tree_enhanced.tree.bind('<<TreeviewSelect>>', self._on_fail_item_select)
        
        # 自動顯示第一個FAIL項目（如果有的話）
        self.root.after(500, self._auto_select_first_fail)
    
    
    def _set_fail_pane_position(self, position):
        """設定FAIL分割視窗位置"""
        try:
            if hasattr(self, 'fail_paned'):
                self.fail_paned.sash_place(0, 0, position)
        except Exception as e:
            print(f"設定FAIL分割視窗位置失敗: {e}")
    
    def _on_fail_pane_adjust(self, event):
        """處理FAIL分割視窗調整事件"""
        try:
            if hasattr(self, 'fail_paned'):
                position = self.fail_paned.sash_coord(0)[1]
                self.settings['fail_pane_position'] = position
                save_settings(self.settings)
        except Exception as e:
            print(f"保存FAIL分割視窗位置失敗: {e}")
    
    def _auto_select_first_fail(self):
        """自動選擇第一個FAIL項目並顯示錯誤原因"""
        try:
            if hasattr(self, 'fail_tree_enhanced'):
                children = self.fail_tree_enhanced.tree.get_children()
                if children:
                    first_item = children[0]
                    self.fail_tree_enhanced.tree.selection_set(first_item)
                    # 自動觸發選擇事件，顯示錯誤原因
                    self._on_fail_item_select(None)
        except Exception as e:
            print(f"自動選擇第一個FAIL項目失敗: {e}")
    
    def _on_fail_item_select(self, event):
        """處理FAIL項目選擇事件"""
        try:
            selection = self.fail_tree_enhanced.tree.selection()
            if selection:
                item_id = selection[0]
                values = self.fail_tree_enhanced.tree.item(item_id, 'values')
                
                if values:
                    step_name = values[0]
                    error_code = values[4] if len(values) > 4 else "未知錯誤"
                    
                    # 更新標題 - 主題用大字體紅色文字白底
                    # 從錯誤原因中擷取測試名稱部分
                    # 例如：VSCH026-043:Chec Frimware version is Fail ! <ErrorCode: BSFR18>
                    # 要顯示：Chec Frimware version is Fail
                    main_error = error_code
                    if ":" in error_code and "is Fail" in error_code:
                        # 擷取冒號後的部分
                        after_colon = error_code.split(":", 1)[1].strip()
                        # 找到 "is Fail" 的位置
                        if "is Fail" in after_colon:
                            fail_pos = after_colon.find("is Fail")
                            # 擷取到 "is Fail" 結束的部分，去掉後面的 <ErrorCode: xxx>
                            test_name_with_fail = after_colon[:fail_pos + 7].strip()  # 7 = len("is Fail")
                            main_error = test_name_with_fail
                    
                    # 顯示大字體紅色文字白底
                    self.fail_error_title.config(text=main_error, 
                                                font=('Arial', 20, 'bold'), fg='red', bg='white')
                    
                    # 從存儲中獲取完整內容，只顯示FAIL原因部分
                    full_content = self.fail_tree_enhanced.full_content_storage.get(item_id, '')
                    fail_reason_content = self._extract_fail_reason(full_content)
                    
                    # 更新錯誤內容
                    self.fail_error_text.config(state=tk.NORMAL)
                    self.fail_error_text.delete('1.0', tk.END)
                    self._insert_formatted_fail_content(fail_reason_content)
                    self.fail_error_text.config(state=tk.NORMAL)
                else:
                    self.fail_error_title.config(text="無詳細錯誤資訊")
                    self.fail_error_text.config(state=tk.NORMAL)
                    self.fail_error_text.delete('1.0', tk.END)
                    self.fail_error_text.insert('1.0', "沒有詳細錯誤內容可顯示")
                    self.fail_error_text.config(state=tk.NORMAL)
        except Exception as e:
            print(f"處理FAIL項目選擇失敗: {e}")
    
    def _extract_fail_reason(self, full_content):
        """提取FAIL原因部分，不是全部錯誤字串"""
        if not full_content:
            return "沒有詳細錯誤內容可顯示"
        
        lines = full_content.split('\n')
        fail_reason_lines = []
        
        # 找到包含關鍵錯誤資訊的行
        for line in lines:
            # 移除行號前綴（如 "370. "）
            clean_line = line
            if '. ' in line and line.split('. ', 1)[0].strip().isdigit():
                clean_line = line.split('. ', 1)[1]
            
            # 包含重要錯誤資訊的行
            if any(keyword in clean_line for keyword in [
                'Result:', 'validation:', 'type of', 'TestTime:', 'is Fail', 
                'ErrorCode:', 'Test Completed', 'Test Aborted', 'TotalCount:', 
                'Report name:', 'Execute Phase', 'FAIL', 'ERROR', 'NACK'
            ]):
                fail_reason_lines.append(clean_line)
        
        return '\n'.join(fail_reason_lines) if fail_reason_lines else full_content
    
    def _insert_formatted_fail_content(self, content):
        """插入格式化的FAIL內容，特定行顯示紅色"""
        lines = content.split('\n')
        for line in lines:
            # 檢查是否包含 "is Fail" 的行，顯示紅色
            if "is Fail" in line:
                self.fail_error_text.insert(tk.END, line + '\n', 'fail_red')
            else:
                self.fail_error_text.insert(tk.END, line + '\n')
        
        # 設定紅色文字標籤
        self.fail_error_text.tag_configure('fail_red', foreground='red', font=('Consolas', 12, 'bold'))
    
    def _build_enhanced_log_tab(self):
        """建立原始LOG標籤頁"""
        self.tab_log = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_log, text="📄 原始LOG")
        
        # 使用增強型文字元件
        self.log_text_enhanced = EnhancedText(self.tab_log)
        self.log_text_enhanced.pack(fill=tk.BOTH, expand=1)
    
    def _build_enhanced_settings_tab(self):
        """建立設定標籤頁"""
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="⚙️ 設定")
        
        # 建立滾動框架
        canvas = tk.Canvas(self.tab_settings)
        scrollbar = ttk.Scrollbar(self.tab_settings, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 設定區域
        self._build_settings_content(scrollable_frame)
        
        # 打包滾動元件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 綁定滾動事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _build_settings_content(self, parent):
        """建立設定內容"""
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
        current_pane_width = self.settings.get('pane_width', 250)
        
        # 減少按鈕
        btn_pane_minus = tk.Button(pane_frame, text="－", width=3, 
                                  command=self._decrease_pane_width)
        btn_pane_minus.pack(side=tk.LEFT, padx=5)
        
        # 顯示當前寬度
        self.pane_width_label = tk.Label(pane_frame, text=f"{current_pane_width}px", 
                                        width=8, relief=tk.SUNKEN, font=('Arial', 12))
        self.pane_width_label.pack(side=tk.LEFT, padx=5)
        
        # 增加按鈕
        btn_pane_plus = tk.Button(pane_frame, text="＋", width=3, 
                                 command=self._increase_pane_width)
        btn_pane_plus.pack(side=tk.LEFT, padx=5)
        
        # 重置按鈕
        btn_pane_reset = tk.Button(pane_frame, text="重置", 
                                  command=self._reset_pane_width)
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
                                command=self._decrease_ui_font)
        btn_ui_minus.pack(side=tk.LEFT, padx=5)
        
        self.settings_ui_font_size_label = tk.Label(ui_font_frame, text=str(self.ui_font_size), 
                                          width=3, relief=tk.SUNKEN, font=('Arial', 12))
        self.settings_ui_font_size_label.pack(side=tk.LEFT, padx=5)
        
        btn_ui_plus = tk.Button(ui_font_frame, text="＋", width=3, 
                              command=self._increase_ui_font)
        btn_ui_plus.pack(side=tk.LEFT, padx=5)
        
        # 內容字體大小控制
        content_font_frame = tk.Frame(font_frame)
        content_font_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(content_font_frame, text="內容字體大小：", font=('Arial', 12)).pack(side=tk.LEFT)
        
        btn_content_minus = tk.Button(content_font_frame, text="－", width=3, 
                                    command=self._decrease_content_font)
        btn_content_minus.pack(side=tk.LEFT, padx=5)
        
        self.settings_content_font_size_label = tk.Label(content_font_frame, text=str(self.content_font_size), 
                                              width=3, relief=tk.SUNKEN, font=('Arial', 12))
        self.settings_content_font_size_label.pack(side=tk.LEFT, padx=5)
        
        btn_content_plus = tk.Button(content_font_frame, text="＋", width=3, 
                                     command=self._increase_content_font)
        btn_content_plus.pack(side=tk.LEFT, padx=5)
        
        # 分隔線
        separator2 = ttk.Separator(parent, orient='horizontal')
        separator2.pack(fill=tk.X, padx=20, pady=20)
        
        # 其他設定區域
        other_frame = tk.LabelFrame(parent, text="其他設定", padx=20, pady=20)
        other_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 自動分析設定
        self.auto_analyze_var = tk.BooleanVar(value=self.settings.get('auto_analyze', True))
        auto_analyze_check = tk.Checkbutton(other_frame, text="選擇檔案後自動開始分析", 
                                           variable=self.auto_analyze_var, 
                                           font=('Arial', 12))
        auto_analyze_check.pack(anchor=tk.W, pady=5)
        
        # 路徑記憶設定
        self.remember_path_var = tk.BooleanVar(value=self.settings.get('remember_path', True))
        remember_path_check = tk.Checkbutton(other_frame, text="記住上次選擇的路徑", 
                                            variable=self.remember_path_var, 
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
                            command=self._save_settings,
                            bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'))
        save_btn.pack(side=tk.RIGHT, padx=5)
    
    def _get_default_directory(self):
        """獲取預設目錄 - EXE或PY檔案所在目錄"""
        try:
            # 如果是EXE檔案，使用sys.executable
            if getattr(sys, 'frozen', False):
                # 打包成EXE的情況
                default_dir = os.path.dirname(sys.executable)
            else:
                # 直接執行PY檔案的情況
                default_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 如果目錄不存在，使用當前工作目錄
            if not os.path.exists(default_dir):
                default_dir = os.getcwd()
            
            return default_dir
        except Exception:
            # 如果出現任何錯誤，使用當前工作目錄
            return os.getcwd()
    
    def _select_file(self):
        """選擇單一檔案"""
        # 優先使用上次選擇的路徑，如果沒有則使用預設路徑
        if self.settings.get('last_log_path') and os.path.exists(self.settings.get('last_log_path')):
            default_dir = os.path.dirname(self.settings.get('last_log_path'))
        else:
            default_dir = self._get_default_directory()
        
        file_path = filedialog.askopenfilename(
            title="選擇Log檔案", 
            filetypes=[("Log檔案", "*.log"), ("所有檔案", "*.*")],
            initialdir=default_dir
        )
        if file_path:
            self.current_mode = 'single'
            self.current_log_path = file_path
            filename = os.path.basename(file_path)
            self.file_info_label.config(text=f"已選擇：{filename}", fg='green')
            
            # 儲存選擇的路徑到設定
            self.settings['last_log_path'] = file_path
            self._save_settings_silent()
            
            # 自動開始分析（enhanced）
            self._analyze_enhanced_log()
    
    def _select_folder(self):
        """選擇資料夾"""
        # 優先使用上次選擇的路徑，如果沒有則使用預設路徑
        if self.settings.get('last_folder_path') and os.path.exists(self.settings.get('last_folder_path')):
            default_dir = self.settings.get('last_folder_path')
        else:
            default_dir = self._get_default_directory()
        
        folder_path = filedialog.askdirectory(
            title="選擇Log資料夾",
            initialdir=default_dir
        )
        if folder_path:
            self.current_mode = 'multi'
            self.current_log_path = folder_path
            
            foldername = os.path.basename(folder_path)
            self.file_info_label.config(text=f"已選擇資料夾：{foldername}", fg='blue')
            
            # 儲存選擇的路徑到設定
            self.settings['last_folder_path'] = folder_path
            self._save_settings_silent()
            
            # 自動開始分析（enhanced）
            self._analyze_enhanced_log()
    
    def _analyze_enhanced_log(self):
        """分析log檔案並更新增強版GUI顯示"""
        if not self.current_log_path:
            messagebox.showwarning("警告", "請先選擇log檔案或資料夾")
            return
            
        # 清空現有內容
        self.pass_tree_enhanced.clear()
        self.fail_tree_enhanced.clear()
        self.log_text_enhanced.clear()
        
        try:
            if self.current_mode == 'single':
                self._analyze_enhanced_single_file()
            else:
                self._analyze_enhanced_multiple_files()
                
        except Exception as e:
            messagebox.showerror("分析錯誤", f"分析過程中發生錯誤：\n{str(e)}")
    
    def _analyze_enhanced_single_file(self):
        """分析單一檔案（增強版）"""
        result = self.log_parser.parse_log_file(self.current_log_path)
        pass_items = result['pass_items']
        fail_items = result['fail_items']
        raw_lines = result['raw_lines']
        last_fail = result['last_fail']
        fail_line_idx = result['fail_line_idx']
        
        # Tab1: PASS - 顯示所有通過的測項
        for idx, item in enumerate(pass_items, 1):
            full_response = item.get('full_response', '')
            has_retry = item.get('has_retry_but_pass', False)  # 使用 has_retry_but_pass 屬性
            self.pass_tree_enhanced.insert_pass_item(
                (item['step_name'], item['command'], item['response'], item['result']),
                step_number=idx,
                full_response=full_response,
                has_retry=has_retry
            )
        
        # Tab2: FAIL - 顯示所有FAIL區塊
        for idx, item in enumerate(fail_items):
            is_main_fail = item.get('is_main_fail', False)
            full_response = item.get('full_response', '')
            self.fail_tree_enhanced.insert_fail_item(
                (item['step_name'], item['command'], item['response'], item['retry'], item['error']),
                full_response=full_response,
                is_main_fail=is_main_fail
            )
        
        # Tab3: 原始LOG，標紅錯誤行並自動跳轉
        if raw_lines:
            # 將raw_lines轉換為字符串
            log_content = '\n'.join(raw_lines)
            self.log_text_enhanced.insert_log_with_highlighting(log_content, {
                'fail_line_idx': fail_line_idx,
                'pass_items': pass_items,
                'fail_items': fail_items
            })
            
            # 如果有錯誤行，跳轉到錯誤位置
            if fail_line_idx is not None and fail_line_idx < len(raw_lines):
                self.log_text_enhanced.highlight_error_block(fail_line_idx + 1, fail_line_idx + 1)
                self.log_text_enhanced.text.see(f"{fail_line_idx + 1}.0")
        
        # 單一檔案模式禁用Excel匯出
        # self.export_btn.config(state=tk.DISABLED) # 移除此行
        
        # 自動切換到相關Tab
        if fail_items:
            self.notebook.select(self.tab_fail)
        else:
            self.notebook.select(self.tab_pass)
    
    def _analyze_enhanced_multiple_files(self):
        """分析多個檔案（增強版）"""
        result = self.log_parser.parse_log_folder(self.current_log_path)
        pass_items = result['pass_items']
        fail_items = result['fail_items']
        
        # Tab1: PASS - 顯示所有通過的測項
        for idx, item in enumerate(pass_items, 1):
            full_response = item.get('full_response', '')
            has_retry = item.get('has_retry_but_pass', False)  # 使用 has_retry_but_pass 屬性
            self.pass_tree_enhanced.insert_pass_item(
                (item['step_name'], item['command'], item['response'], item['result']),
                step_number=idx,
                full_response=full_response,
                has_retry=has_retry
            )
        
        # Tab2: FAIL - 顯示所有失敗的測項
        for item in fail_items:
            full_response = item.get('full_response', '')
            self.fail_tree_enhanced.insert_fail_item(
                (item['step_name'], item['command'], item['response'], item['retry'], item['error']),
                full_response=full_response,
                is_main_fail=False
            )
        
        # Tab3: 清空原始LOG（多檔案模式不顯示原始內容）
        self.log_text_enhanced.clear()
        self.log_text_enhanced.text.insert(tk.END, "多檔案分析模式：請查看PASS/FAIL分頁檢視結果")
        
        # 多檔案模式啟用Excel匯出
        # self.export_btn.config(state=tk.NORMAL if (pass_items or fail_items) else tk.DISABLED) # 移除此行
        
        # 自動切換到PASS分頁
        self.notebook.select(self.tab_pass)
    
    def _clear_enhanced_results(self):
        """清除增強版分析結果"""
        self.pass_tree_enhanced.clear()
        self.fail_tree_enhanced.clear()
        self.log_text_enhanced.clear()
        # 清除FAIL錯誤顯示區域
        if hasattr(self, 'fail_error_title'):
            self.fail_error_title.config(text="選擇FAIL項目查看詳細錯誤")
        if hasattr(self, 'fail_error_text'):
            self.fail_error_text.config(state=tk.NORMAL)
            self.fail_error_text.delete('1.0', tk.END)
            self.fail_error_text.config(state=tk.NORMAL)
        self.file_info_label.config(text="未選擇檔案", fg='#666')
        self.current_log_path = ''
        self.current_mode = 'single'
    
    def _increase_ui_font(self):
        """增加介面文字字體大小"""
        if self.ui_font_size < 15:
            self.ui_font_size += 1
            self._apply_font_size()
            self._save_settings_silent()
    
    def _decrease_ui_font(self):
        """減少介面文字字體大小"""
        if self.ui_font_size > 10:
            self.ui_font_size -= 1
            self._apply_font_size()
            self._save_settings_silent()
    
    def _increase_content_font(self):
        """增加內容字體大小"""
        if self.content_font_size < 15:
            self.content_font_size += 1
            self._apply_font_size()
            self._save_settings_silent()
    
    def _decrease_content_font(self):
        """減少內容字體大小"""
        if self.content_font_size > 10:
            self.content_font_size -= 1
            self._apply_font_size()
            self._save_settings_silent()
    
    def _apply_font_size(self):
        """套用字體大小"""
        # 更新介面文字大小
        self.font_scaler.set_font_size(self.ui_font_size)
        
        # 更新左側面板中的字體大小標籤
        if hasattr(self, 'ui_font_size_label'):
            self.ui_font_size_label.config(text=str(self.ui_font_size), font=('Arial', self.ui_font_size))
        
        if hasattr(self, 'content_font_size_label'):
            self.content_font_size_label.config(text=str(self.content_font_size), font=('Arial', self.content_font_size))
        
        # 更新設定標籤頁中的字體大小標籤
        if hasattr(self, 'settings_ui_font_size_label'):
            self.settings_ui_font_size_label.config(text=str(self.ui_font_size), font=('Arial', self.ui_font_size))
        
        if hasattr(self, 'settings_content_font_size_label'):
            self.settings_content_font_size_label.config(text=str(self.content_font_size), font=('Arial', self.content_font_size))
        
        # 更新標籤頁名稱字體（介面文字控制）
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Arial', self.ui_font_size))
        # 重新設定標籤頁懸停效果
        style.map('TNotebook.Tab', background=[('active', '#00FF00')], foreground=[('active', 'black')])
        
        # 更新增強型元件的內容字體（內容字體控制）
        if hasattr(self, 'log_text_enhanced'):
            self.log_text_enhanced.text.configure(font=('Consolas', self.content_font_size))
        
        # 更新TreeView內容字體（內容字體控制）
        if hasattr(self, 'pass_tree_enhanced'):
            self._apply_treeview_font(self.pass_tree_enhanced.tree)
        if hasattr(self, 'fail_tree_enhanced'):
            self._apply_treeview_font(self.fail_tree_enhanced.tree)
        
        # 更新錯誤詳情面板內容字體
        if hasattr(self, 'fail_details'):
            self.fail_details.error_text.configure(font=('Consolas', self.content_font_size))
        
        # 更新FAIL錯誤顯示區域字體
        if hasattr(self, 'fail_error_text'):
            self.fail_error_text.configure(font=('Consolas', self.content_font_size))
        if hasattr(self, 'fail_error_title'):
            self.fail_error_title.configure(font=('Arial', self.ui_font_size + 4, 'bold'))
        
        # 更新TreeView展開視窗的內容字體
        if hasattr(self, 'pass_tree_enhanced'):
            try:
                self.pass_tree_enhanced.set_font_size(self.content_font_size)
            except Exception:
                pass
        if hasattr(self, 'fail_tree_enhanced'):
            try:
                self.fail_tree_enhanced.set_font_size(self.content_font_size)
            except Exception:
                pass
    
    def _apply_treeview_font(self, treeview):
        """套用TreeView字體"""
        # 同步展開視窗內容字體
        if hasattr(self, 'pass_tree_enhanced'):
            try:
                self.pass_tree_enhanced.set_font_size(self.content_font_size)
            except Exception:
                pass
        if hasattr(self, 'fail_tree_enhanced'):
            try:
                self.fail_tree_enhanced.set_font_size(self.content_font_size)
            except Exception:
                pass
    
    def _save_settings_silent(self):
        """無聲儲存設定（不顯示確認視窗）"""
        self.settings['ui_font_size'] = self.ui_font_size
        self.settings['content_font_size'] = self.content_font_size
        # 保存面板寬度
        if hasattr(self, 'left_frame'):
            left_width = self.left_frame.winfo_width()
            if left_width > 0:
                self.settings['pane_width'] = left_width
        # 保存視窗大小
        self.settings['window_width'] = self.root.winfo_width()
        self.settings['window_height'] = self.root.winfo_height()
        
        save_settings(self.settings)
    
    def _save_settings(self):
        """儲存設定（顯示確認視窗）"""
        self.settings['ui_font_size'] = self.ui_font_size
        self.settings['content_font_size'] = self.content_font_size
        # 保存面板寬度
        if hasattr(self, 'left_frame'):
            left_width = self.left_frame.winfo_width()
            if left_width > 0:
                self.settings['pane_width'] = left_width
        # 保存視窗大小
        self.settings['window_width'] = self.root.winfo_width()
        self.settings['window_height'] = self.root.winfo_height()
        # 保存其他設定
        if hasattr(self, 'auto_analyze_var'):
            self.settings['auto_analyze'] = self.auto_analyze_var.get()
        if hasattr(self, 'remember_path_var'):
            self.settings['remember_path'] = self.remember_path_var.get()
        
        save_settings(self.settings)
        messagebox.showinfo("設定保存", "設定已成功保存！")
    

    
    def _decrease_pane_width(self):
        """減少左側面板寬度"""
        current_width = self.settings.get('pane_width', 250)
        if current_width > 100:  # 至少保留一個最小寬度
            new_width = current_width - 10
            self.settings['pane_width'] = new_width
            if hasattr(self, 'pane_width_label'):
                self.pane_width_label.config(text=f"{new_width}px")
            # 更新分割視窗的面板寬度
            if hasattr(self, 'left_frame'):
                self.left_frame.configure(width=new_width)
                self.paned.update_idletasks()
            save_settings(self.settings)
    
    def _increase_pane_width(self):
        """增加左側面板寬度"""
        current_width = self.settings.get('pane_width', 250)
        if current_width < 500:  # 最大寬度限制
            new_width = current_width + 10
            self.settings['pane_width'] = new_width
            if hasattr(self, 'pane_width_label'):
                self.pane_width_label.config(text=f"{new_width}px")
            # 更新分割視窗的面板寬度
            if hasattr(self, 'left_frame'):
                self.left_frame.configure(width=new_width)
                self.paned.update_idletasks()
            save_settings(self.settings)
    
    def _reset_pane_width(self):
        """重置左側面板寬度為預設值"""
        default_width = 250
        self.settings['pane_width'] = default_width
        if hasattr(self, 'pane_width_label'):
            self.pane_width_label.config(text=f"{default_width}px")
        # 更新分割視窗的面板寬度
        if hasattr(self, 'left_frame'):
            self.left_frame.configure(width=default_width)
            self.paned.update_idletasks()
        save_settings(self.settings)

    def _open_markdown_help(self):
        """開啟並顯示 docs/README.md 內容（使用內容字體大小）"""
        try:
            from ui_components import get_resource_path
            md_path = get_resource_path(os.path.join('docs', 'README.md'))
            content = ''
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                # 若 README.md 不存在，嘗試 QUICK_START.md
                alt_path = get_resource_path(os.path.join('docs', 'QUICK_START.md'))
                with open(alt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            self._show_text_viewer_window("README 說明", content)
        except Exception as e:
            try:
                messagebox.showerror("錯誤", f"無法讀取說明：{e}")
            except Exception:
                pass

    def _show_text_viewer_window(self, title: str, content: str):
        """顯示純文字的查看視窗（簡易Markdown檢視），字體使用內容字體大小"""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("1000x750")
        frame = tk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=1)
        text = tk.Text(frame, wrap=tk.WORD, font=('Consolas', self.content_font_size))
        vs = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        hs = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text.xview)
        text.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        text.grid(row=0, column=0, sticky='nsew')
        vs.grid(row=0, column=1, sticky='ns')
        hs.grid(row=1, column=0, sticky='ew')
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        text.insert('1.0', content)
        text.config(state=tk.NORMAL)

def main_enhanced():
    """增強版主程式"""
    root = tk.Tk()
    app = EnhancedLogAnalyzerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main_enhanced() 