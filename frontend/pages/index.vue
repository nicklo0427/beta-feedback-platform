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
            <h1 class="app-title home-hero-title">
              <span class="home-hero-title__brand">beta-feedback-platform</span>
              <span class="home-hero-title__promise">{{ t('home.guest.promiseTitle') }}</span>
            </h1>
            <p class="app-description">
              {{ t('home.guest.description') }}
            </p>
            <p class="home-hero-flow-hint">
              {{ t('home.guest.flowHint') }}
            </p>

            <div class="home-hero-actions">
              <NuxtLink
                class="resource-action"
                data-testid="home-guest-register-link"
                to="/register"
              >
                {{ t('home.guest.actions.register') }}
              </NuxtLink>
              <NuxtLink
                class="resource-action resource-action--quiet"
                data-testid="home-guest-login-link"
                to="/login"
              >
                {{ t('home.guest.actions.login') }}
              </NuxtLink>
              <a
                class="resource-action resource-action--quiet"
                data-testid="home-guest-flow-link"
                href="#home-flow"
              >
                {{ t('home.guest.actions.learnMore') }}
              </a>
            </div>

            <div class="home-hero-proof">
              <span class="resource-shell__meta-chip">{{ t('home.guest.proof.workflow') }}</span>
              <span class="resource-shell__meta-chip">{{ t('home.guest.proof.review') }}</span>
              <span class="resource-shell__meta-chip">{{ t('home.guest.proof.crossPlatform') }}</span>
            </div>
          </div>

          <figure class="home-brand-hero" data-testid="home-guest-visual">
            <div class="home-brand-hero__frame">
              <img
                class="home-brand-hero__image"
                :src="'/brand/t092-hero-beta-ops-scene.svg'"
                :alt="t('home.guest.visuals.heroAlt')"
              >
              <div class="home-brand-hero__callout home-brand-hero__callout--top">
                <span class="resource-shell__meta-chip">{{ t('home.guest.visuals.heroLabel') }}</span>
              </div>
              <div class="home-brand-hero__callout home-brand-hero__callout--bottom">
                <span class="resource-shell__meta-chip">{{ t('home.guest.proof.workflow') }}</span>
                <span class="resource-shell__meta-chip">{{ t('home.guest.proof.crossPlatform') }}</span>
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
      </section>

      <section class="resource-section home-trust-proof" data-testid="home-trust-proof-section">
        <div class="home-section-heading">
          <p class="app-eyebrow">{{ t('home.trust.eyebrow') }}</p>
          <h2 class="resource-section__title">{{ t('home.trust.title') }}</h2>
          <p class="resource-section__description">
            {{ t('home.trust.description') }}
          </p>
        </div>

        <div class="home-trust-proof__grid">
          <article class="home-visual-panel" data-testid="home-supporting-visual-review">
            <figure class="home-visual-panel__figure">
              <img
                class="home-visual-panel__image"
                :src="'/brand/t092-trust-operations-scene.svg'"
                :alt="t('home.trust.visualAlt')"
                loading="lazy"
              >
            </figure>
            <div class="home-visual-panel__body">
              <span class="shell-link-label">{{ t('home.trust.visualLabel') }}</span>
              <strong class="shell-link-title">{{ t('home.trust.visualTitle') }}</strong>
              <p class="shell-link-description">{{ t('home.trust.visualDescription') }}</p>
            </div>
          </article>

          <div class="home-trust-proof__cards">
            <article class="summary-stat-card">
              <span class="summary-stat-card__label">{{ t('home.trust.cards.notWhatLabel') }}</span>
              <strong class="summary-stat-card__value">{{ t('home.trust.cards.notWhatValue') }}</strong>
              <ul class="home-list" data-testid="home-non-goals">
                <li>{{ t('home.trust.nonGoals.ratingFarm') }}</li>
                <li>{{ t('home.trust.nonGoals.reviewExchange') }}</li>
                <li>{{ t('home.trust.nonGoals.trafficBoost') }}</li>
              </ul>
            </article>
            <article class="summary-stat-card">
              <span class="summary-stat-card__label">{{ t('home.trust.cards.safetyLabel') }}</span>
              <strong class="summary-stat-card__value">{{ t('home.trust.cards.safetyValue') }}</strong>
              <p class="home-summary-card__description">
                {{ t('home.trust.cards.safetyDescription') }}
              </p>
            </article>
            <article class="summary-stat-card">
              <span class="summary-stat-card__label">{{ t('home.trust.cards.platformsLabel') }}</span>
              <strong class="summary-stat-card__value">{{ t('home.trust.cards.platformsValue') }}</strong>
              <div class="resource-shell__meta">
                <span class="resource-shell__meta-chip">{{ t('home.trust.platformChipWeb') }}</span>
                <span class="resource-shell__meta-chip">{{ t('home.trust.platformChipIos') }}</span>
                <span class="resource-shell__meta-chip">{{ t('home.trust.platformChipAndroid') }}</span>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section id="home-flow" class="resource-section home-product-flow" data-testid="home-product-flow-section">
        <div class="home-section-heading">
          <p class="app-eyebrow">{{ t('home.flow.eyebrow') }}</p>
          <h2 class="resource-section__title">{{ t('home.flow.title') }}</h2>
          <p class="resource-section__description">{{ t('home.flow.description') }}</p>
        </div>

        <div class="home-flow-sequence">
          <article class="home-flow-card">
            <span class="home-flow-card__step">01</span>
            <strong class="home-flow-card__title">{{ t('home.flow.projectTitle') }}</strong>
            <p class="home-flow-card__description">{{ t('home.flow.projectDescription') }}</p>
          </article>
          <article class="home-flow-card">
            <span class="home-flow-card__step">02</span>
            <strong class="home-flow-card__title">{{ t('home.flow.campaignTitle') }}</strong>
            <p class="home-flow-card__description">{{ t('home.flow.campaignDescription') }}</p>
          </article>
          <article class="home-flow-card">
            <span class="home-flow-card__step">03</span>
            <strong class="home-flow-card__title">{{ t('home.flow.deviceProfileTitle') }}</strong>
            <p class="home-flow-card__description">{{ t('home.flow.deviceProfileDescription') }}</p>
          </article>
          <article class="home-flow-card">
            <span class="home-flow-card__step">04</span>
            <strong class="home-flow-card__title">{{ t('home.flow.taskTitle') }}</strong>
            <p class="home-flow-card__description">{{ t('home.flow.taskDescription') }}</p>
          </article>
          <article class="home-flow-card">
            <span class="home-flow-card__step">05</span>
            <strong class="home-flow-card__title">{{ t('home.flow.feedbackTitle') }}</strong>
            <p class="home-flow-card__description">{{ t('home.flow.feedbackDescription') }}</p>
          </article>
        </div>

        <div class="home-flow-outcome">
          <span class="shell-link-label">{{ t('home.flow.outcomeLabel') }}</span>
          <strong class="shell-link-title">{{ t('home.flow.outcomeTitle') }}</strong>
          <p class="shell-link-description">{{ t('home.flow.outcomeDescription') }}</p>
        </div>
      </section>

      <section class="resource-section home-role-value" data-testid="home-role-value-section">
        <div class="home-section-heading">
          <p class="app-eyebrow">{{ t('home.roles.eyebrow') }}</p>
          <h2 class="resource-section__title">{{ t('home.roles.title') }}</h2>
          <p class="resource-section__description">{{ t('home.roles.description') }}</p>
        </div>

        <div class="home-role-grid">
          <article class="summary-stat-card">
            <span class="summary-stat-card__label">{{ t('home.roles.developerLabel') }}</span>
            <strong class="summary-stat-card__value">{{ t('home.roles.developerValue') }}</strong>
            <p class="home-summary-card__description">{{ t('home.roles.developerDescription') }}</p>
          </article>
          <article class="summary-stat-card">
            <span class="summary-stat-card__label">{{ t('home.roles.testerLabel') }}</span>
            <strong class="summary-stat-card__value">{{ t('home.roles.testerValue') }}</strong>
            <p class="home-summary-card__description">{{ t('home.roles.testerDescription') }}</p>
          </article>
          <article class="home-visual-panel home-visual-panel--role" data-testid="home-supporting-visual-tester">
            <figure class="home-visual-panel__figure">
              <img
                class="home-visual-panel__image"
                :src="'/brand/t092-role-participation-scene.svg'"
                :alt="t('home.roles.visualAlt')"
                loading="lazy"
              >
            </figure>
            <div class="home-visual-panel__body">
              <span class="shell-link-label">{{ t('home.roles.visualLabel') }}</span>
              <strong class="shell-link-title">{{ t('home.roles.visualTitle') }}</strong>
              <p class="shell-link-description">{{ t('home.roles.visualDescription') }}</p>
            </div>
          </article>
        </div>
      </section>

      <section class="resource-section home-final-cta" data-testid="home-final-cta">
        <h2 class="resource-section__title">{{ t('home.guest.final.title') }}</h2>
        <p class="resource-section__description">
          {{ t('home.guest.final.description') }}
        </p>

        <div class="home-final-cta__actions">
          <NuxtLink class="resource-action" data-testid="home-final-register-link" to="/register">
            {{ t('home.guest.final.register') }}
          </NuxtLink>
          <NuxtLink
            class="resource-action resource-action--quiet"
            data-testid="home-final-login-link"
            to="/login"
          >
            {{ t('home.guest.final.login') }}
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
  gap: 1.2rem;
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

