# T088 - App Shell Redesign

## 1. 背景

當 public homepage、auth pages 與 `/dashboard` 都分層之後，登入後 app shell 需要被明確重新設計，才能和 public layout 拉開距離。現在的 shell 已有產品化基線，但比例、導覽層級與 page frame 仍是逐步疊加出來的結果。

## 2. 目標

重新設計登入後 app shell，使它更像成熟產品工作區，而不是從 public/home 演化而來的混合殼。

## 3. 範圍

- redesign sidebar
- redesign slim topbar
- redesign page frame / content spacing
- 將 `Dashboard` 放到第一主導航
- 保留 light/dark、locale、session/account controls

## 4. Shell 建議

### Sidebar

- 第一入口：
  - `Dashboard`
- 保留現有分組：
  - 我的工作區
  - 營運與審查
  - 核心資源
- 重新整理：
  - 分組層級
  - active state
  - icon / chip style
  - padding / width / density

### Topbar

- 比首頁 public header 更產品內頁化
- 保留：
  - locale
  - theme
  - session/account summary
  - actor/session context
- 收斂高度、gap、controls hierarchy

### Page Frame

- 統一：
  - max width
  - header spacing
  - section spacing
  - list/detail/form 的外層 frame rhythm

## 5. API / Route 建議

不新增 API。

route 不變，但 shell navigation 需加入：

- `/dashboard`

## 6. 前端頁面 / 路由建議

主要修改：

- app layout / shell component
- navigation data source
- shared shell SCSS tokens / layout styles

## 7. Acceptance Criteria

- app shell 與 public layout 視覺語言明顯不同
- `Dashboard` 是第一主導航
- app shell 比例、密度與閱讀節奏更穩定
- 現有 session / locale / theme / actor controls 仍可使用

## 8. Out of Scope

- 不重做每個 detail page 的內容
- 不重做 public homepage
- 不改 backend auth/session

## 9. Backend Work Items

- 無新的 runtime 工作

## 10. Frontend Work Items

- redesign sidebar
- redesign topbar
- redesign app page frame
- dashboard nav integration
- shell regression tests

## 11. Test Items

- frontend `typecheck`
- frontend `build`
- shell navigation regression
- dashboard nav regression
- theme / locale / session controls regression
- mobile nav smoke

## 12. Risk / Notes

- 這張票要避免同時去重排每個 detail page 內容，否則 scope 會爆開
- 核心是 shell 層與 page frame，不是頁面內部所有資訊重組

## 13. 依賴關係（Dependencies）

- `T084`
- 建議在 `T087` 後做
