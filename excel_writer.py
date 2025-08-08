# excel_writer.py
# 用途：將log分析結果匯出為Excel檔案，支援PASS/FAIL分頁，欄位依規格
import pandas as pd

class ExcelWriter:
    def __init__(self):
        pass

    def export(self, pass_items, fail_items, output_path):
        """
        匯出分析結果到Excel，分為PASS/FAIL兩個sheet
        pass_items: List[dict]
        fail_items: List[dict]
        output_path: str
        """
        # PASS欄位：Step Name | 指令 | 回應 | 結果
        pass_df = pd.DataFrame(pass_items)
        if not pass_df.empty:
            pass_df = pass_df[['step_name', 'command', 'response', 'result']]
            pass_df.columns = ['Step Name', '指令', '回應', '結果']
        # FAIL欄位：Step Name | 指令 | 錯誤回應 | Retry 次數 | 錯誤原因
        fail_df = pd.DataFrame(fail_items)
        if not fail_df.empty:
            fail_df = fail_df[['step_name', 'command', 'response', 'retry', 'error']]
            fail_df.columns = ['Step Name', '指令', '錯誤回應', 'Retry 次數', '錯誤原因']
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            if not pass_df.empty:
                pass_df.to_excel(writer, sheet_name='PASS', index=False)
            if not fail_df.empty:
                fail_df.to_excel(writer, sheet_name='FAIL', index=False) 