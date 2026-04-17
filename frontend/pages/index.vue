<script setup lang="ts">
import { computed } from 'vue'

import { useAuthRuntimeMode, useAuthSession } from '~/features/accounts/current-actor'
import { useAppI18n } from '~/features/i18n/use-app-i18n'

definePageMeta({
  layout: 'public'
})

const authRuntimeMode = useAuthRuntimeMode()
const authSession = useAuthSession()
const { locale, t } = useAppI18n()

const showLocalFallbackNote = computed(
  () => authRuntimeMode.value !== 'session_only' && authSession.value?.account == null
)
</script>

<template>
  <main class="app-shell public-home" :data-locale="locale">
    <section class="app-panel public-home__panel">
      <section class="resource-section home-landing-hero" data-testid="home-guest-hero">
        <div class="home-landing-hero__grid">
          <div class="home-landing-hero__copy">
            <p class="app-eyebrow">{{ t('home.guest.eyebrow') }}</p>
            <h1 class="app-title">beta-feedback-platform</h1>
            <p class="app-description">
              {{ t('home.guest.description') }}
            </p>

            <div class="home-hero-actions">
              <NuxtLink
                class="resource-action"
                data-testid="home-guest-login-link"
                to="/login"
              >
                {{ t('home.guest.actions.login') }}
              </NuxtLink>
              <NuxtLink
                class="resource-action"
                data-testid="home-guest-register-link"
                to="/register"
              >
                {{ t('home.guest.actions.register') }}
              </NuxtLink>
              <a
                class="resource-action resource-action--quiet"
                data-testid="home-guest-flow-link"
                href="#home-flow"
              >
                {{ t('home.guest.actions.learnMore') }}
              </a>
            </div>
          </div>

          <figure class="home-brand-hero" data-testid="home-guest-visual">
            <div class="home-brand-hero__frame">
              <img
                class="home-brand-hero__image"
                :src="'/brand/t083-hero-collaboration-scene.svg'"
                :alt="t('home.guest.visuals.heroAlt')"
              >
              <div class="home-brand-hero__callout home-brand-hero__callout--top">
                <span class="resource-shell__meta-chip">{{ t('home.guest.visuals.heroLabel') }}</span>
              </div>
              <div class="home-brand-hero__callout home-brand-hero__callout--bottom">
                <span class="resource-shell__meta-chip">{{ t('home.guest.cards.workflowValue') }}</span>
                <span class="resource-shell__meta-chip">{{ t('home.guest.cards.developerValue') }}</span>
              </div>
            </div>
            <figcaption class="home-brand-hero__caption">
              <span class="shell-link-label">{{ t('home.guest.visuals.heroLabel') }}</span>
              <strong class="shell-link-title">{{ t('home.guest.visuals.heroTitle') }}</strong>
              <span class="shell-link-description">
                {{ t('home.guest.visuals.heroDescription') }}
              </span>
            </figcaption>
          </figure>
        </div>

        <div class="home-guest-grid">
          <article class="summary-stat-card">
            <span class="summary-stat-card__label">{{ t('home.guest.cards.developerLabel') }}</span>
            <strong class="summary-stat-card__value">{{ t('home.guest.cards.developerValue') }}</strong>
            <p class="home-summary-card__description">
              {{ t('home.guest.cards.developerDescription') }}
            </p>
          </article>
          <article class="summary-stat-card">
            <span class="summary-stat-card__label">{{ t('home.guest.cards.testerLabel') }}</span>
            <strong class="summary-stat-card__value">{{ t('home.guest.cards.testerValue') }}</strong>
            <p class="home-summary-card__description">
              {{ t('home.guest.cards.testerDescription') }}
            </p>
          </article>
          <article class="summary-stat-card">
            <span class="summary-stat-card__label">{{ t('home.guest.cards.workflowLabel') }}</span>
            <strong class="summary-stat-card__value">{{ t('home.guest.cards.workflowValue') }}</strong>
            <p class="home-summary-card__description">
              {{ t('home.guest.cards.workflowDescription') }}
            </p>
          </article>
        </div>
      </section>

      <section class="resource-section" data-testid="home-overview-section">
        <h2 class="resource-section__title">{{ t('home.overview.title') }}</h2>
        <div class="home-grid">
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">{{ t('home.overview.whatTitle') }}</h3>
            <p class="home-summary-card__description">
              {{ t('home.overview.whatDescription') }}
            </p>
          </div>
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">{{ t('home.overview.notWhatTitle') }}</h3>
            <ul class="home-list" data-testid="home-non-goals">
              <li>{{ t('home.overview.nonGoals.ratingFarm') }}</li>
              <li>{{ t('home.overview.nonGoals.reviewExchange') }}</li>
              <li>{{ t('home.overview.nonGoals.trafficBoost') }}</li>
            </ul>
          </div>
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">{{ t('home.overview.supportedPlatformsTitle') }}</h3>
            <div class="resource-shell__meta">
              <span class="resource-shell__meta-chip">{{ t('home.overview.platformChipWeb') }}</span>
              <span class="resource-shell__meta-chip">{{ t('home.overview.platformChipIos') }}</span>
              <span class="resource-shell__meta-chip">{{ t('home.overview.platformChipAndroid') }}</span>
            </div>
          </div>
        </div>
      </section>

      <section class="resource-section" data-testid="home-entry-section">
        <h2 class="resource-section__title">{{ t('home.guest.entryTitle') }}</h2>
        <p class="resource-section__description">
          {{ t('home.guest.entryDescription') }}
        </p>

        <div class="home-entry-grid">
          <NuxtLink class="shell-link-card" data-testid="home-entry-login-card" to="/login">
            <span class="shell-link-label">{{ t('home.guest.loginCardLabel') }}</span>
            <strong class="shell-link-title">{{ t('home.guest.loginCardTitle') }}</strong>
            <span class="shell-link-description">
              {{ t('home.guest.loginCardDescription') }}
            </span>
          </NuxtLink>

          <NuxtLink class="shell-link-card" data-testid="home-entry-register-card" to="/register">
            <span class="shell-link-label">{{ t('home.guest.registerCardLabel') }}</span>
            <strong class="shell-link-title">{{ t('home.guest.registerCardTitle') }}</strong>
            <span class="shell-link-description">
              {{ t('home.guest.registerCardDescription') }}
            </span>
          </NuxtLink>
        </div>
      </section>

      <section class="resource-section" data-testid="home-visual-story-section">
        <h2 class="resource-section__title">{{ t('home.guest.visuals.sectionTitle') }}</h2>
        <p class="resource-section__description">
          {{ t('home.guest.visuals.sectionDescription') }}
        </p>

        <div class="home-visual-story-grid">
          <article class="home-visual-panel" data-testid="home-supporting-visual-review">
            <figure class="home-visual-panel__figure">
              <img
                class="home-visual-panel__image"
                :src="'/brand/t083-review-pipeline-scene.svg'"
                :alt="t('home.guest.visuals.reviewAlt')"
                loading="lazy"
              >
            </figure>
            <div class="home-visual-panel__body">
              <span class="shell-link-label">{{ t('home.guest.visuals.reviewLabel') }}</span>
              <strong class="shell-link-title">{{ t('home.guest.visuals.reviewTitle') }}</strong>
              <p class="shell-link-description">{{ t('home.guest.visuals.reviewDescription') }}</p>
            </div>
          </article>

          <article class="home-visual-panel" data-testid="home-supporting-visual-tester">
            <figure class="home-visual-panel__figure">
              <img
                class="home-visual-panel__image"
                :src="'/brand/t083-device-participation-scene.svg'"
                :alt="t('home.guest.visuals.testerAlt')"
                loading="lazy"
              >
            </figure>
            <div class="home-visual-panel__body">
              <span class="shell-link-label">{{ t('home.guest.visuals.testerLabel') }}</span>
              <strong class="shell-link-title">{{ t('home.guest.visuals.testerTitle') }}</strong>
              <p class="shell-link-description">{{ t('home.guest.visuals.testerDescription') }}</p>
            </div>
          </article>
        </div>
      </section>

      <section id="home-flow" class="resource-section" data-testid="home-core-flow">
        <h2 class="resource-section__title">{{ t('home.flow.title') }}</h2>
        <ol class="home-flow">
          <li class="home-flow__item">
            <strong>{{ t('home.flow.projectTitle') }}</strong>
            <span>{{ t('home.flow.projectDescription') }}</span>
          </li>
          <li class="home-flow__item">
            <strong>{{ t('home.flow.campaignTitle') }}</strong>
            <span>{{ t('home.flow.campaignDescription') }}</span>
          </li>
          <li class="home-flow__item">
            <strong>{{ t('home.flow.deviceProfileTitle') }}</strong>
            <span>{{ t('home.flow.deviceProfileDescription') }}</span>
          </li>
          <li class="home-flow__item">
            <strong>{{ t('home.flow.taskTitle') }}</strong>
            <span>{{ t('home.flow.taskDescription') }}</span>
          </li>
          <li class="home-flow__item">
            <strong>{{ t('home.flow.feedbackTitle') }}</strong>
            <span>{{ t('home.flow.feedbackDescription') }}</span>
          </li>
        </ol>
      </section>

      <section class="resource-section" data-testid="home-trust-section">
        <h2 class="resource-section__title">{{ t('home.safety.title') }}</h2>
        <div class="home-grid">
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">{{ t('home.safety.safetyFirstTitle') }}</h3>
            <ul class="home-list">
              <li>{{ t('home.safety.safetyItemOfficial') }}</li>
              <li>{{ t('home.safety.safetyItemUnknownSource') }}</li>
              <li>{{ t('home.safety.safetyItemDeviceSecurity') }}</li>
            </ul>
          </div>
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">{{ t('home.safety.trustTitle') }}</h3>
            <p class="home-summary-card__description">
              {{ t('home.safety.trustDescription') }}
            </p>
          </div>
        </div>
      </section>

      <section class="resource-section home-final-cta" data-testid="home-final-cta">
        <h2 class="resource-section__title">{{ t('home.guest.final.title') }}</h2>
        <p class="resource-section__description">
          {{ t('home.guest.final.description') }}
        </p>

        <div class="home-final-cta__actions">
          <NuxtLink class="resource-action" data-testid="home-final-login-link" to="/login">
            {{ t('home.guest.final.login') }}
          </NuxtLink>
          <NuxtLink class="resource-action" data-testid="home-final-register-link" to="/register">
            {{ t('home.guest.final.register') }}
          </NuxtLink>
        </div>

        <section
          v-if="showLocalFallbackNote"
          class="resource-state"
          data-testid="home-entry-fallback-note"
        >
          <h3 class="resource-state__title">{{ t('home.guest.fallbackTitle') }}</h3>
          <p class="resource-state__description">
            {{ t('home.guest.fallbackDescription') }}
          </p>
        </section>
      </section>
    </section>
  </main>
