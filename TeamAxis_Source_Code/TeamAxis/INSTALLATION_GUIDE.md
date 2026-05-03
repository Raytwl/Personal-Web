# TeamAxis 安裝與運行指南

## 系統需求

- **作業系統**: Windows 10 或更高版本
- **Python**: Python 3.8 或更高版本
- **硬碟空間**: 至少 100 MB 可用空間

## 第一步：檢查 Python 安裝

1. 打開命令提示字元（Command Prompt）或 PowerShell
2. 輸入以下命令檢查 Python 是否已安裝：
```bash
python --version
```

如果顯示 Python 3.8 或更高版本，則可以繼續。如果沒有安裝 Python，請前往 [python.org](https://www.python.org/downloads/) 下載並安裝。

**注意**: 安裝 Python 時，請確保勾選 "Add Python to PATH" 選項。

## 第二步：下載或確認專案檔案

確保您已經有完整的 TeamAxis 專案資料夾，包含以下結構：

```
TeamAxis/
├── main.py
├── requirements.txt
├── README.md
├── database/
│   ├── __init__.py
│   ├── db_manager.py
│   └── models.py
├── auth/
│   ├── __init__.py
│   └── login.py
├── license/
│   ├── __init__.py
│   └── license_manager.py
├── ui/
│   ├── __init__.py
│   ├── login_window.py
│   └── main_window.py
├── features/
│   ├── __init__.py
│   ├── progress_visualization.py
│   ├── task_allocation.py
│   └── risk_warning.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

## 第三步：安裝依賴套件

1. 打開命令提示字元或 PowerShell
2. 導航到 TeamAxis 專案目錄：
```bash
cd C:\Users\HP\Desktop\TeamAxis
```
（請根據您的實際路徑調整）

3. 安裝所需的 Python 套件：
```bash
pip install -r requirements.txt
```

這將安裝以下套件：
- matplotlib (用於圖表視覺化)
- pandas (用於資料處理)
- numpy (用於數值計算)
- Pillow (用於圖像處理)

**注意**: 
- `tkinter` 通常隨 Python 一起安裝，如果遇到問題，可能需要單獨安裝
- `sqlite3` 是 Python 標準庫的一部分，無需單獨安裝

如果遇到權限問題，可以嘗試：
```bash
pip install --user -r requirements.txt
```

## 第四步：運行應用程式

1. 確保您在 TeamAxis 專案目錄中
2. 運行主程式：
```bash
python main.py
```

應用程式應該會啟動並顯示登入視窗。

## 預設登入憑證

首次運行時，使用以下憑證登入（管理員帳號）：
- **使用者名稱**: `admin`
- **密碼**: `admin123`
- **License Key**: 管理員可以跳過（留空或使用預設值）

**重要**: 登入後請立即更改密碼以確保安全性。

## 用戶註冊

### 註冊新用戶

1. 在登入視窗點擊 "Register" 按鈕
2. 填寫以下資訊：
   - **使用者名稱**: 必須唯一
   - **密碼**: 至少 6 個字符
   - **確認密碼**: 必須與密碼一致
   - **電子郵件**: 可選
   - **License Key**: 必須提供有效的授權金鑰（格式：XXXX-XXXX-XXXX-XXXX）

3. 點擊 "Register" 完成註冊

### License Key 格式

- License Key 格式為：`XXXX-XXXX-XXXX-XXXX`
- 共 16 個字符（字母和數字），用連字符分隔成 4 組
- 例如：`A1B2-C3D4-E5F6-G7H8`

### 登入要求

- **管理員用戶**: 可以跳過 License Key 驗證
- **普通用戶**: 必須提供有效的 License Key 才能登入
- License Key 必須：
  - 存在於系統中
  - 狀態為 "active"
  - 未過期
  - 屬於該用戶（或未分配）

### 獲取 License Key

管理員可以在主視窗的 "License Management" 標籤頁中生成新的 License Key：
1. 點擊 "Generate License" 按鈕
2. 選擇用戶（可選，留空則創建未分配的 License）
3. 設置有效期（天數）
4. 點擊 "Generate"
5. 複製生成的 License Key 並提供給用戶

## 功能說明

### 基本功能

1. **用戶登入 (User Login)**
   - 安全的用戶認證系統
   - 支援多用戶管理

2. **License 管理 (License Management)**
   - 生成和管理軟體授權
   - 追蹤授權到期日期
   - 啟用/停用授權

3. **資料庫功能 (Database)**
   - SQLite 資料庫自動初始化
   - 專案、任務、用戶、授權和風險資料管理

### 高級功能 (N-1)

1. **視覺化專案進度 (Visualize Project Progress)**
   - 專案進度條形圖
   - 任務狀態圓餅圖
   - 可選擇特定專案或查看所有專案

2. **任務分配參考 (Reference for Task Allocation)**
   - 用戶工作負載分析
   - 任務分配建議
   - 工作負載平衡報告

3. **風險警告 (Risk Warning)**
   - 專案風險監控
   - 風險嚴重程度分類
   - 自動風險警報
   - 風險摘要報告

## 使用介面說明

### 主視窗標籤頁

1. **Dashboard (儀表板)**
   - 顯示系統統計資訊
   - 最近專案列表

2. **Projects (專案)**
   - 查看所有專案
   - 創建新專案
   - 雙擊專案可查看視覺化

3. **Tasks (任務)**
   - 查看所有任務
   - 創建新任務
   - 分配任務給用戶

4. **License Management (授權管理)**
   - 生成新授權
   - 查看所有授權
   - 管理授權狀態

5. **Progress Visualization (進度視覺化)**
   - 選擇專案查看圖表
   - 專案進度條形圖
   - 任務狀態分佈圖

6. **Task Allocation (任務分配)**
   - 查看用戶工作負載
   - 獲取分配建議
   - 查看工作負載報告

7. **Risk Warning (風險警告)**
   - 查看所有風險
   - 添加新風險
   - 查看風險摘要

## 常見問題

### Q1: 運行時出現 "ModuleNotFoundError"
**解決方案**: 確保已安裝所有依賴套件：
```bash
pip install -r requirements.txt
```

### Q2: tkinter 無法導入
**解決方案**: 
- Windows: 通常 tkinter 已包含在 Python 安裝中
- 如果沒有，可能需要重新安裝 Python 並選擇 "tcl/tk" 選項

### Q3: 資料庫錯誤
**解決方案**: 
- 確保有寫入權限
- 刪除 `teamaxis.db` 檔案讓系統重新創建

### Q4: 圖表無法顯示
**解決方案**: 
- 確保已安裝 matplotlib
- 檢查是否有足夠的專案和任務資料

### Q5: 應用程式無法啟動
**解決方案**: 
1. 檢查 Python 版本：`python --version`
2. 檢查所有檔案是否完整
3. 查看錯誤訊息並對照解決

## 資料庫檔案

應用程式會自動創建 `teamaxis.db` SQLite 資料庫檔案在專案根目錄。此檔案包含所有應用程式資料。

**備份建議**: 定期備份 `teamaxis.db` 檔案以保護您的資料。

## 更新應用程式

如果需要更新應用程式：
1. 備份 `teamaxis.db` 資料庫檔案
2. 替換程式碼檔案
3. 重新安裝依賴（如果需要）：
```bash
pip install -r requirements.txt --upgrade
```

## 技術支援

如果遇到問題：
1. 檢查錯誤訊息
2. 確認所有依賴已正確安裝
3. 確認 Python 版本符合要求
4. 檢查檔案完整性

## 系統架構

- **語言**: Python 3.8+
- **資料庫**: SQLite3
- **UI 框架**: Tkinter
- **圖表庫**: Matplotlib
- **資料處理**: Pandas, NumPy

## 安全注意事項

1. 首次登入後立即更改預設密碼
2. 定期備份資料庫檔案
3. 不要在公共電腦上儲存敏感資料
4. License 管理功能僅供授權用戶使用

---

**祝您使用愉快！**

