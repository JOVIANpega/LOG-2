# 測試Log分析器 - 實作文件

## 🎯 目標工作內容

根據您的需求，我已經完成了一個功能完整的GUI工具來分析測試log檔案。以下是各個Python檔案的詳細說明：

---

## 📁 檔案結構與功能

### 1. main.py - 主程式GUI介面
**用途**：提供現代化的圖形使用者介面來分析測試log檔案

#### 主要類別：LogAnalyzerApp

```python
class LogAnalyzerApp:
    def __init__(self, root):
        """
        初始化GUI應用程式
        - 設定視窗標題和大小
        - 載入使用者設定（字體大小等）
        - 初始化各個模組（log_parser, excel_writer, font_scaler）
        - 建立UI介面
        """
```

#### 核心方法說明：

**_build_ui(self)**
```python
def _build_ui(self):
    """
    建立主要UI結構
    - 使用PanedWindow實現左右分割視窗
    - 左側：檔案選擇與設定區域
    - 右側：分析結果顯示區域（Tab介面）
    """
```

**_build_left_panel(self, parent)**
```python
def _build_left_panel(self, parent):
    """
    建立左側控制面板
    - 檔案/資料夾選擇按鈕
    - 字體大小調整控制（+/-按鈕）
    - 分析按鈕
    - 顯示目前選擇的檔案/資料夾資訊
    """
```

**_build_right_panel(self, parent)**
```python
def _build_right_panel(self, parent):
    """
    建立右側結果顯示區域
    - Tab1：PASS測項清單（TreeView表格）
    - Tab2：FAIL測項清單（TreeView表格）
    - Tab3：原始LOG內容（Text元件）
    - 匯出Excel按鈕
    """
```

**_analyze_log(self)**
```python
def _analyze_log(self):
    """
    執行log分析的核心邏輯
    - 根據current_mode決定分析單檔或多檔
    - 呼叫log_parser進行解析
    - 更新各個Tab的內容
    - 處理FAIL項目的標紅顯示
    - 自動跳轉到相關Tab
    """
```

---

### 2. log_parser.py - Log解析引擎
**用途**：負責解析測試log檔案，分類PASS/FAIL，提取必要欄位

#### 主要類別：LogParser

```python
class LogParser:
    def __init__(self):
        """
        初始化解析器
        - 設定正則表達式模式來識別不同的log元素
        - step_pattern: 識別測試步驟 (@STEP數字@名稱)
        - cmd_pattern: 識別指令行 (> 開頭)
        - resp_pattern: 識別回應行 (< 開頭)
        - pass_pattern: 識別通過結果 (Test is Pass)
        - fail_pattern: 識別失敗結果 (Test is Fail)
        """
```

**parse_log_file(self, file_path)**
```python
def parse_log_file(self, file_path):
    """
    解析單一log檔案的主要方法
    
    處理流程：
    1. 讀取檔案內容，處理編碼問題
    2. 逐行掃描，識別測試步驟開始
    3. 收集每個測項的指令、回應、重試次數
    4. 判斷測試結果（PASS/FAIL）
    5. 對於FAIL項目，尋找錯誤訊息
    6. 回傳結構化的分析結果
    
    回傳格式：
    {
        'pass_items': [測試通過項目列表],
        'fail_items': [測試失敗項目列表],
        'raw_lines': [原始log行列表],
        'last_fail': 最後一個失敗項目,
        'fail_line_idx': 失敗行索引
    }
    """
```

**parse_log_folder(self, folder_path)**
```python
def parse_log_folder(self, folder_path):
    """
    解析資料夾內所有log檔案
    - 遞迴搜尋所有.log檔案
    - 合併所有檔案的分析結果
    - 適用於批次處理多個log檔案
    """
```

---

### 3. excel_writer.py - Excel匯出功能
**用途**：將log分析結果匯出為Excel檔案，支援PASS/FAIL分頁

#### 主要類別：ExcelWriter

