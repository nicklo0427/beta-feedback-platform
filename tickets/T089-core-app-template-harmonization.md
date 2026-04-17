# T089 - Core App Template Harmonization

## 1. 背景

shell 層設計完成後，高頻 app 頁面仍可能保留不同世代的 page template 節奏。若不進一步 harmonize，整體產品感仍會在進到 workspace/list/detail/form 後被打散。

## 2. 目標

把高頻 app 頁面收斂到新的 template 語言，讓登入後工作區具備一致的：

- page header
- summary hierarchy
- actions row
- list rhythm
- detail + context rail 結構

## 3. 範圍

優先頁面：

- `/my/projects`
- `/my/campaigns`
- `/my/tasks`
- `/my/eligible-campaigns`
- `/my/participation-requests`
- `/review/feedback`
- `/review/participation-requests`
- `/projects`
- `/campaigns`
- `/tasks`

以及上述高頻頁面最常用的 detail 頁。

## 4. Template 建議

### Workspace / Queue Pages

- summary cards
- queue / cards
- next actions
- 清楚的 section hierarchy

### Resource List Pages

- page header
- filters / actions row
- list body
- empty / loading / error state

### Detail Pages

- 主欄 + context rail
- 清楚的 breadcrumb / eyebrow / title / meta chips
- timeline / related actions / summary panels 收斂到 context 區

## 5. API / Route 建議

不新增 API。

不改 route。

## 6. 前端頁面 / 路由建議

主要修改：

- 高頻 workspace/list/detail 頁
- shared page template classes / components
- context rail / section header helpers

## 7. Acceptance Criteria

- 高頻 app 頁面節奏一致
- list / detail / workspace 不再混用不同世代結構
- context rail、header hierarchy 與 actions row 收斂
- 不改 backend data flow

## 8. Out of Scope

- 不要求整站所有低頻 admin/resource 頁一次全部重做
- 不做資料邏輯重構
- 不新增 analytics / charts

## 9. Backend Work Items

- 無新的 runtime 工作

## 10. Frontend Work Items

- workspace template harmonization
- list template harmonization
- detail + context rail harmonization
- 共用 page section / header / meta styles 收斂
- 補高頻頁面 regression

## 11. Test Items

- frontend `typecheck`
- frontend `build`
- workspace page regression
- list page regression
- detail page regression
- app shell + page template integration smoke

## 12. Risk / Notes

- 這張票容易 scope 膨脹，所以應先以高頻 app 頁面為主
- 不需要在這張票把所有低優先權 CRUD 頁全部翻新

## 13. 依賴關係（Dependencies）

- `T088`
