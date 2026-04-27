# T083 - Homepage Generated Visual Direction and Brand Panels

## 1. 背景

目前首頁的資訊架構已逐步產品化，但品牌視覺層仍偏薄。文案與 layout 已經比早期版本清楚很多，然而登入前首頁還缺少能建立「專業感 / 產品感 / beta platform 信任感」的視覺主體。

如果只靠文字與 card，第一眼仍容易偏向 internal tool，而不是外部 beta collaboration product。

## 2. 目標

在首頁加入生成圖片與品牌視覺模組，讓登入前首頁更有：

- 產品感
- 專業感
- 視覺焦點
- 對開發者 / 測試者雙角色的情境暗示

## 3. 範圍

- 為首頁設計並導入生成圖片資產
- 將圖片整合進 hero / supporting brand panels
- 確保 light / dark 主題、桌機優先、手機可用
- 與既有 i18n 文案共存，不產生文案與視覺互相打架的情況

## 4. 視覺方向建議

建議方向：

- 不是 stock photo 拼貼
- 不是過度抽象的 AI 裝飾圖
- 而是偏產品品牌插畫 / composited concept visual

畫面內容可圍繞：

- developer workspace
- tester participation
- task / feedback / review 流程
- 多平台 beta 測試情境

建議至少有：

- 1 個 hero 主視覺
- 1 到 2 個 supporting visual panels

## 5. 資產建議

資產可放在：

- `frontend/public/...`
- 或 `frontend/assets/...`

應保留：

- prompt / variant 選擇紀錄
- 最終採用版本
- 壓縮後可直接進 repo 的尺寸

## 6. API 路徑建議

本票不新增 API。

## 7. 前端頁面 / 路由建議

- 主要修改：
  - `frontend/pages/index.vue`
- 視需要調整：
  - `frontend/assets/scss/_layout.scss`
  - `frontend/assets/scss/_components.scss`
  - 新增首頁專用局部樣式或 visual component

## 8. Acceptance Criteria

- 首頁至少有一個明確的 hero 視覺焦點
- 圖像與文案能共同強化產品定位
- 圖像在 light / dark 下都不顯突兀
- 390px 手機寬度下不爆版
- 不影響首頁 CTA 可讀性與可點擊性
- 圖像資產已實際納入 repo，不只是 ticket 描述

## 9. Out of Scope

- 不做全站插畫系統
- 不做 image CDN / media pipeline
- 不做影片背景
- 不做大型動態 3D / WebGL 視覺

## 10. Backend Work Items

- 無新的 runtime 工作

## 11. Frontend Work Items

- 產出並挑選生成圖片
- 導入首頁 hero / supporting panels
- 補齊 light / dark / responsive 視覺整合
- 補必要的 i18n alt / caption 文案
- 補最小 visual regression / screenshot 驗收

## 12. Test Items

- frontend `typecheck`
- frontend `build`
- homepage desktop screenshot regression
- homepage mobile screenshot regression
- `zh-TW / en` 文案與圖片共存 smoke
- theme toggle 下的首頁 smoke

## 13. Risk / Notes

- 最大風險不是技術，而是生成圖風格失控，讓首頁看起來像 generic AI landing page
- 圖像要服務產品定位，不是只為了「有圖」
- 若首輪生成結果太像 stock / 太抽象，寧可少量但精緻

## 14. 依賴關係（Dependencies）

建議依賴：

- `T082`

如果希望並行進行，也至少要先確認 `T082` 的首頁資訊架構方向，避免圖片做完後 hero 結構又改掉。