.home-hero-title {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.home-hero-title__brand {
  display: block;
}

.home-hero-title__promise {
  display: block;
  max-width: 12ch;
}

.home-hero-flow-hint {
  max-width: 42rem;
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 1rem;
  line-height: 1.75;
}

.home-hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.home-hero-proof {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
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

.home-section-heading {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.home-trust-proof__grid,
.home-trust-proof__cards,
.home-role-grid {
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

.home-product-flow {
  gap: 1.15rem;
}

.home-flow-sequence {
  display: grid;
  gap: 0.95rem;
}

.home-flow-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  padding: 1.1rem;
  border: 1px solid var(--border-soft-alt);
  border-radius: 1.35rem;
  background: var(--surface-card-strong);
  box-shadow: var(--shadow-soft);
}

.home-flow-card__step {
  color: var(--color-accent-soft);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.home-flow-card__title {
  color: var(--color-text-primary);
  font-size: 1.02rem;
}

.home-flow-card__description {
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.7;
}

.home-flow-outcome {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  padding: 1.1rem 1.2rem;
  border: 1px solid var(--border-accent);
  border-radius: 1.5rem;
  background:
    radial-gradient(circle at top right, rgba(124, 190, 255, 0.12), transparent 32%),
    linear-gradient(160deg, rgba(255, 255, 255, 0.94), rgba(236, 244, 253, 0.82));
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

:global(:root[data-theme='dark']) .home-flow-outcome {
  background:
    radial-gradient(circle at top right, rgba(118, 186, 255, 0.14), transparent 32%),
    linear-gradient(160deg, rgba(10, 19, 34, 0.95), rgba(8, 16, 30, 0.88));
}

@media (min-width: 768px) {
  .home-landing-hero__grid {
    grid-template-columns: minmax(0, 1.06fr) minmax(24rem, 0.94fr);
  }

  .home-trust-proof__grid {
    grid-template-columns: minmax(0, 1.02fr) minmax(0, 0.98fr);
  }

  .home-trust-proof__cards {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-content: start;
  }

  .home-flow-sequence {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }

  .home-role-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    align-items: stretch;
  }

  .home-visual-panel--role {
    grid-column: span 1;
  }
}
</style>
