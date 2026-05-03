# TeamAxis 快速開始指南

## 5 分鐘快速啟動

### 步驟 1: 確認 Python 已安裝
```bash
python --version
```
應該顯示 Python 3.8 或更高版本

### 步驟 2: 安裝依賴
```bash
cd C:\Users\HP\Desktop\TeamAxis
pip install -r requirements.txt
```

### 步驟 3: 運行應用程式
```bash
python main.py
```

### 步驟 4: 登入或註冊

**登入（管理員）**:
- 使用者名稱: `admin`
- 密碼: `admin123`
- License Key: 管理員可以跳過（留空或使用預設值）

**註冊新用戶**:
1. 點擊 "Register" 按鈕
2. 填寫用戶名、密碼、確認密碼、電子郵件
3. 輸入有效的 License Key（格式：XXXX-XXXX-XXXX-XXXX）
4. 點擊 "Register"

**注意**: 
- 普通用戶登入時必須提供有效的 License Key
- License Key 格式為：XXXX-XXXX-XXXX-XXXX（16個字符，用連字符分隔）
- 管理員可以跳過 License 驗證

## 第一次使用

### 1. 創建第一個專案
1. 點擊 "Projects" 標籤頁
2. 點擊 "New Project" 按鈕
3. 填寫專案資訊：
   - 專案名稱（必填）
   - 描述（可選）
   - 開始日期（格式：YYYY-MM-DD）
   - 結束日期（格式：YYYY-MM-DD）
4. 點擊 "Create"

### 2. 創建任務
1. 點擊 "Tasks" 標籤頁
2. 點擊 "New Task" 按鈕
3. 選擇專案並填寫任務資訊
4. 分配給用戶（可選）
5. 設置優先級和到期日
6. 點擊 "Create"

### 3. 查看進度視覺化
1. 點擊 "Progress Visualization" 標籤頁
2. 選擇專案或查看所有專案
3. 查看進度條形圖和任務狀態圓餅圖

### 4. 使用任務分配功能
1. 點擊 "Task Allocation" 標籤頁
2. 查看所有用戶的工作負載
3. 點擊 "Workload Report" 查看詳細報告

### 5. 添加風險警告
1. 點擊 "Risk Warning" 標籤頁
2. 點擊 "Add Risk" 按鈕
3. 選擇專案並描述風險
4. 設置嚴重程度
5. 點擊 "Add"

### 6. 管理 License
1. 點擊 "License Management" 標籤頁
2. 點擊 "Generate License" 按鈕
3. 選擇用戶和有效期（天數）
4. 點擊 "Generate"
5. 複製並保存授權金鑰

## 常用操作

### 查看專案詳情
- 在 "Projects" 標籤頁中雙擊專案名稱，會自動跳轉到視覺化頁面

### 刷新資料
- 每個標籤頁都有 "Refresh" 按鈕，點擊即可更新資料

### 登出
- 點擊選單欄 "File" → "Logout"

## 提示

1. **日期格式**: 所有日期必須使用 YYYY-MM-DD 格式（例如：2024-01-15）
2. **優先級**: 可選值為 low, medium, high, critical
3. **任務狀態**: pending, in_progress, completed, blocked
4. **專案狀態**: active, completed, on_hold, cancelled
5. **風險嚴重程度**: low, medium, high, critical

## 故障排除

### 應用程式無法啟動
- 檢查 Python 版本
- 確認所有依賴已安裝
- 查看錯誤訊息

### 圖表無法顯示
- 確保已創建專案和任務
- 檢查 matplotlib 是否正確安裝

### 資料庫錯誤
- 刪除 `teamaxis.db` 讓系統重新創建
- 確保有寫入權限

## 下一步

- 閱讀 `INSTALLATION_GUIDE.md` 了解詳細安裝步驟
- 閱讀 `PROJECT_STRUCTURE.md` 了解專案架構
- 閱讀 `README.md` 了解完整功能說明

---

**開始使用 TeamAxis 管理您的專案吧！**