```python
class ExcelWriter:
    def export(self, pass_items, fail_items, output_path):
        """
        匯出分析結果到Excel檔案
        
        功能說明：
        - 建立兩個工作表：PASS和FAIL
        - PASS工作表欄位：Step Name | 指令 | 回應 | 結果
        - FAIL工作表欄位：Step Name | 指令 | 錯誤回應 | Retry次數 | 錯誤原因
        - 使用pandas和openpyxl引擎確保相容性
        - 自動調整欄位寬度以提升可讀性
        """
```

---

### 4. ui_components.py - UI輔助元件
**用途**：提供GUI元件輔助函式，支援字體大小調整、分割視窗、Tab等

#### 主要類別：FontScaler

```python
class FontScaler:
    def __init__(self, root, min_size=10, max_size=15, default_size=11):
        """
        字體縮放管理器
        - 管理所有註冊的UI元件字體大小
        - 設定字體大小範圍限制
        - 支援即時調整和批次更新
        """
    
    def register(self, widget):
        """
        註冊需要字體調整的元件
        - 將元件加入管理清單
        - 後續字體調整會自動套用到所有註冊的元件
        """
    
    def set_font_size(self, size):
        """
        設定字體大小並即時套用
        - 檢查大小範圍限制
        - 批次更新所有註冊元件的字體
        - 特別處理TreeView元件的樣式設定
        """
```

---

### 5. settings_loader.py - 設定管理
**用途**：管理GUI工具的本地設定（如字體大小），支援讀取與寫入settings.json

#### 主要函數：

```python
def load_settings():
    """
    讀取本地設定檔
    - 檢查settings.json是否存在
    - 若不存在則回傳預設值
    - 處理檔案讀取錯誤，確保程式穩定性
    - 合併預設設定與使用者設定
    """

def save_settings(settings):
    """
    儲存設定到本地檔案
    - 將設定字典寫入settings.json
    - 使用UTF-8編碼確保中文相容性
    - 格式化JSON輸出提升可讀性
    - 錯誤處理避免程式崩潰
    """
```

---

## 🔧 核心功能實現

### 1. 左右分割視窗
- 使用`tk.PanedWindow`實現可調整的分割視窗
- 左側最小寬度220px，右側最小寬度600px
- 使用者可拖拉調整比例

### 2. 字體大小控制
- 預設字體大小11，可調整範圍10-15
- 使用+/-按鈕進行調整，不使用滑桿
- 即時套用到所有UI元件
- 設定自動儲存到settings.json

### 3. Log分析邏輯
- 正則表達式識別測試步驟、指令、回應
- 自動分類PASS/FAIL結果
- 提取錯誤訊息和重試次數
- 支援單檔和多檔分析模式

### 4. 結果顯示
- Tab1：PASS測項表格顯示
- Tab2：FAIL測項表格顯示（錯誤項目標紅）
- Tab3：原始LOG內容（失敗行標紅並自動跳轉）

### 5. Excel匯出
- 僅多檔模式支援匯出
- 分別建立PASS和FAIL工作表
- 欄位符合規格要求
- 使用pandas確保資料正確性

---

## 🚀 使用流程

1. **啟動程式**：執行`python main.py`
2. **選擇檔案**：點擊「選擇檔案」或「選擇資料夾」
3. **開始分析**：點擊「開始分析」按鈕
4. **查看結果**：在各個Tab中查看分析結果
5. **調整字體**：使用+/-按鈕調整介面大小
6. **匯出報告**：多檔模式下可匯出Excel報告

---

## 📋 技術特色

- **模組化設計**：功能分離，易於維護和擴展
- **錯誤處理**：完善的異常處理機制
- **使用者體驗**：直觀的操作介面和即時反饋
- **資料安全**：UTF-8編碼處理，避免中文亂碼
- **效能優化**：大檔案處理和記憶體管理
- **設定持久化**：使用者偏好自動儲存

這個實作完全符合您的需求規格，提供了一個功能完整、使用者友善的測試log分析工具。