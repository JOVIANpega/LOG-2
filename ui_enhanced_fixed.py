# ui_enhanced.py
# 用途：提供進階的GUI元件，包含顏色標籤、hover效果、文字格式化等
import tkinter as tk
from tkinter import ttk
import re

class EnhancedTreeview:
    """增強型TreeView，支援顏色標籤和hover效果"""
    
    def __init__(self, parent, columns, show='headings'):
        self.tree = ttk.Treeview(parent, columns=columns, show=show)
        self.full_content_storage = {}  # 用字典存儲完整內容
        self.all_items_data = []  # 存儲所有測試項的資料
        self.font_size = 11
        self._hover_popup = None
        self._hover_row = None
        self.setup_styles()
        self.setup_hover_effects()
        self.setup_scrollbars(parent)
    
    def setup_styles(self):
        """設定樣式"""
        self.style = ttk.Style()
        
        # PASS項目樣式（黑色）
        self.style.configure("Pass.Treeview", foreground="black", font=('Arial', self.font_size))
        self.style.configure("Pass.Treeview.Item", foreground="black", font=('Arial', self.font_size))
        
        # FAIL項目樣式（紅色）
        self.style.configure("Fail.Treeview", foreground="red", font=('Arial', self.font_size))
        self.style.configure("Fail.Treeview.Item", foreground="red", font=('Arial', self.font_size))
        
        # Hover效果樣式
        self.style.configure("Hover.Treeview.Item", background="#E8F4FD")
        
        # 一般TreeView樣式
        self.style.configure("Treeview", font=('Arial', self.font_size))
        self.style.configure("Treeview.Heading", font=('Arial', self.font_size, 'bold'))
    
    def setup_hover_effects(self):
        """設定hover效果"""
        self.tree.bind('<Motion>', self._on_hover)
        self.tree.bind('<Leave>', self._on_leave)
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Control-c>', self._on_copy)  # 支援Ctrl+C複製
        self.current_hover_item = None
    
    def setup_scrollbars(self, parent):
        """設定滾動條"""
        # 垂直滾動條
        self.v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.v_scrollbar.set)
        
        # 水平滾動條
        self.h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.h_scrollbar.set)
    
    def pack_with_scrollbars(self, **kwargs):
        """打包TreeView和滾動條"""
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 從kwargs中提取pack參數，避免衝突
        pack_kwargs = {}
        for key, value in kwargs.items():
            if key in ['fill', 'expand', 'side', 'padx', 'pady', 'ipadx', 'ipady', 'anchor']:
                pack_kwargs[key] = value
        
        # 設定預設值
        if 'fill' not in pack_kwargs:
            pack_kwargs['fill'] = tk.BOTH
        if 'expand' not in pack_kwargs:
            pack_kwargs['expand'] = 1
            
        # 直接使用pack_kwargs，不傳遞kwargs
        self.tree.pack(**pack_kwargs)
    
    def _on_hover(self, event):
        """滑鼠懸停效果"""
        item = self.tree.identify_row(event.y)
        if item != self.current_hover_item:
            if self.current_hover_item:
                # 取消舊的hover標籤
                tags = list(self.tree.item(self.current_hover_item, 'tags'))
                if 'hover' in tags:
                    tags.remove('hover')
                self.tree.item(self.current_hover_item, tags=tuple(tags))
            if item:
                tags = list(self.tree.item(item, 'tags'))
                if 'hover' not in tags:
                    tags.append('hover')
                self.tree.item(item, tags=tuple(tags))
                self.current_hover_item = item
        # 額外：顯示懸停浮窗（整列只要有保存內容即可顯示）
        self._maybe_show_hover_popup(event)
    
    def _on_leave(self, event):
        """滑鼠離開效果"""
        if self.current_hover_item:
            self.tree.item(self.current_hover_item, tags=())
            self.current_hover_item = None
        self._hover_row = None
        self._hide_hover_popup()
    
    def _on_double_click(self, event):
        """雙擊展開詳細內容"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            # 從字典中獲取完整內容
            full_content = self.full_content_storage.get(item)
            if full_content:
                self._show_detail_dialog(full_content, current_item_id=item)
            else:
                print("沒有找到詳細內容")

    def set_font_size(self, size: int):
        """設定展開視窗字體大小"""
        try:
            sz = int(size)
        except Exception:
            sz = 11
        self.font_size = max(10, min(15, sz))
        
        # 更新TreeView內容字體大小
        self.style.configure("Treeview", font=('Arial', self.font_size))
        self.style.configure("Treeview.Heading", font=('Arial', self.font_size, 'bold'))
        self.style.configure("Pass.Treeview", font=('Arial', self.font_size))
        self.style.configure("Pass.Treeview.Item", font=('Arial', self.font_size))
        self.style.configure("Fail.Treeview", font=('Arial', self.font_size))
        self.style.configure("Fail.Treeview.Item", font=('Arial', self.font_size))
        
        # 更新懸停浮窗字體
        if self._hover_popup and self._hover_popup.winfo_exists():
            try:
                self._hover_text.config(font=('Consolas', self.font_size))
            except Exception:
                pass
    
    def _on_copy(self, event):
        """處理Ctrl+C複製選中項目"""
        try:
            selected_items = self.tree.selection()
            if selected_items:
                item = selected_items[0]
                values = self.tree.item(item, 'values')
                if values:
                    # 複製選中行的所有內容
                    content = '\t'.join(str(v) for v in values)
                    self._copy_to_clipboard(content)
        except Exception as e:
            print(f"複製選中項目失敗: {e}")
    
    def _maybe_show_hover_popup(self, event):
        row = self.tree.identify_row(event.y)
        if not row:
            self._hover_row = None
            self._hide_hover_popup()
            return
        content = self.full_content_storage.get(row)
        if not content:
            if self._hover_row != row:
                self._hover_row = None
                self._hide_hover_popup()
            return
        # 位置計算 - 檢查是否靠近下方
        abs_x = self.tree.winfo_rootx() + event.x + 12
        abs_y = self.tree.winfo_rooty() + event.y + 12
        
        # 檢查是否靠近螢幕下方，如果是則往上顯示
        screen_height = self.tree.winfo_screenheight()
        popup_height = 400
        if abs_y + popup_height > screen_height - 50:  # 距離底部50像素時往上顯示
            abs_y = screen_height - popup_height - 50
        
        if self._hover_row == row and self._hover_popup and self._hover_popup.winfo_exists():
            try:
                self._hover_popup.geometry(f"700x400+{abs_x}+{abs_y}")
            except Exception:
                pass
            return
        self._hover_row = row
        self._show_hover_popup("完整內容", content, abs_x, abs_y)

    def _show_hover_popup(self, title, content, x, y):
        if self._hover_popup and self._hover_popup.winfo_exists():
            try:
                self._hover_text.config(state=tk.NORMAL)
                self._hover_text.delete('1.0', tk.END)
                self._hover_text.insert('1.0', content)
                self._hover_text.config(font=('Consolas', self.font_size))
                self._hover_popup.geometry(f"700x400+{x}+{y}")
                # 重新應用語法高亮
                self._apply_syntax_highlighting(self._hover_text, content)
                return
            except Exception:
                try:
                    self._hover_popup.destroy()
                except Exception:
                    pass
                self._hover_popup = None
        # 建立新浮窗
        self._hover_popup = tk.Toplevel(self.tree)
        self._hover_popup.overrideredirect(True)
        self._hover_popup.attributes('-topmost', True)
        self._hover_popup.geometry(f"700x400+{x}+{y}")
        frame = tk.Frame(self._hover_popup, bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=1)
        text = tk.Text(frame, wrap=tk.NONE, font=('Consolas', self.font_size))
        
        # 垂直滾動條 - 做大一點，靠近文字區
        vs = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview, width=20)
        vs.grid(row=0, column=1, sticky='ns', padx=(5, 0))
        
        # 水平滾動條 - 做大一點
        hs = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text.xview, width=20)
        hs.grid(row=1, column=0, sticky='ew', pady=(5, 0))
        
        text.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        text.grid(row=0, column=0, sticky='nsew')
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        text.insert('1.0', content)
        text.config(state=tk.NORMAL)
        # 應用語法高亮
        self._apply_syntax_highlighting(text, content)
        self._hover_popup.bind('<Leave>', lambda e: self._hide_hover_popup())
        self._hover_text = text

    def _hide_hover_popup(self):
        if self._hover_popup and self._hover_popup.winfo_exists():
            try:
                self._hover_popup.destroy()
            except Exception:
                pass
        self._hover_popup = None
        self._hover_row = None

    def insert_pass_item(self, values, step_number, full_response="", has_retry=False):
        """插入PASS項目"""
        # 在Step Name前加上編號
        enhanced_values = list(values)
        step_name = f"{step_number}. {enhanced_values[0]}"
        
        # 只有當真正有RETRY時才添加標記，但用黑色文字
        if has_retry:
            step_name += " [RETRY但PASS]"
        
        enhanced_values[0] = step_name
        enhanced_values[2] = enhanced_values[2] + " [+點擊詳細]"
        
        item_id = self.tree.insert('', 'end', values=enhanced_values)
        
        # 設定標籤和顏色 - PASS項目文字全部為黑色，包括RETRY
        command_value = str(enhanced_values[1]) if len(enhanced_values) > 1 else ""
        
        # 檢查是否有"未找到指令"，如果有則確保顯示為黑色
        if "未找到指令" in command_value:
            # "未找到指令"的情況顯示為黑色
            self.tree.item(item_id, tags=('pass_normal',))
            self.tree.tag_configure('pass_normal', foreground='black')
        elif has_retry:
            # RETRY項目也顯示為黑色（不再是紅色）
            self.tree.item(item_id, tags=('pass_retry',))
            self.tree.tag_configure('pass_retry', foreground='black')
        else:
            # 正常PASS項目顯示為黑色
            self.tree.item(item_id, tags=('pass',))
            self.tree.tag_configure('pass', foreground='black')
        
        # 儲存完整回應內容到字典中
        if full_response:
            self.full_content_storage[item_id] = full_response
        
        # 存儲測試項資料到 all_items_data 中
        item_data = {
            'item_id': item_id,
            'step_name': step_name,
            'command': command_value,
            'response': enhanced_values[2] if len(enhanced_values) > 2 else "",
            'result': enhanced_values[3] if len(enhanced_values) > 3 else "",
            'full_response': full_response,
            'has_retry': has_retry,
            'type': 'pass'
        }
        self.all_items_data.append(item_data)
        
        return item_id
    
    def insert_fail_item(self, values, full_response="", is_main_fail=True):
        """插入FAIL項目"""
        # 處理錯誤回應內容
        enhanced_values = list(values)
        enhanced_values[2] = enhanced_values[2] + " [+點擊詳細]"
        
        item_id = self.tree.insert('', 'end', values=enhanced_values)
        
        # 設定標籤和顏色 - 預設全部為黑色，只有真正的錯誤才顯示紅色
        command_value = str(enhanced_values[1]) if len(enhanced_values) > 1 else ""
        error_value = str(enhanced_values[4]) if len(enhanced_values) > 4 else ""
        
        # 檢查是否為真正的錯誤（有具體錯誤訊息且不是"未找到指令"）
        is_real_error = False
        
        # 排除"未找到指令"的情況
        if "未找到指令" not in command_value:
            # 檢查是否有具體的錯誤訊息
            if error_value and error_value != "未知錯誤" and error_value != "無錯誤":
                # 檢查是否包含錯誤關鍵字
                error_keywords = ['FAIL', 'ERROR', 'NACK', 'TIMEOUT', '失敗', '錯誤', '超時', '異常']
                if any(keyword in error_value.upper() for keyword in error_keywords):
                    is_real_error = True
        
        if is_real_error:
            # 真正的錯誤項目顯示紅色
            self.tree.item(item_id, tags=('fail_main_red',))
            self.tree.tag_configure('fail_main_red', foreground='red', font=('Arial', 10, 'bold'))
        else:
            # 其他FAIL項目顯示黑色（包括"未找到指令"）
            self.tree.item(item_id, tags=('fail_main_black',))
            self.tree.tag_configure('fail_main_black', foreground='black', font=('Arial', 10, 'bold'))
        
        # 儲存完整回應內容到字典中
        if full_response:
            self.full_content_storage[item_id] = full_response
        
        # 存儲測試項資料到 all_items_data 中
        item_data = {
            'item_id': item_id,
            'step_name': enhanced_values[0],
            'command': command_value,
            'response': enhanced_values[2] if len(enhanced_values) > 2 else "",
            'result': enhanced_values[3] if len(enhanced_values) > 3 else "",
            'error': error_value,
            'full_response': full_response,
            'is_main_fail': is_main_fail,
            'type': 'fail'
        }
        self.all_items_data.append(item_data)
        
        return item_id
    
    def clear(self):
        """清空內容"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.full_content_storage.clear()  # 清空存儲字典
        self.all_items_data.clear()  # 清空所有測試項資料
    
    def _show_detail_dialog(self, content, current_item_id=None):
        """顯示詳細內容對話框（測項指令內容）"""
        try:
            detail_window = tk.Toplevel()
            detail_window.title("測項指令內容")
            detail_window.geometry("1000x700")
            
            # 標題
            title_label = tk.Label(detail_window, text="測項指令內容", 
                                  font=('Arial', 14, 'bold'), fg='#2E86AB')
            title_label.pack(pady=10)
            
            # 文字框架
            text_frame = tk.Frame(detail_window)
            text_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)
            
            # 文字框（可選取複製）
            text_widget = tk.Text(text_frame, wrap=tk.NONE, font=('Consolas', self.font_size))
            text_widget.grid(row=0, column=0, sticky='nsew')
            
            # 垂直滾動條 - 做大一點，靠近文字區
            v_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview, width=20)
            v_scrollbar.grid(row=0, column=1, sticky='ns')
            
            # 水平滾動條 - 做大一點
            h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview, width=20)
            h_scrollbar.grid(row=1, column=0, sticky='ew')
            
            # 設定框架的網格權重
            text_frame.grid_rowconfigure(0, weight=1)
            text_frame.grid_columnconfigure(0, weight=1)
            
            text_widget.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # 插入內容
            if content:
                text_widget.insert('1.0', str(content))
                # 設定語法高亮
                self._apply_syntax_highlighting(text_widget, str(content))
            else:
                text_widget.insert('1.0', "沒有詳細內容可顯示")
            
            # 允許選取但不允許編輯
            text_widget.config(state=tk.NORMAL)
            
            # 按鈕框架
            btn_frame = tk.Frame(detail_window)
            btn_frame.pack(pady=10)
            
            # 找到當前項目在 all_items_data 中的索引
            current_index = -1
            if current_item_id and self.all_items_data:
                for i, item_data in enumerate(self.all_items_data):
                    if item_data['item_id'] == current_item_id:
                        current_index = i
                        break
            
            # 上一頁按鈕
            prev_btn = tk.Button(btn_frame, text="上一頁", 
                               command=lambda: self._show_previous_item(detail_window, text_widget, current_index))
            prev_btn.pack(side=tk.LEFT, padx=5)
            
            # 下一頁按鈕
            next_btn = tk.Button(btn_frame, text="下一頁", 
                               command=lambda: self._show_next_item(detail_window, text_widget, current_index))
            next_btn.pack(side=tk.LEFT, padx=5)
            
            # 複製全部按鈕
            copy_btn = tk.Button(btn_frame, text="複製全部", 
                               command=lambda: self._copy_to_clipboard(content))
            copy_btn.pack(side=tk.LEFT, padx=5)
            
            # 關閉按鈕
            close_btn = tk.Button(btn_frame, text="關閉", command=detail_window.destroy)
            close_btn.pack(side=tk.LEFT, padx=5)
            
            # 更新按鈕狀態
            self._update_navigation_buttons(prev_btn, next_btn, current_index)
            
        except Exception as e:
            print(f"顯示詳細內容對話框失敗: {e}")
    
    def _show_previous_item(self, detail_window, text_widget, current_index):
        """顯示上一個測試項"""
        if current_index > 0 and self.all_items_data:
            prev_index = current_index - 1
            prev_item_data = self.all_items_data[prev_index]
            content = prev_item_data.get('full_response', '沒有詳細內容可顯示')
            
            # 更新文字內容
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', str(content))
            self._apply_syntax_highlighting(text_widget, str(content))
            text_widget.config(state=tk.NORMAL)
            
            # 更新標題
            detail_window.title(f"測項指令內容 - {prev_item_data['step_name']}")
            
            # 更新按鈕狀態
            self._update_navigation_buttons_in_window(detail_window, prev_index)
    
    def _show_next_item(self, detail_window, text_widget, current_index):
        """顯示下一個測試項"""
        if self.all_items_data and current_index < len(self.all_items_data) - 1:
            # 計算下一個索引
            next_index = current_index + 1
            next_item_data = self.all_items_data[next_index]
            content = next_item_data.get('full_response', '沒有詳細內容可顯示')
            
            # 更新文字內容
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', str(content))
            self._apply_syntax_highlighting(text_widget, str(content))
            text_widget.config(state=tk.NORMAL)
            
            # 更新標題
            detail_window.title(f"測項指令內容 - {next_item_data['step_name']}")
            
            # 更新按鈕狀態
            self._update_navigation_buttons_in_window(detail_window, next_index)
    
    def _update_navigation_buttons(self, prev_btn, next_btn, current_index):
        """更新導航按鈕狀態"""
        if prev_btn and next_btn:
            # 更新上一頁按鈕狀態
            if current_index <= 0:
                prev_btn.config(state=tk.DISABLED)
            else:
                prev_btn.config(state=tk.NORMAL)
            
            # 更新下一頁按鈕狀態
            if current_index >= len(self.all_items_data) - 1:
                next_btn.config(state=tk.DISABLED)
            else:
                next_btn.config(state=tk.NORMAL)
    
    def _update_navigation_buttons_in_window(self, detail_window, current_index):
        """更新視窗中的導航按鈕狀態"""
        prev_btn = None
        next_btn = None
        text_widget = None
        
        # 找到文字框和按鈕
        for widget in detail_window.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Text):
                        text_widget = child
                    elif isinstance(child, tk.Button):
                        if child.cget('text') == '上一頁':
                            prev_btn = child
                        elif child.cget('text') == '下一頁':
                            next_btn = child
        
        # 更新按鈕狀態和命令
        if prev_btn and next_btn and text_widget:
            # 更新上一頁按鈕狀態
            if current_index <= 0:
                prev_btn.config(state=tk.DISABLED)
            else:
                prev_btn.config(state=tk.NORMAL)
            
            # 更新下一頁按鈕狀態 - 允許進行到最後一個項目
            if current_index >= len(self.all_items_data) - 1:
                next_btn.config(state=tk.DISABLED)
            else:
                next_btn.config(state=tk.NORMAL)
                
            # 更新按鈕的命令，使用正確的參數和閉包
            prev_btn.config(command=lambda idx=current_index: self._show_previous_item(detail_window, text_widget, idx))
            next_btn.config(command=lambda idx=current_index: self._show_next_item(detail_window, text_widget, idx))
    
    def _apply_syntax_highlighting(self, text_widget, content):
        """對詳細內容應用語法高亮"""
        try:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line_start = f"{i+1}.0"
                line_end = f"{i+1}.end"
                
                # UART指令 - 藍色
                if '(UART) >' in line or '> ' in line:
                    text_widget.tag_add('cmd', line_start, line_end)
                    text_widget.tag_configure('cmd', foreground='blue', font=('Consolas', self.font_size, 'bold'))
                
                # UART回應 - 紫色
                elif '(UART) <' in line or '< ' in line:
                    text_widget.tag_add('resp', line_start, line_end)
                    text_widget.tag_configure('resp', foreground='purple')
                
                # 錯誤行 - 紅色
                elif any(keyword in line.upper() for keyword in ['FAIL', 'ERROR', 'NACK']):
                    text_widget.tag_add('error', line_start, line_end)
                    text_widget.tag_configure('error', foreground='red', font=('Consolas', self.font_size, 'bold'))
                
                # Step行 - 綠色
                elif 'Do @STEP' in line or '@STEP' in line:
                    text_widget.tag_add('step', line_start, line_end)
                    text_widget.tag_configure('step', foreground='green', font=('Consolas', self.font_size, 'bold'))
                
                # PASS - 綠色
                elif 'PASS' in line.upper():
                    text_widget.tag_add('pass', line_start, line_end)
                    text_widget.tag_configure('pass', foreground='green', font=('Consolas', self.font_size, 'bold'))
                
                # 其他內容 - 黑色（預設）
                else:
                    text_widget.tag_add('normal', line_start, line_end)
                    text_widget.tag_configure('normal', foreground='black')
        except Exception as e:
            print(f"語法高亮應用失敗: {e}")
    
    def _copy_to_clipboard(self, content):
        """複製內容到剪貼板"""
        try:
            import tkinter as tk
            root = tk._default_root
            root.clipboard_clear()
            root.clipboard_append(str(content))
            print("內容已複製到剪貼板")
        except Exception as e:
            print(f"複製失敗: {e}")

