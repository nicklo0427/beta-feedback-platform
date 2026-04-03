<template>
  <main class="app-shell">
    <section class="app-panel">
      <p class="app-eyebrow">Frontend Bootstrap</p>
      <h1 class="app-title">beta-feedback-platform</h1>
      <p class="app-description">
        這是一個 Nuxt 3 + TypeScript 的最小前端骨架，用於驗證初始化完成。
        目前只保留框架入口、路由首頁，以及 Tailwind CSS / Pinia 的接入基礎，
        尚未實作任何業務頁面或業務流程。
      </p>

      <nav class="shell-link-grid" aria-label="Frontend shell navigation">
        <NuxtLink class="shell-link-card" data-testid="home-projects-link" to="/projects">
          <span class="shell-link-label">Projects</span>
          <strong class="shell-link-title">Project Shell</strong>
          <span class="shell-link-description">
            查看 Project list 與 detail 的最小頁面骨架。
          </span>
        </NuxtLink>

        <NuxtLink class="shell-link-card" data-testid="home-campaigns-link" to="/campaigns">
          <span class="shell-link-label">Campaigns</span>
          <strong class="shell-link-title">Campaign Shell</strong>
          <span class="shell-link-description">
            查看 Campaign list 與 detail 的最小頁面骨架。
          </span>
        </NuxtLink>

        <NuxtLink class="shell-link-card" data-testid="home-tasks-link" to="/tasks">
          <span class="shell-link-label">Tasks</span>
          <strong class="shell-link-title">Task Shell</strong>
          <span class="shell-link-description">
            查看 Task list 與 detail 的最小頁面骨架。
          </span>
        </NuxtLink>

        <NuxtLink
          class="shell-link-card"
          data-testid="home-device-profiles-link"
          to="/device-profiles"
        >
          <span class="shell-link-label">Device Profiles</span>
          <strong class="shell-link-title">Tester Device Profile Shell</strong>
          <span class="shell-link-description">
            查看 Tester Device Profile list 與 detail 的最小頁面骨架。
          </span>
        </NuxtLink>
      </nav>
    </section>
  </main>
</template>
