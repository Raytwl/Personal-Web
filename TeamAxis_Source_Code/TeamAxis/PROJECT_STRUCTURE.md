# TeamAxis 專案結構說明

## 完整專案結構

```
TeamAxis/
│
├── main.py                          # 主程式入口點
├── requirements.txt                 # Python 依賴套件列表
├── README.md                        # 專案說明文件（英文）
├── INSTALLATION_GUIDE.md            # 安裝與運行指南（繁體中文）
├── PROJECT_STRUCTURE.md             # 本文件 - 專案結構說明
│
├── database/                        # 資料庫模組
│   ├── __init__.py                 # Python 套件初始化
│   ├── db_manager.py               # 資料庫管理器（所有 CRUD 操作）
│   └── models.py                   # 資料模型定義（User, Project, Task, License, Risk）
│
├── auth/                           # 認證模組
│   ├── __init__.py                 # Python 套件初始化
│   └── login.py                    # 登入認證管理器
│
├── license/                         # License 管理模組
│   ├── __init__.py                 # Python 套件初始化
│   └── license_manager.py         # License 生成與管理
│
├── ui/                              # 使用者介面模組
│   ├── __init__.py                 # Python 套件初始化
│   ├── login_window.py             # 登入視窗
│   └── main_window.py              # 主應用程式視窗（包含所有功能標籤頁）
│
├── features/                        # 高級功能模組
│   ├── __init__.py                 # Python 套件初始化
│   ├── progress_visualization.py   # 專案進度視覺化（圖表生成）
│   ├── task_allocation.py          # 任務分配參考系統
│   └── risk_warning.py             # 風險警告系統
│
├── utils/                           # 工具函數模組
│   ├── __init__.py                 # Python 套件初始化
│   └── helpers.py                  # 輔助函數（日期格式化、顏色等）
│
└── teamaxis.db                      # SQLite 資料庫檔案（運行後自動生成）
```

## 檔案功能說明

### 核心檔案

#### `main.py`
- **功能**: 應用程式入口點
- **作用**: 啟動登入視窗，處理登入成功後的主視窗切換

#### `requirements.txt`
- **功能**: Python 依賴套件清單
- **包含**: matplotlib, pandas, numpy, Pillow

### 資料庫模組 (`database/`)

#### `models.py`
定義了五個主要資料模型：
- `User`: 用戶模型（ID, 用戶名, 密碼雜湊, 電子郵件, 角色）
- `Project`: 專案模型（ID, 名稱, 描述, 開始/結束日期, 狀態, 進度）
- `Task`: 任務模型（ID, 專案ID, 名稱, 描述, 分配者, 狀態, 優先級, 到期日, 進度）
- `License`: 授權模型（ID, 授權金鑰, 用戶ID, 發行/到期日期, 狀態）
- `Risk`: 風險模型（ID, 專案ID, 描述, 嚴重程度, 狀態, 緩解措施）

#### `db_manager.py`
資料庫管理器，提供所有資料庫操作：
- 資料庫初始化與表格創建
- 用戶操作（認證、創建、查詢）
- 專案操作（創建、查詢、更新進度）
- 任務操作（創建、查詢、更新狀態）
- License 操作（創建、查詢、更新狀態）
- 風險操作（創建、查詢、更新狀態）

### 認證模組 (`auth/`)

#### `login.py`
- `AuthManager`: 認證管理器
  - 處理用戶登入/登出
  - 管理當前登入用戶狀態
  - 檢查用戶權限（管理員）

### License 管理模組 (`license/`)

#### `license_manager.py`
- `LicenseManager`: License 管理器
  - 生成唯一授權金鑰
  - 創建授權（指定用戶和有效期）
  - 檢查授權有效性
  - 啟用/停用授權
  - 查詢即將到期的授權

### UI 模組 (`ui/`)

#### `login_window.py`
- `LoginWindow`: 登入視窗類別
  - 創建登入介面
  - 處理登入驗證
  - 登入成功後回調主視窗