# 其他類別保持不變...
class EnhancedText:
    """增強型Text元件，支援語法高亮和區段標籤"""
    
    def __init__(self, parent, **kwargs):
        # 創建框架來容納Text和滾動條
        self.frame = tk.Frame(parent)
        self.text = tk.Text(self.frame, **kwargs)
        self.setup_tags()
        self.step_positions = {}  # 儲存每個step的位置
        self.setup_search_functionality()
        self.setup_scrollbars()
    
    def setup_scrollbars(self):
        """設定滾動條"""
        # 垂直滾動條
        self.v_scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.text.yview, width=20)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 水平滾動條
        self.h_scrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.text.xview, width=20)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 配置Text元件的滾動
        self.text.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def pack(self, **kwargs):
        """打包Text元件框架"""
        return self.frame.pack(**kwargs)
    
    def clear(self):
        """清空文字內容"""
        self.text.delete(1.0, tk.END)
        self.step_positions.clear()
    
    def setup_tags(self):
        """設定文字標籤樣式"""
        # Step區段背景色
        self.text.tag_configure('step_bg_1', background='#E8F4FD')  # 淺藍
        self.text.tag_configure('step_bg_2', background='#F0E8FF')  # 淺紫
        
        # PASS/FAIL文字顏色
        self.text.tag_configure('pass_text', foreground='green', font=('Arial', 10, 'bold'))
        self.text.tag_configure('fail_text', foreground='red', font=('Arial', 10, 'bold'))
        
        # 指令和回應樣式
        self.text.tag_configure('command', foreground='blue', font=('Arial', 9, 'bold'))
        self.text.tag_configure('response', foreground='purple', font=('Arial', 9))
        
        # 錯誤區塊樣式
        self.text.tag_configure('error_block', background='#FFE4E1', foreground='red')
        
        # Hover效果
        self.text.tag_configure('step_hover', background='#FFFF99')
        
        # 綁定點擊事件
        self.text.tag_bind('step_clickable', '<Button-1>', self._on_step_click)
        self.text.tag_bind('step_clickable', '<Enter>', self._on_step_hover)
        self.text.tag_bind('step_clickable', '<Leave>', self._on_step_leave)
    
    def setup_search_functionality(self):
        """設定搜尋功能"""
        self.search_frame = None
        self.search_var = tk.StringVar()
        self.search_index = '1.0'
        
        # 綁定Ctrl+F
        self.text.bind('<Control-f>', self._show_search_dialog)
        self.text.bind('<Control-F>', self._show_search_dialog)
    
    def _show_search_dialog(self, event=None):
        """顯示搜尋對話框"""
        if self.search_frame:
            self.search_frame.destroy()
        
        # 創建搜尋框架
        self.search_frame = tk.Frame(self.text.master)
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        tk.Label(self.search_frame, text="搜尋:").pack(side=tk.LEFT)
        
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.focus()
        
        tk.Button(self.search_frame, text="下一個", command=self._find_next).pack(side=tk.LEFT, padx=2)
        tk.Button(self.search_frame, text="上一個", command=self._find_prev).pack(side=tk.LEFT, padx=2)
        tk.Button(self.search_frame, text="關閉", command=self._close_search).pack(side=tk.LEFT, padx=2)
        
        # 綁定Enter鍵
        self.search_entry.bind('<Return>', lambda e: self._find_next())
        self.search_entry.bind('<Escape>', lambda e: self._close_search())
        
        return "break"
    
    def _find_next(self):
        """尋找下一個"""
        search_text = self.search_var.get()
        if not search_text:
            return
        
        # 清除之前的高亮
        self.text.tag_remove('search_highlight', '1.0', tk.END)
        
        # 從當前位置開始搜尋
        pos = self.text.search(search_text, self.search_index, tk.END)
        if pos:
            # 計算結束位置
            end_pos = f"{pos}+{len(search_text)}c"
            
            # 高亮顯示
            self.text.tag_add('search_highlight', pos, end_pos)
            self.text.tag_configure('search_highlight', background='yellow', foreground='black')
            
            # 跳轉到該位置
            self.text.see(pos)
            self.text.mark_set(tk.INSERT, pos)
            
            # 更新搜尋位置
            self.search_index = end_pos
        else:
            # 從頭開始搜尋
            self.search_index = '1.0'
            self._find_next()
    
    def _find_prev(self):
        """尋找上一個"""
        search_text = self.search_var.get()
        if not search_text:
            return
        
        # 清除之前的高亮
        self.text.tag_remove('search_highlight', '1.0', tk.END)
        
        # 從當前位置向前搜尋
        pos = self.text.search(search_text, self.search_index, '1.0', backwards=True)
        if pos:
            # 計算結束位置
            end_pos = f"{pos}+{len(search_text)}c"
            
            # 高亮顯示
            self.text.tag_add('search_highlight', pos, end_pos)
            self.text.tag_configure('search_highlight', background='yellow', foreground='black')
            
            # 跳轉到該位置
            self.text.see(pos)
            self.text.mark_set(tk.INSERT, pos)
            
            # 更新搜尋位置
            self.search_index = pos
        else:
            # 從末尾開始搜尋
            self.search_index = tk.END
            self._find_prev()
    
    def _close_search(self):
        """關閉搜尋框"""
        if self.search_frame:
            self.search_frame.destroy()
            self.search_frame = None
        
        # 清除高亮
        self.text.tag_remove('search_highlight', '1.0', tk.END)
        
        # 焦點回到文字框
        self.text.focus()
    
    def _on_step_click(self, event):
        """點擊step標籤跳轉"""
        # 獲取點擊的標籤內容
        index = self.text.index(tk.CURRENT)
        tags = self.text.tag_names(index)
        
        for tag in tags:
            if tag.startswith('step_'):
                step_name = tag.replace('step_', '').replace('_clickable', '')
                if step_name in self.step_positions:
                    self.jump_to_step(step_name)
                break
    
    def _on_step_hover(self, event):
        """step標籤hover效果"""
        index = self.text.index(tk.CURRENT)
        self.text.tag_add('step_hover', f"{index} linestart", f"{index} lineend")
        # 改變游標樣式
        self.text.config(cursor='hand2')
    
    def _on_step_leave(self, event):
        """移除hover效果"""
        self.text.tag_remove('step_hover', '1.0', tk.END)
        # 恢復游標樣式
        self.text.config(cursor='xterm')
    
    def insert_log_with_highlighting(self, log_content, test_results):
        """插入log內容並進行語法高亮"""
        self.text.delete('1.0', tk.END)
        self.step_positions.clear()
        
        lines = log_content.split('\n')
        current_step = None
        step_counter = 0
        bg_toggle = True
        
        for i, line in enumerate(lines):
            line_start = self.text.index(tk.INSERT)
            
            # 檢查是否為新的step
            step_match = re.search(r'Do @STEP\d+@([^@\n]+)', line)
            if step_match:
                current_step = step_match.group(1).strip()
                step_counter += 1
                bg_toggle = not bg_toggle
                
                # 記錄step位置
                self.step_positions[current_step] = line_start
                
                # 插入可點擊的step標籤
                self.text.insert(tk.INSERT, line + '\n')
                line_end = self.text.index(tk.INSERT)
                
                # 設定背景色
                bg_tag = 'step_bg_1' if bg_toggle else 'step_bg_2'
                self.text.tag_add(bg_tag, line_start, line_end)
                
                # 設定可點擊標籤
                step_tag = f"step_{current_step}_clickable"
                self.text.tag_add(step_tag, line_start, line_end)
                self.text.tag_add('step_clickable', line_start, line_end)
                
                continue
            
            # 檢查指令行
            if '>' in line:
                self.text.insert(tk.INSERT, line + '\n')
                line_end = self.text.index(tk.INSERT)
                self.text.tag_add('command', line_start, line_end)
                continue
            
            # 檢查回應行
            if '<' in line:
                self.text.insert(tk.INSERT, line + '\n')
                line_end = self.text.index(tk.INSERT)
                self.text.tag_add('response', line_start, line_end)
                continue
            
            # 檢查PASS/FAIL結果
            if 'Test is Pass' in line:
                self.text.insert(tk.INSERT, line + '\n')
                line_end = self.text.index(tk.INSERT)
                self.text.tag_add('pass_text', line_start, line_end)
                continue
            elif 'Test is Fail' in line or 'FAIL' in line or 'ERROR' in line:
                self.text.insert(tk.INSERT, line + '\n')
                line_end = self.text.index(tk.INSERT)
                self.text.tag_add('fail_text', line_start, line_end)
                continue
            
            # 一般行
            self.text.insert(tk.INSERT, line + '\n')
    
    def jump_to_step(self, step_name):
        """跳轉到指定step"""
        if step_name in self.step_positions:
            position = self.step_positions[step_name]
            self.text.see(position)
            self.text.mark_set(tk.INSERT, position)
    
    def highlight_error_block(self, start_line, end_line):
        """高亮錯誤區塊"""
        start_pos = f"{start_line}.0"
        end_pos = f"{end_line}.end"
        self.text.tag_add('error_block', start_pos, end_pos)
        self.text.see(start_pos)