</template>

<style scoped lang="scss">
.home-landing-hero {
  gap: 1rem;
}

.public-home__panel {
  width: min(100%, var(--resource-max-width));
  margin: 0 auto;
}

.home-landing-hero__grid {
  display: grid;
  gap: 1.25rem;
  align-items: center;
}

.home-landing-hero__copy {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.home-hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.home-brand-hero {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 0;
}

.home-brand-hero__frame {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-accent-medium);
  border-radius: 1.75rem;
  background:
    radial-gradient(circle at top left, rgba(124, 190, 255, 0.2), transparent 42%),
    radial-gradient(circle at bottom right, rgba(120, 228, 198, 0.18), transparent 38%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(231, 240, 252, 0.88));
  box-shadow: var(--shadow-strong);
}

.home-brand-hero__image,
.home-visual-panel__image {
  display: block;
  width: 100%;
  height: auto;
}

.home-brand-hero__callout {
  position: absolute;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.home-brand-hero__callout--top {
  top: 1rem;
  left: 1rem;
}

.home-brand-hero__callout--bottom {
  right: 1rem;
  bottom: 1rem;
  justify-content: flex-end;
}

.home-brand-hero__caption {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.home-guest-grid,
.home-entry-grid,
.home-visual-story-grid,
.home-grid {
  display: grid;
  gap: 1rem;
}

.home-visual-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-soft);
  border-radius: 1.5rem;
  background: var(--surface-card-strong);
  box-shadow: var(--shadow-soft);
}