#### `main_window.py`
- `MainWindow`: 主應用程式視窗類別
  - 創建選單欄和標籤頁介面
  - 實現所有功能標籤頁：
    - Dashboard（儀表板）
    - Projects（專案管理）
    - Tasks（任務管理）
    - License Management（授權管理）
    - Progress Visualization（進度視覺化）
    - Task Allocation（任務分配）
    - Risk Warning（風險警告）
  - 提供各種對話框（新建專案、任務、授權、風險等）
  - 資料刷新和顯示

### 功能模組 (`features/`)

#### `progress_visualization.py`
- `ProgressVisualizer`: 進度視覺化器
  - 生成專案進度條形圖
  - 生成任務狀態圓餅圖
  - 生成專案進度時間線圖表

#### `task_allocation.py`
- `TaskAllocationManager`: 任務分配管理器
  - 計算用戶工作負載
  - 提供任務分配建議
  - 生成工作負載平衡報告
  - 分析任務分配摘要

#### `risk_warning.py`
- `RiskWarningSystem`: 風險警告系統
  - 監控專案風險
  - 分析專案風險狀況
  - 生成風險摘要
  - 提供即時風險警報
  - 分類風險嚴重程度

### 工具模組 (`utils/`)

#### `helpers.py`
提供輔助函數：
- `format_date()`: 日期格式化
- `validate_date()`: 日期驗證
- `calculate_progress()`: 進度計算
- `get_status_color()`: 狀態顏色代碼
- `get_priority_color()`: 優先級顏色代碼
- `get_severity_color()`: 嚴重程度顏色代碼

## 資料流程

1. **啟動流程**:
   ```
   main.py → LoginWindow → 認證成功 → MainWindow
   ```

2. **資料流程**:
   ```
   UI → DatabaseManager → SQLite → 返回資料 → UI 顯示
   ```

3. **功能流程**:
   - **視覺化**: UI → ProgressVisualizer → DatabaseManager → 生成圖表 → UI
   - **任務分配**: UI → TaskAllocationManager → DatabaseManager → 分析 → UI
   - **風險警告**: UI → RiskWarningSystem → DatabaseManager → 分析 → UI

## 資料庫結構

### 表格

1. **users**: 用戶表
   - user_id (主鍵)
   - username (唯一)
   - password_hash
   - email
   - role
   - created_at

2. **projects**: 專案表
   - project_id (主鍵)
   - name
   - description
   - start_date
   - end_date
   - status
   - progress
   - created_at

3. **tasks**: 任務表
   - task_id (主鍵)
   - project_id (外鍵)
   - name
   - description
   - assignee_id (外鍵)
   - status
   - priority
   - due_date
   - progress
   - created_at

4. **licenses**: 授權表
   - license_id (主鍵)
   - license_key (唯一)
   - user_id (外鍵)
   - issue_date
   - expiry_date
   - status
   - created_at

5. **risks**: 風險表
   - risk_id (主鍵)
   - project_id (外鍵)
   - description
   - severity
   - status
   - mitigation
   - created_at

## 擴展建議

如果需要擴展功能，可以：

1. **添加新功能模組**: 在 `features/` 目錄下創建新檔案
2. **添加新資料模型**: 在 `database/models.py` 中添加，並在 `db_manager.py` 中實現操作
3. **添加新 UI 標籤頁**: 在 `ui/main_window.py` 中添加新的標籤頁方法
4. **添加新工具函數**: 在 `utils/helpers.py` 中添加

## 維護建議

1. **定期備份**: 備份 `teamaxis.db` 資料庫檔案
2. **日誌記錄**: 可以添加日誌記錄功能（使用 Python logging 模組）
3. **錯誤處理**: 已包含基本錯誤處理，可根據需要擴展
4. **測試**: 建議添加單元測試（使用 unittest 或 pytest）

---

**最後更新**: 2024

