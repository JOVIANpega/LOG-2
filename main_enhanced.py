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
import webbrowser
from log_parser import LogParser
from ui_components import FontScaler, build_output_dir, get_resource_path
from ui_enhanced_fixed import EnhancedTreeview, EnhancedText, FailDetailsPanel
from enhanced_settings import build_settings_content
from enhanced_left_panel import build_left_panel
from excel_writer import ExcelWriter

class EnhancedLogAnalyzerApp:
    """增強版LOG分析器應用程式"""
    
    def __init__(self, root):
        """初始化增強版應用程式"""
        self.root = root
        # 先載入設定再設定標題
        self.settings = load_settings()
        app_title = self.settings.get('app_title', 'PEGA test log Aanlyser')
        version = self.settings.get('version', 'V1.5.6')
        self.root.title(f"{app_title} {version}")
        
        # 載入設定（其餘）
        self.ui_font_size = self.settings.get('ui_font_size', 11)
        self.content_font_size = self.settings.get('content_font_size', 11)
        
        # 設定視窗大小
        window_width = self.settings.get('window_width', 1400)
        window_height = self.settings.get('window_height', 900)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # 初始化模組
        self.font_scaler = FontScaler(root, default_size=self.ui_font_size)
        self.log_parser = LogParser()
        self.excel_writer = ExcelWriter()
        
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
        """建立增強版左側面板（抽離至模組）"""
        build_left_panel(self, parent)
    
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
        pass_columns = ("測項名稱", "指令", "收到指令", "PASS/FAIL")
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
        fail_columns = ("測項名稱", "指令", "錯誤回應", "Retry次數", "FAIL原因")
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
        
        # 自動顯示FAIL錯誤原因（不需要點擊）
        self.root.after(1000, self._auto_display_fail_reason)
    
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
        """建立設定內容（抽離至模組）"""
        build_settings_content(self, parent)
    
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
            # 先清除現有結果，避免誤導
            self._clear_enhanced_results()
            
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
        
        # 先讓使用者看到所有內容物（僅視覺，實際只處理 .log）
        folder_path = filedialog.askdirectory(
            title="選擇Log資料夾",
            initialdir=default_dir
        )
        if folder_path:
            # 先清除現有結果，避免誤導
            self._clear_enhanced_results()
            
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
        
        # 自動切換到相關Tab
        if fail_items:
            self.notebook.select(self.tab_fail)
        else:
            self.notebook.select(self.tab_pass)
    
    def _analyze_enhanced_multiple_files(self):
        """分析多個檔案（增強版）"""
        # 逐檔案解析，按照檔名是否含 PASS 分類
        folder = self.current_log_path
        # 顯示將被處理的 .log 檔清單預覽
        try:
            self._show_log_file_preview(folder)
        except Exception:
            pass
        pass_logs = []
        fail_logs = []
        total_files = 0
        for root, dirs, files in os.walk(folder):
            for fn in files:
                if not fn.lower().endswith('.log'):
                    continue
                total_files += 1
                path = os.path.join(root, fn)
                res = self.log_parser.parse_log_file(path)
                # 擷取必要資訊供 Excel 與 Summary Tab 使用
                entry = {
                    'file_path': path,
                    'file_name': os.path.basename(path),
                    'raw_lines': res.get('raw_lines') or [],
                    'ui_annotations': res.get('ui_annotations') or [],
                    'pass_items': res.get('pass_items') or [],
                    'fail_items': res.get('fail_items') or [],
                    'summary': self._extract_file_summary(res, path),
                    'step_marks': self._build_step_marks(res.get('raw_lines') or [])
                }
                if 'PASS' in fn.upper():
                    pass_logs.append(entry)
                else:
                    # 記錄第一個 FAIL 原因到 summary
                    if res.get('fail_items'):
                        entry['summary']['FAIL原因'] = res['fail_items'][0].get('error', '')
                    fail_logs.append(entry)
        # 將 pass/fail 測項分別展示於 PASS/FAIL 標籤頁（聚合）
        for idx, entry in enumerate(pass_logs, 1):
            for j, item in enumerate(entry['pass_items'], 1):
                self.pass_tree_enhanced.insert_pass_item(
                    (item['step_name'], item['command'], item['response'], item['result']),
                    step_number=j,
                    full_response=item.get('full_response', ''),
                    has_retry=item.get('has_retry_but_pass', False)
                )
        for entry in fail_logs:
            for item in entry['fail_items']:
                self.fail_tree_enhanced.insert_fail_item(
                    (item['step_name'], item['command'], item['response'], item['retry'], item['error']),
                    full_response=item.get('full_response', ''),
                    is_main_fail=item.get('is_main_fail', False)
                )
        # 匯出 Excel：PASS匯總/FAIL匯總，放同資料夾
        try:
            # 在 LOG 目錄下建立 LOG集總整理 子目錄
            out_dir = build_output_dir(folder, 'LOG集總整理')
            pass_path, fail_path = self.excel_writer.export_pass_fail_workbooks(out_dir, pass_logs, fail_logs)
            # 清空 PASS/FAIL 顯示內容（多檔案只產報表，不保留清單）
            self.pass_tree_enhanced.clear()
            self.fail_tree_enhanced.clear()
            # 完成提示 + 開啟資料夾（黑底紅字）
            self._show_open_folder_prompt(out_dir, total_files, len(pass_logs), len(fail_logs), pass_path, fail_path)
        except Exception as e:
            messagebox.showerror("匯出失敗", f"產生Excel時發生錯誤：\n{e}")
        # 自動切到匯總報表（取消）
        # self.notebook.select(self.tab_summary)


    def _extract_file_summary(self, parse_result: dict, file_path: str) -> dict:
        """從檔名或檔案內容提取測試日期時間、SFIS狀態、測試總時間、主要FAIL原因（若有）"""
        name = os.path.basename(file_path)
        # 從檔名猜測日期時間（yyyyMMddHHmmss）
        import re
        dt = ''
        m = re.search(r'(20\d{12})', name)
        if m:
            s = m.group(1)
            try:
                dt = f"{s[0:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:{s[12:14]}"
            except Exception:
                dt = ''
        # SFIS 狀態：簡單從內容找 ON/OFF 關鍵詞
        raw_lines = parse_result.get('raw_lines') or []
        sfis = ''
        for line in raw_lines[:200]:  # 前200行掃描
            if 'SFIS' in line.upper():
                if 'ON' in line.upper():
                    sfis = 'ON'
                    break
                if 'OFF' in line.upper():
                    sfis = 'OFF'
                    break
        # 測試總時間：從最後 200 行抓取 pattern 例如 "TestTime: 00:05:32" 或 "Total time: 12.3s"
        total_time = ''
        for line in (raw_lines[-200:] if raw_lines else []):
            if 'TestTime' in line or 'Total time' in line or '總時間' in line:
                total_time = line.strip()
                break
        return {
            '測試日期時間': dt,
            'SFIS': sfis,
            '測試總時間': total_time,
        }

    def _build_step_marks(self, raw_lines: list) -> dict:
        """建立步驟起始行的標號對照，key 為 raw_lines 索引，value 為 1..n"""
        marks = {}
        import re
        step_re = re.compile(r'Do\s+@STEP\d+@')
        count = 0
        for idx, line in enumerate(raw_lines):
            if step_re.search(line):
                count += 1
                marks[idx] = count
        return marks
    
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
        """自動選擇第一個FAIL項目並顯示FAIL原因"""
        try:
            if hasattr(self, 'fail_tree_enhanced'):
                children = self.fail_tree_enhanced.tree.get_children()
                if children:
                    first_item = children[0]
                    self.fail_tree_enhanced.tree.selection_set(first_item)
                    # 自動觸發選擇事件，顯示FAIL原因
                    self._on_fail_item_select(None)
        except Exception as e:
            print(f"自動選擇第一個FAIL項目失敗: {e}")
    
    def _auto_display_fail_reason(self):
        """自動顯示FAIL錯誤原因（不需要點擊）"""
        try:
            if hasattr(self, 'fail_tree_enhanced') and self.fail_tree_enhanced.tree:
                items = self.fail_tree_enhanced.tree.get_children()
                if items:
                    # 自動選擇第一個項目並顯示錯誤原因
                    first_item = items[0]
                    self.fail_tree_enhanced.tree.selection_set(first_item)
                    self.fail_tree_enhanced.tree.see(first_item)
                    
                    # 直接顯示錯誤原因，不需要點擊
                    self._display_fail_reason_for_item(first_item)
        except Exception as e:
            print(f"自動顯示FAIL錯誤原因失敗: {e}")
    
    def _display_fail_reason_for_item(self, item_id):
        """為指定項目顯示FAIL錯誤原因"""
        try:
            values = self.fail_tree_enhanced.tree.item(item_id, 'values')
            
            if values:
                step_name = values[0]
                error_code = values[4] if len(values) > 4 else "未知錯誤"
                
                # 從存儲中獲取完整內容
                full_content = self.fail_tree_enhanced.full_content_storage.get(item_id, '')
                
                # 提取主要的FAIL原因作為大字體標題
                main_error = self._extract_main_fail_reason(full_content)
                
                # 顯示大字體紅色文字白底
                self.fail_error_title.config(text=main_error, 
                                            font=('Arial', 20, 'bold'), fg='red', bg='white')
                
                # 提取FAIL原因部分顯示在下方
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
            print(f"顯示FAIL錯誤原因失敗: {e}")
    
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
                    
                    # 從存儲中獲取完整內容，優先找到包含 "is Fail" 的行作為標題
                    full_content = self.fail_tree_enhanced.full_content_storage.get(item_id, '')
                    
                    # 優先從完整內容中找到包含 "is Fail" 的行作為大字體標題
                    main_error = self._extract_main_fail_reason(full_content)
                    
                    # 顯示大字體紅色文字白底
                    self.fail_error_title.config(text=main_error, 
                                                font=('Arial', 20, 'bold'), fg='red', bg='white')
                    
                    # 提取FAIL原因部分顯示在下方
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
        """提取FAIL原因部分，優先提取包含 'is Fail' 的行"""
        if not full_content:
            return "沒有詳細錯誤內容可顯示"
        
        lines = full_content.split('\n')
        fail_reason_lines = []
        is_fail_lines = []
        
        # 優先找到包含 "is Fail" 的行
        for line in lines:
            # 移除行號前綴（如 "370. "）
            clean_line = line
            if '. ' in line and line.split('. ', 1)[0].strip().isdigit():
                clean_line = line.split('. ', 1)[1]
            
            # 優先提取包含 "is Fail" 的行
            if "is Fail" in clean_line:
                is_fail_lines.append(clean_line)
            # 其他包含重要錯誤資訊的行
            elif any(keyword in clean_line for keyword in [
                'Result:', 'validation:', 'type of', 'TestTime:', 
                'ErrorCode:', 'Test Completed', 'Test Aborted', 'TotalCount:', 
                'Report name:', 'Execute Phase', 'FAIL', 'ERROR', 'NACK'
            ]):
                fail_reason_lines.append(clean_line)
        
        # 優先顯示包含 "is Fail" 的行，然後是其他錯誤資訊
        result_lines = is_fail_lines + fail_reason_lines
        return '\n'.join(result_lines) if result_lines else full_content
    
    def _extract_main_fail_reason(self, full_content):
        """提取主要的FAIL原因作為大字體標題"""
        if not full_content:
            return "無詳細錯誤資訊"
        
        lines = full_content.split('\n')
        
        # 優先找到包含 "is Fail" 的行
        for line in lines:
            # 移除行號前綴（如 "370. "）
            clean_line = line
            if '. ' in line and line.split('. ', 1)[0].strip().isdigit():
                clean_line = line.split('. ', 1)[1]
            
            # 找到包含 "is Fail" 的行
            if "is Fail" in clean_line:
                # 處理類似 "VSCH026-043:Chec Frimware version is Fail ! <ErrorCode: BSFR18>" 的格式
                if ':' in clean_line and "is Fail" in clean_line:
                    # 擷取冒號後的部分
                    after_colon = clean_line.split(":", 1)[1].strip()
                    # 找到 "is Fail" 的位置
                    if "is Fail" in after_colon:
                        fail_pos = after_colon.find("is Fail")
                        # 擷取到 "is Fail" 結束的部分，去掉後面的 <ErrorCode: xxx> 和時間戳記
                        test_name_with_fail = after_colon[:fail_pos + 7].strip()  # 7 = len("is Fail")
                        
                        # 移除時間戳記（如 "2025/08/07 08:53:36 [1]" 格式）
                        if '[' in test_name_with_fail and ']' in test_name_with_fail:
                            bracket_start = test_name_with_fail.find('[')
                            bracket_end = test_name_with_fail.find(']')
                            if bracket_start != -1 and bracket_end != -1:
                                # 檢查括號前是否有時間戳記格式
                                before_bracket = test_name_with_fail[:bracket_start].strip()
                                if '/' in before_bracket and ':' in before_bracket:
                                    # 移除時間戳記部分
                                    test_name_with_fail = test_name_with_fail[bracket_end + 1:].strip()
                        
                        return test_name_with_fail
                elif "is Fail" in clean_line:
                    # 如果沒有冒號但有 "is Fail"，直接擷取到 "is Fail" 結束
                    fail_pos = clean_line.find("is Fail")
                    if fail_pos != -1:
                        # 找到 <ErrorCode: 的位置
                        error_code_pos = clean_line.find("<ErrorCode:")
                        if error_code_pos != -1:
                            return clean_line[:error_code_pos].strip()
                        else:
                            return clean_line[:fail_pos + 7].strip()
        
        # 如果沒有找到 "is Fail"，嘗試找到其他錯誤資訊
        for line in lines:
            clean_line = line
            if '. ' in line and line.split('. ', 1)[0].strip().isdigit():
                clean_line = line.split('. ', 1)[1]
            
            # 尋找包含 "All Test Aborted" 的行
            if "All Test Aborted" in clean_line:
                return clean_line
        
        return "未知錯誤"
    
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
    
    def _apply_font_size(self):
        """套用字體大小"""
        # 更新介面文字大小
        self.font_scaler.set_font_size(self.ui_font_size)
        
        # 更新左側面板中的字體大小標籤
        if hasattr(self, 'ui_font_size_label'):
            self.ui_font_size_label.config(text=str(self.ui_font_size), font=('Arial', self.ui_font_size))
        
        if hasattr(self, 'content_font_size_label'):
            self.content_font_size_label.config(text=str(self.content_font_size), font=('Arial', self.content_font_size))
        # 檔案名稱顯示應跟隨內容字體大小
        if hasattr(self, 'file_info_label'):
            try:
                self.file_info_label.configure(font=('Arial', self.content_font_size))
            except Exception:
                pass
        
        # 更新設定標籤頁中的字體大小標籤
        if hasattr(self, 'settings_ui_font_size_label'):
            self.settings_ui_font_size_label.config(text=str(self.ui_font_size), font=('Arial', self.ui_font_size))
        
        if hasattr(self, 'settings_content_font_size_label'):
            self.settings_content_font_size_label.config(text=str(self.content_font_size), font=('Arial', self.content_font_size))
        
        # 更新設定頁面中所有元件的字體大小
        self._apply_settings_page_fonts()
        
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
        
        # 更新匯總 Summary Tree 字體
        if hasattr(self, 'pass_summary_tree'):
            style = ttk.Style()
            style.configure('Treeview', font=('Arial', self.content_font_size))
            style.configure('Treeview.Heading', font=('Arial', self.content_font_size, 'bold'))
        
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

    def _apply_settings_page_fonts(self):
        """更新設定頁面中所有元件的字體大小"""
        try:
            if not hasattr(self, 'settings_frame'):
                return
                
            # 遞迴更新所有元件的字體
            def update_widget_font(widget):
                """遞迴更新元件的字體大小"""
                try:
                    # 根據元件的標識符更新字體
                    if hasattr(widget, '_is_settings_title'):
                        # 設定頁面標題（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size + 4, 'bold'))
                    elif hasattr(widget, '_is_settings_label'):
                        # 設定標籤（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif hasattr(widget, '_is_settings_button'):
                        # 設定按鈕（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif hasattr(widget, '_is_settings_checkbutton'):
                        # 設定核取方塊（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif hasattr(widget, '_is_settings_entry'):
                        # 設定輸入框（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif hasattr(widget, '_is_info_label'):
                        # 說明文字（內容字體控制）
                        widget.config(font=('Arial', self.content_font_size))
                    elif hasattr(widget, '_is_font_size_label'):
                        # 字體大小標籤（保持原樣，不更新）
                        pass
                    elif isinstance(widget, tk.LabelFrame):
                        # LabelFrame 標題（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif isinstance(widget, tk.Label) and not hasattr(widget, '_is_font_size_label') and not hasattr(widget, '_is_info_label'):
                        # 一般標籤（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif isinstance(widget, tk.Button):
                        # 一般按鈕（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif isinstance(widget, tk.Checkbutton):
                        # 一般核取方塊（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif isinstance(widget, tk.Entry):
                        # 一般輸入框（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    
                    # 遞迴處理子元件
                    for child in widget.winfo_children():
                        update_widget_font(child)
                        
                except Exception as e:
                    print(f"更新元件字體時發生錯誤: {e}")
            
            # 從根元件開始遞迴更新
            update_widget_font(self.settings_frame)
            
        except Exception as e:
            print(f"更新設定頁面字體時發生錯誤: {e}")
    
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
        if hasattr(self, 'gui_header_var'):
            self.settings['gui_header'] = self.gui_header_var.get().strip() or 'ONLY FOR CENTIMANIA LOG'
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
        """儲存設定並即時顯示（顯示確認視窗）"""
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
        
        # 保存標題
        if hasattr(self, 'app_title_var'):
            self.settings['app_title'] = self.app_title_var.get().strip() or 'PEGA test log Aanlyser'
        if hasattr(self, 'gui_header_var'):
            self.settings['gui_header'] = self.gui_header_var.get().strip() or 'ONLY FOR CENTIMANIA LOG'
        # 保存版本號碼
        if hasattr(self, 'version_var'):
            self.settings['version'] = self.version_var.get().strip() or 'V1.5.6'
        
        save_settings(self.settings)
        
        # 立即套用所有設定變更
        try:
            # 套用標題和版本號碼
            app_title = self.settings['app_title']
            version = self.settings.get('version', 'V1.5.6')
            self.root.title(f"{app_title} {version}")
            
            # 套用左側標題
            if hasattr(self, 'left_title_label'):
                self.left_title_label.config(text=self.settings['gui_header'])
            
            # 套用字體大小到所有元件
            self._apply_font_size()
            
            # 套用左側面板寬度
            if hasattr(self, 'paned_window') and 'pane_width' in self.settings:
                target_width = self.settings['pane_width']
                current_width = self.paned_window.sashpos(0)
                if abs(current_width - target_width) > 5:  # 如果差異超過5px才調整
                    self.paned_window.sashpos(0, target_width)
                    if hasattr(self, 'pane_width_label'):
                        self.pane_width_label.config(text=f"{target_width}px")
            
            # 更新設定頁面的字體大小標籤
            if hasattr(self, 'settings_ui_font_size_label'):
                self.settings_ui_font_size_label.config(text=str(self.ui_font_size))
            if hasattr(self, 'settings_content_font_size_label'):
                self.settings_content_font_size_label.config(text=str(self.content_font_size))
                
        except Exception as e:
            print(f"套用設定時發生錯誤: {e}")
            
        messagebox.showinfo("設定保存", "所有設定已成功保存並立即生效！")

    def _clear_enhanced_results(self):
        """清除增強版分析結果（供左側按鈕呼叫）"""
        try:
            self.pass_tree_enhanced.clear()
            self.fail_tree_enhanced.clear()
            self.log_text_enhanced.clear()
            if hasattr(self, 'pass_summary_tree'):
                self.pass_summary_tree.delete(*self.pass_summary_tree.get_children())
            if hasattr(self, 'fail_summary_tree'):
                self.fail_summary_tree.delete(*self.fail_summary_tree.get_children())
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
        except Exception:
            pass

    def _open_markdown_help(self):
        """開啟並顯示 dioc/README.md 或 QUICK_START.md 內容"""
        try:
            md_path = get_resource_path(os.path.join('dioc', 'README.md'))
            content = ''
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                alt_path = get_resource_path(os.path.join('dioc', 'QUICK_START.md'))
                with open(alt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            self._show_text_viewer_window("README 說明", content)
        except Exception as e:
            try:
                messagebox.showerror("錯誤", f"無法讀取說明：{e}")
            except Exception:
                pass

    def _open_html_help(self):
        """以系統預設瀏覽器開啟操作說明 HTML（docs/USER_GUIDE.html）"""
        try:
            html_path = get_resource_path(os.path.join('docs', 'USER_GUIDE.html'))
            if not os.path.exists(html_path):
                # 後備使用 README
                return self._open_markdown_help()
            webbrowser.open(f"file:///{html_path}")
        except Exception as e:
            try:
                messagebox.showerror("錯誤", f"無法開啟操作說明：{e}")
            except Exception:
                pass

    def _show_text_viewer_window(self, title: str, content: str):
        """顯示純文字視窗（使用內容字體大小）"""
        win = tk.Toplevel(self.root)
        win.title(title)
        # 設定最小和最大尺寸
        win.minsize(600, 400)
        win.maxsize(1200, 900)
        win.geometry("800x600")
        
        # 讓視窗居中顯示
        win.transient(self.root)
        win.grab_set()
        win.update_idletasks()
        
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
        
        # 自動調整視窗大小以適應內容
        self._auto_resize_text_window(win, text)

    # === UI 字體調整 ===
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

    # === 左側面板寬度調整 ===
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



    def _auto_resize_text_window(self, win, text_widget):
        """根據文字內容自動調整文字視窗大小，確保導航按鈕始終可見"""
        try:
            # 獲取文字內容的行數和最大行寬度
            content = text_widget.get('1.0', tk.END)
            lines = content.split('\n')
            max_line_length = max(len(line) for line in lines) if lines else 0
            total_lines = len(lines)
            
            # 計算合適的視窗尺寸
            # 每行大約需要 8-10 像素寬度，每行大約需要 16-18 像素高度
            char_width = 8  # 每個字符的寬度
            char_height = 16  # 每行的高度
            
            # 計算文字區域的寬度和高度（更緊湊的計算）
            text_width = min(max_line_length * char_width + 80, 800)   # 減少邊距，最大800
            text_height = min(total_lines * char_height + 150, 600)    # 減少邊距，最大600
            
            # 設定視窗大小（更緊湊）
            window_width = max(600, text_width + 40)   # 減少額外寬度
            window_height = max(400, text_height + 80)  # 減少額外高度，確保導航按鈕可見
            
            # 限制最大尺寸（更嚴格，避免視窗過大）
            window_width = min(window_width, 900)   # 從1200減少到900
            window_height = min(window_height, 700)  # 從900減少到700
            
            # 更新視窗大小
            win.geometry(f"{window_width}x{window_height}")
            
            # 重新居中視窗
            win.update_idletasks()
            x = (win.winfo_screenwidth() // 2) - (window_width // 2)
            y = (win.winfo_screenheight() // 2) - (window_height // 2)
            win.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
        except Exception as e:
            print(f"自動調整文字視窗大小失敗: {e}")

    def _show_open_folder_prompt(self, out_dir: str, total_files: int, pass_count: int, fail_count: int, pass_path: str, fail_path: str):
        """白底視窗，僅問題段落以黃底黑字反白"""
        win = tk.Toplevel(self.root)
        win.title("匯出完成")
        win.geometry("700x300")
        
        # 讓視窗居中顯示
        win.transient(self.root)
        win.grab_set()
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (700 // 2)
        y = (win.winfo_screenheight() // 2) - (300 // 2)
        win.geometry(f"700x300+{x}+{y}")
        
        try:
            win.configure(bg='white')
        except Exception:
            pass
        info = (
            f"匯出完成 / 共 {total_files} 個檔案\n\n"
            f"PASS: {pass_count}\nFAIL: {fail_count}\n\n"
            f"已產生：\n{pass_path}\n{fail_path}\n"
        )
        lbl_info = tk.Label(win, text=info, bg='white', fg='black', font=('Microsoft JhengHei', 11))
        lbl_info.pack(fill=tk.BOTH, expand=1, padx=16, pady=(16, 6))
        lbl_ask = tk.Label(win, text="是否要開啟輸出資料夾？", bg='#FFF176', fg='black', font=('Microsoft JhengHei', 11, 'bold'))
        lbl_ask.pack(fill=tk.X, padx=16, pady=(0, 8))
        btns = tk.Frame(win, bg='white')
        btns.pack(pady=8)
        def on_yes():
            try:
                os.startfile(out_dir)
            except Exception:
                pass
            win.destroy()
        def on_no():
            win.destroy()
        yes = tk.Button(btns, text="開啟資料夾", command=on_yes)
        no = tk.Button(btns, text="關閉", command=on_no)
        yes.pack(side=tk.LEFT, padx=10)
        no.pack(side=tk.LEFT, padx=10)


def main_enhanced():
    """增強版主程式"""
    root = tk.Tk()
    app = EnhancedLogAnalyzerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main_enhanced() 