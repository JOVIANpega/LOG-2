#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器GUI應用程式
提供現代化的圖形使用者介面來分析測試log檔案
支援標準版和增強版模式
"""

import tkinter as tk
import sys
import os

def main():
    """主程式入口點"""
    # 檢查命令行參數
    if len(sys.argv) > 1 and sys.argv[1] == '--classic':
        # 標準版
        from main_standard import main as main_standard_func
        main_standard_func()
    else:
        # 增強版（預設）
        from main_enhanced import main_enhanced as main_enhanced_func
        main_enhanced_func()

if __name__ == '__main__':
    main() 