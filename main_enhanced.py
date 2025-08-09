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
        self.root.title(self.settings.get('app_title', 'PEGA test log Aanlyser'))
        
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
            # 移除行號前綴（如 "370. ")
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
        
        # 保存標題
        if hasattr(self, 'app_title_var'):
            self.settings['app_title'] = self.app_title_var.get().strip() or 'PEGA test log Aanlyser'
        save_settings(self.settings)
        # 立即套用標題
        try:
            self.root.title(self.settings['app_title'])
        except Exception:
            pass
        messagebox.showinfo("設定保存", "設定已成功保存！")

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
        """開啟並顯示 docs/README.md 或 QUICK_START.md 內容"""
        try:
            md_path = get_resource_path(os.path.join('docs', 'README.md'))
            content = ''
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
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
        """顯示純文字視窗（使用內容字體大小）"""
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

    def _show_open_folder_prompt(self, out_dir: str, total_files: int, pass_count: int, fail_count: int, pass_path: str, fail_path: str):
        """白底視窗，僅問題段落以黃底黑字反白"""
        win = tk.Toplevel(self.root)
        win.title("匯出完成")
        win.geometry("700x300")
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