.home-visual-panel__figure {
  overflow: hidden;
  margin: 0;
  border: 1px solid var(--border-accent);
  border-radius: 1.25rem;
  background:
    radial-gradient(circle at top left, rgba(124, 190, 255, 0.15), transparent 40%),
    linear-gradient(160deg, rgba(255, 255, 255, 0.96), rgba(236, 244, 253, 0.88));
}

.home-visual-panel__body {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
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
    color: var(--color-text-muted);
    line-height: 1.7;
  }
}

.home-final-cta {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.home-final-cta__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.home-list {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--color-text-muted);
  line-height: 1.8;
}

.home-flow {
  display: grid;
  gap: 0.85rem;
  margin: 0;
  padding-left: 1.25rem;
}

.home-flow__item {
  color: var(--color-text-muted);
  line-height: 1.7;

  strong {
    color: var(--color-text-primary);
    margin-right: 0.4rem;
  }
}

:global(:root[data-theme='dark']) .home-brand-hero__frame,
:global(:root[data-theme='dark']) .home-visual-panel__figure {
  background:
    radial-gradient(circle at top left, rgba(118, 186, 255, 0.18), transparent 40%),
    radial-gradient(circle at bottom right, rgba(123, 242, 211, 0.14), transparent 34%),
    linear-gradient(155deg, rgba(13, 24, 42, 0.98), rgba(8, 18, 32, 0.9));
}

@media (min-width: 768px) {
  .home-landing-hero__grid {
    grid-template-columns: minmax(0, 1.05fr) minmax(20rem, 0.95fr);
  }

  .home-guest-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .home-entry-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-items: stretch;
  }

  .home-visual-story-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .home-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