class FailDetailsPanel:
    """FAIL詳細資訊面板"""
    
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """設定UI"""
        # 標題
        title_label = tk.Label(self.frame, text="錯誤完整區塊", 
                              font=('Arial', 12, 'bold'), fg='red')
        title_label.pack(pady=(10, 5))
        
        # 錯誤內容文字框（可複製）
        self.error_text = tk.Text(self.frame, height=8, wrap=tk.WORD, 
                                 bg='#FFE4E1', fg='red', font=('Consolas', 9))
        self.error_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 滾動條
        scrollbar = tk.Scrollbar(self.frame, command=self.error_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.error_text.config(yscrollcommand=scrollbar.set)
    
    def show_error_details(self, error_content):
        """顯示錯誤詳細內容"""
        self.error_text.delete('1.0', tk.END)
        self.error_text.insert('1.0', error_content)
        self.error_text.config(state=tk.NORMAL)  # 允許複製
    
    def clear(self):
        """清空內容"""
        self.error_text.delete('1.0', tk.END)

def extract_error_block(log_lines, fail_line_idx):
    """提取錯誤完整區塊"""
    if fail_line_idx is None or fail_line_idx >= len(log_lines):
        return ""
    
    # 往前找到指令開始
    start_idx = fail_line_idx
    for i in range(fail_line_idx, max(0, fail_line_idx - 50), -1):
        if '>' in log_lines[i]:  # 找到指令行
            start_idx = i
            break
    
    # 往後找到錯誤結束（或下一個指令）
    end_idx = fail_line_idx
    for i in range(fail_line_idx, min(len(log_lines), fail_line_idx + 20)):
        if i > fail_line_idx and ('>' in log_lines[i] or 'Do @STEP' in log_lines[i]):
            break
        end_idx = i
    
    # 提取區塊
    error_block = '\n'.join(log_lines[start_idx:end_idx + 1])
    return error_block