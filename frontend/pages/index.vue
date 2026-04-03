<template>
  <main class="app-shell">
    <section class="app-panel">
      <p class="app-eyebrow">Cross-platform Beta Testing Ops</p>
      <h1 class="app-title">beta-feedback-platform</h1>
      <p class="app-description">
        這是一個跨平台 Beta 測試媒合與回饋管理平台，讓開發者能在同一個系統內完成
        測試招募、資格條件設定、任務派發、結構化回饋整理，以及第一版信譽摘要。
      </p>

      <div class="home-hero-actions">
        <NuxtLink
          class="resource-action"
          data-testid="home-start-projects-link"
          to="/projects"
        >
          Start with projects
        </NuxtLink>
        <NuxtLink
          class="resource-action"
          data-testid="home-start-campaigns-link"
          to="/campaigns"
        >
          Open campaigns
        </NuxtLink>
      </div>

      <section
        class="resource-section"
        data-testid="home-overview-section"
      >
        <h2 class="resource-section__title">Product Overview</h2>
        <div class="home-grid">
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">What this platform does</h3>
            <p class="home-summary-card__description">
              幫助開發者找到合適的測試者、管理不同平台的測試活動，並把 task 與 feedback
              留在同一條可追蹤流程內。
            </p>
          </div>
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">What this platform is not</h3>
            <ul class="home-list" data-testid="home-non-goals">
              <li>不是互刷平台</li>
              <li>不是評論交換平台</li>
              <li>不是灌量工具</li>
            </ul>
          </div>
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">Phase 1 platforms</h3>
            <div class="resource-shell__meta">
              <span class="resource-shell__meta-chip">Web / Mobile Web / PWA</span>
              <span class="resource-shell__meta-chip">iOS</span>
              <span class="resource-shell__meta-chip">Android</span>
            </div>
          </div>
        </div>
      </section>

      <section
        class="resource-section"
        data-testid="home-primary-nav"
      >
        <h2 class="resource-section__title">Core Modules</h2>
        <nav class="shell-link-grid" aria-label="Primary module navigation">
          <NuxtLink class="shell-link-card" data-testid="home-projects-link" to="/projects">
            <span class="shell-link-label">Projects</span>
            <strong class="shell-link-title">Product and testing scope</strong>
            <span class="shell-link-description">
              從產品主體開始整理測試目標，作為後續 campaign 與 task 的入口。
            </span>
          </NuxtLink>

          <NuxtLink class="shell-link-card" data-testid="home-campaigns-link" to="/campaigns">
            <span class="shell-link-label">Campaigns</span>
            <strong class="shell-link-title">Activities, safety, and rules</strong>
            <span class="shell-link-description">
              管理測試批次、來源標示、安全風險與 eligibility 條件。
            </span>
          </NuxtLink>

          <NuxtLink
            class="shell-link-card"
            data-testid="home-device-profiles-link"
            to="/device-profiles"
          >
            <span class="shell-link-label">Device Profiles</span>
            <strong class="shell-link-title">Tester device context</strong>
            <span class="shell-link-description">
              維護測試裝置與平台資訊，作為 eligibility、task 與 reputation 的 anchor。
            </span>
          </NuxtLink>

          <NuxtLink class="shell-link-card" data-testid="home-tasks-link" to="/tasks">
            <span class="shell-link-label">Tasks</span>
            <strong class="shell-link-title">Assignments and status flow</strong>
            <span class="shell-link-description">
              追蹤 task 指派、狀態流轉，以及 feedback 提交所在的主要操作入口。
            </span>
          </NuxtLink>
        </nav>
      </section>

      <section
        class="resource-section"
        data-testid="home-core-flow"
      >
        <h2 class="resource-section__title">Core Flow</h2>
        <ol class="home-flow">
          <li class="home-flow__item">
            <strong>Project</strong>
            <span>定義產品或測試主體。</span>
          </li>
          <li class="home-flow__item">
            <strong>Campaign</strong>
            <span>設定測試批次、平台條件、安全來源與資格規則。</span>
          </li>
          <li class="home-flow__item">
            <strong>Device Profile</strong>
            <span>建立 tester 裝置上下文，對齊 eligibility 與 assignment anchor。</span>
          </li>
          <li class="home-flow__item">
            <strong>Task</strong>
            <span>派發任務並追蹤 status flow。</span>
          </li>
          <li class="home-flow__item">
            <strong>Feedback</strong>
            <span>在 task context 下提交結構化回饋，並累積第一版 reputation signals。</span>
          </li>
        </ol>
      </section>

      <section class="resource-section">
        <h2 class="resource-section__title">Safety and Trust Principles</h2>
        <div class="home-grid">
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">Safety first</h3>
            <ul class="home-list">
              <li>優先採用各平台官方測試 / 分發機制</li>
              <li>不鼓勵來源不明安裝檔</li>
              <li>不鼓勵關閉裝置安全防護</li>
            </ul>
          </div>
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">Trust grows from activity</h3>
            <p class="home-summary-card__description">
              第一版 reputation 只做 derived summary，不做公開排行；重點是讓開發者與測試者都能看到最基本的合作訊號。
            </p>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped lang="scss">
.home-hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.home-grid {
  display: grid;
  gap: 1rem;
}

.home-summary-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;

  &__title {
    margin: 0;
    font-size: 1.05rem;
  }

  &__description {
    margin: 0;
    color: #cbd5e1;
    line-height: 1.7;
  }
}

.home-list {
  margin: 0;
  padding-left: 1.1rem;
  color: #cbd5e1;
  line-height: 1.8;
}

.home-flow {
  display: grid;
  gap: 0.85rem;
  margin: 0;
  padding-left: 1.25rem;
}

.home-flow__item {
  color: #cbd5e1;
  line-height: 1.7;

  strong {
    color: #e2e8f0;
    margin-right: 0.4rem;
  }
}

@media (min-width: 768px) {
  .home-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
