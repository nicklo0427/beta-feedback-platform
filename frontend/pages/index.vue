<script setup lang="ts">
import { computed, ref } from 'vue'

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

type TrustSignalKey = 'notShortcut' | 'safetyFirst' | 'platforms'

interface TrustSignalConfig {
  key: TrustSignalKey
  imageSrc: string
  detailKeys: string[]
  chipKeys: string[]
}

type RoleValueKey = 'developer' | 'tester'

interface RoleValueConfig {
  key: RoleValueKey
  imageSrc: string
  registerHref: string
  bulletKeys: readonly string[]
}

const TRUST_SIGNAL_CONFIGS: TrustSignalConfig[] = [
  {
    key: 'notShortcut',
    imageSrc: '/brand/professional-signal-not-shortcut.webp',
    detailKeys: [
      'home.trust.nonGoals.ratingFarm',
      'home.trust.nonGoals.reviewExchange',
      'home.trust.nonGoals.trafficBoost'
    ],
    chipKeys: []
  },
  {
    key: 'safetyFirst',
    imageSrc: '/brand/professional-signal-safety-first.webp',
    detailKeys: [
      'home.trust.signals.safetyFirst.details.officialChannels',
      'home.trust.signals.safetyFirst.details.sourceTrace',
      'home.trust.signals.safetyFirst.details.reviewDecision'
    ],
    chipKeys: []
  },
  {
    key: 'platforms',
    imageSrc: '/brand/professional-signal-platforms.webp',
    detailKeys: [
      'home.trust.signals.platforms.details.web',
      'home.trust.signals.platforms.details.mobile',
      'home.trust.signals.platforms.details.games'
    ],
    chipKeys: [
      'home.trust.platformChipWeb',
      'home.trust.platformChipIos',
      'home.trust.platformChipAndroid'
    ]
  }
]

const activeTrustSignal = ref<TrustSignalKey>('notShortcut')

const selectTrustSignal = (signalKey: TrustSignalKey) => {
  activeTrustSignal.value = signalKey
}

const selectAdjacentTrustSignal = (direction: 1 | -1) => {
  const activeIndex = TRUST_SIGNAL_CONFIGS.findIndex((signal) => signal.key === activeTrustSignal.value)
  const nextIndex = (activeIndex + direction + TRUST_SIGNAL_CONFIGS.length) % TRUST_SIGNAL_CONFIGS.length

  activeTrustSignal.value = TRUST_SIGNAL_CONFIGS[nextIndex].key
}

const trustSignalItems = computed(() =>
  TRUST_SIGNAL_CONFIGS.map((signal) => ({
    ...signal,
    label: t(`home.trust.signals.${signal.key}.label`),
    title: t(`home.trust.signals.${signal.key}.title`),
    summary: t(`home.trust.signals.${signal.key}.summary`),
    imageAlt: t(`home.trust.signals.${signal.key}.imageAlt`)
  }))
)

const activeTrustSignalItem = computed(
  () => trustSignalItems.value.find((signal) => signal.key === activeTrustSignal.value) ?? trustSignalItems.value[0]
)

const PRODUCT_FLOW_STAGES = [
  {
    key: 'create',
    imageSrc: '/brand/product-flow-stage-create.webp'
  },
  {
    key: 'invite',
    imageSrc: '/brand/product-flow-stage-invite.webp'
  },
  {
    key: 'learn',
    imageSrc: '/brand/product-flow-stage-learn.webp'
  }
] as const

const ROLE_VALUE_CONFIGS: RoleValueConfig[] = [
  {
    key: 'developer',
    imageSrc: '/brand/role-value-developer.webp',
    registerHref: '/register?role=developer',
    bulletKeys: ['launch', 'match', 'organize']
  },
  {
    key: 'tester',
    imageSrc: '/brand/role-value-tester.webp',
    registerHref: '/register?role=tester',
    bulletKeys: ['discover', 'join', 'respond']
  }
]
</script>

<template>
  <main class="app-shell public-home" :data-locale="locale">
    <section class="app-panel public-home__panel">
      <section class="resource-section home-landing-hero" data-testid="home-guest-hero">
        <div class="home-landing-hero__grid">
          <div class="home-landing-hero__copy">
            <h1 class="app-title home-hero-title">
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
:src="'/brand/hero-people-collaboration.webp'"
                :alt="t('home.guest.visuals.heroAlt')"
>
              <div class="home-brand-hero__callout home-brand-hero__callout--bottom">
                <span class="resource-shell__meta-chip">{{ t('home.guest.proof.workflow') }}</span>
                <span class="resource-shell__meta-chip">{{ t('home.guest.proof.crossPlatform') }}</span>
              </div>
            </div>
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
            <figure class="home-visual-panel__figure home-visual-panel__figure--stacked">
              <img
                v-for="signal in trustSignalItems"
                :key="signal.key"
                class="home-visual-panel__image home-visual-panel__image--stacked"
                :class="{ 'home-visual-panel__image--active': activeTrustSignal === signal.key }"
                :src="signal.imageSrc"
                :alt="activeTrustSignal === signal.key ? signal.imageAlt : ''"
                :aria-hidden="activeTrustSignal !== signal.key"
                :data-testid="activeTrustSignal === signal.key ? 'home-trust-signal-image' : undefined"
                :fetchpriority="signal.key === 'notShortcut' ? 'high' : 'auto'"
                loading="eager"
              >
            </figure>
          </article>

          <div class="home-trust-tabs" data-testid="home-trust-tabs">
            <div class="home-trust-tabs__list" role="tablist" :aria-label="t('home.trust.eyebrow')">
              <button v-for="signal in trustSignalItems" :id="`home-trust-tab-${signal.key}`" :key="signal.key"
                class="home-trust-tabs__tab"
                :class="{ 'home-trust-tabs__tab--active': activeTrustSignal === signal.key }" type="button" role="tab"
                :aria-selected="activeTrustSignal === signal.key" :aria-controls="`home-trust-panel-${signal.key}`"
                :tabindex="activeTrustSignal === signal.key ? 0 : -1" :data-testid="`home-trust-signal-${signal.key}`"
                @click="selectTrustSignal(signal.key)" @keydown.left.prevent="selectAdjacentTrustSignal(-1)"
                @keydown.right.prevent="selectAdjacentTrustSignal(1)">
                {{ signal.label }}
              </button>
            </div>

            <section :id="`home-trust-panel-${activeTrustSignalItem.key}`" class="home-trust-tabs__panel"
              role="tabpanel" :aria-labelledby="`home-trust-tab-${activeTrustSignalItem.key}`"
              :data-testid="`home-trust-panel-${activeTrustSignalItem.key}`">
              <strong class="summary-stat-card__value">{{ activeTrustSignalItem.title }}</strong>
              <p class="home-summary-card__description">{{ activeTrustSignalItem.summary }}</p>

              <ul v-if="activeTrustSignalItem.detailKeys.length > 1" class="home-list"
                :data-testid="activeTrustSignalItem.key === 'notShortcut' ? 'home-non-goals' : `home-trust-details-${activeTrustSignalItem.key}`">
                <li v-for="detailKey in activeTrustSignalItem.detailKeys" :key="detailKey">
                  {{ t(detailKey) }}
                </li>
              </ul>
              <p v-else class="home-summary-card__description">
                {{ t(activeTrustSignalItem.detailKeys[0]) }}
              </p>
              <div v-if="activeTrustSignalItem.chipKeys.length > 0" class="resource-shell__meta">
                <span v-for="chipKey in activeTrustSignalItem.chipKeys" :key="chipKey"
                  class="resource-shell__meta-chip">
                  {{ t(chipKey) }}
                </span>
              </div>
            </section>
          </div>
        </div>
      </section>

      <section id="home-flow" class="resource-section home-product-flow" data-testid="home-product-flow-section">
        <div class="home-section-heading">
          <p class="app-eyebrow">{{ t('home.flow.eyebrow') }}</p>
          <h2 class="resource-section__title">{{ t('home.flow.title') }}</h2>
          <p class="resource-section__description">{{ t('home.flow.description') }}</p>
        </div>

        <div class="home-flow-story">
          <div class="home-flow-sequence">
            <article v-for="(stage, index) in PRODUCT_FLOW_STAGES" :key="stage.key" class="home-flow-card"
              :data-testid="`home-flow-stage-${stage.key}`">
              <figure class="home-flow-card__visual">
                <img class="home-flow-card__image" :src="stage.imageSrc"
                  :alt="t(`home.flow.stages.${stage.key}.imageAlt`)" :data-testid="`home-flow-stage-image-${stage.key}`"
                  loading="lazy">
              </figure>
              <span class="home-flow-card__step">{{ String(index + 1).padStart(2, '0') }}</span>
              <strong class="home-flow-card__title">{{ t(`home.flow.stages.${stage.key}.title`) }}</strong>
              <p class="home-flow-card__description">{{ t(`home.flow.stages.${stage.key}.description`) }}</p>
            </article>
          </div>

          <div class="home-flow-outcome">
            <span class="shell-link-label">{{ t('home.flow.outcomeLabel') }}</span>
            <strong class="shell-link-title">{{ t('home.flow.outcomeTitle') }}</strong>
            <p class="shell-link-description">{{ t('home.flow.outcomeDescription') }}</p>
          </div>
        </div>
      </section>

      <section class="resource-section home-role-value" data-testid="home-role-value-section">
        <div class="home-section-heading">
          <p class="app-eyebrow">{{ t('home.roles.eyebrow') }}</p>
          <h2 class="resource-section__title">{{ t('home.roles.title') }}</h2>
          <p class="resource-section__description">{{ t('home.roles.description') }}</p>
        </div>

        <div class="home-role-grid">
          <article v-for="role in ROLE_VALUE_CONFIGS" :key="role.key" class="home-role-card"
            :data-testid="`home-role-card-${role.key}`">
            <div class="home-role-card__body">
              <span class="resource-shell__meta-chip home-role-card__chip">
                {{ t(`home.roles.items.${role.key}.label`) }}
              </span>
              <h3 class="home-role-card__title">{{ t(`home.roles.items.${role.key}.title`) }}</h3>
              <p class="home-role-card__description">{{ t(`home.roles.items.${role.key}.description`) }}</p>
            </div>

            <figure class="home-role-card__visual">
              <img
class="home-role-card__image" :src="role.imageSrc" :alt="t(`home.roles.items.${role.key}.imageAlt`)"
                :data-testid="`home-role-image-${role.key}`"
                loading="lazy"
              >
            </figure>

            <ul class="home-role-card__list">
              <li v-for="bulletKey in role.bulletKeys" :key="`${role.key}-${bulletKey}`">
                {{ t(`home.roles.items.${role.key}.bullets.${bulletKey}`) }}
              </li>
            </ul>

            <NuxtLink class="resource-action home-role-card__action" :data-testid="`home-role-cta-${role.key}`"
              :to="role.registerHref">
              {{ t(`home.roles.items.${role.key}.cta`) }}
            </NuxtLink>
          </article>
        </div>

        <div class="home-role-handoff" data-testid="home-role-handoff">
          <span class="shell-link-label">{{ t('home.roles.handoffLabel') }}</span>
          <strong class="shell-link-title">{{ t('home.roles.handoffTitle') }}</strong>
          <p class="shell-link-description">{{ t('home.roles.handoffDescription') }}</p>
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
  gap: clamp(1.25rem, 3vw, 2.4rem);
  align-items: center;
}

.home-landing-hero__copy {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  max-width: 34rem;
}

.home-landing-hero__copy .app-eyebrow {
  max-width: fit-content;
  padding: 0.18rem 0.58rem;
  border: 1px solid var(--border-accent);
  border-radius: var(--radius-pill);
  background: var(--surface-chip);
  font-size: clamp(0.58rem, 0.8vw, 0.68rem);
  letter-spacing: 0.12em;
}

.home-hero-title {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: clamp(2rem, 3.4vw, 3.45rem);
  line-height: 1.08;
}

.home-hero-title__promise {
  display: block;
  max-width: 13ch;
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
  min-height: clamp(19rem, 36vw, 28rem);
}

.home-brand-hero__image,
.home-visual-panel__image {
  display: block;
  width: 100%;
  height: 100%;
    object-fit: cover;
    object-position: center;
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
.home-role-grid {
  display: grid;
  gap: 1rem;
}

.home-trust-tabs {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.home-trust-tabs__list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  padding: 0.35rem;
  border: 1px solid var(--border-soft-alt);
  border-radius: var(--radius-pill);
  background: var(--surface-card);
  box-shadow: var(--shadow-soft);
}

.home-trust-tabs__tab {
  flex: 1 1 8rem;
  min-height: 2.6rem;
  padding: 0.65rem 0.9rem;
  border: 1px solid transparent;
  border-radius: var(--radius-pill);
  background: transparent;
  color: var(--color-text-muted);
  font: inherit;
  font-size: 0.86rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-align: center;
  cursor: pointer;
  transition:
    background var(--transition-fast),
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    color var(--transition-fast);

  &:hover {
    background: var(--surface-chip);
    color: var(--color-text-primary);
  }

  &:focus-visible {
    outline: 3px solid var(--color-focus-ring);
    outline-offset: 2px;
  }
}

.home-trust-tabs__tab--active {
  border-color: var(--border-accent-medium);
  background: var(--surface-card-strong);
  color: var(--color-text-primary);
  box-shadow: var(--shadow-soft);
}

.home-trust-tabs__panel {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1.1rem;
  border: 1px solid var(--border-soft-alt);
  border-radius: 1.35rem;
  background: var(--surface-card-strong);
  box-shadow: var(--shadow-soft);
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
  min-height: clamp(15rem, 30vw, 21rem);
}

.home-visual-panel__figure--stacked {
  position: relative;
  isolation: isolate;
}

.home-visual-panel__body {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.home-visual-panel__image--stacked {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 180ms ease;
  will-change: opacity;
}

.home-visual-panel__image--active {
  opacity: 1;
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

.home-flow-story {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.home-flow-sequence {
  display: grid;
  gap: 1rem;
}

.home-flow-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
    padding: 1rem;
  border: 1px solid var(--border-soft-alt);
  border-radius: 1.35rem;
  background: var(--surface-card-strong);
  box-shadow: var(--shadow-soft);
}

.home-flow-card__visual {
  overflow: hidden;
  margin: 0;
  border: 1px solid var(--border-accent);
  border-radius: 1.1rem;
  background:
    radial-gradient(circle at top left, rgba(124, 190, 255, 0.18), transparent 40%),
    linear-gradient(160deg, rgba(255, 255, 255, 0.96), rgba(236, 244, 253, 0.88));
}

.home-flow-card__image {
  display: block;
  width: 100%;
  aspect-ratio: 3 / 2;
  object-fit: cover;
  object-position: center;
}
.home-flow-card__step {
  display: inline-grid;
    width: 2.45rem;
    height: 2.45rem;
    place-items: center;
    border: 1px solid var(--border-accent);
    border-radius: 50%;
    background:
      radial-gradient(circle at 35% 25%, rgba(255, 255, 255, 0.95), transparent 46%),
      linear-gradient(145deg, rgba(124, 190, 255, 0.22), rgba(120, 228, 198, 0.2));
  color: var(--color-accent-soft);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.08em;
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

.home-role-value {
  gap: 1.15rem;
}

.home-role-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.1rem;
  border: 1px solid var(--border-soft-alt);
  border-radius: 1.45rem;
  background: var(--surface-card-strong);
  box-shadow: var(--shadow-soft);
}

.home-role-card__body {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.home-role-card__chip {
  width: fit-content;
}

.home-role-card__title {
  margin: 0;
  font-size: 1.16rem;
  line-height: 1.4;
}

.home-role-card__description {
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.72;
}

.home-role-card__visual {
  overflow: hidden;
  margin: 0;
  border: 1px solid var(--border-accent);
  border-radius: 1.15rem;
  background:
    radial-gradient(circle at top left, rgba(124, 190, 255, 0.18), transparent 40%),
    linear-gradient(160deg, rgba(255, 255, 255, 0.96), rgba(236, 244, 253, 0.88));
}

.home-role-card__image {
  display: block;
  width: 100%;
  aspect-ratio: 3 / 2;
  object-fit: cover;
  object-position: center;
}

.home-role-card__list {
  display: grid;
  gap: 0.65rem;
  margin: 0;
  padding-left: 1.15rem;
  color: var(--color-text-muted);
  line-height: 1.7;
}

.home-role-card__action {
  align-self: flex-start;
  margin-top: auto;
}

.home-role-handoff {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  padding: 1.05rem 1.15rem;
  border: 1px solid var(--border-accent);
  border-radius: 1.35rem;
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
:global(:root[data-theme='dark']) .home-visual-panel__figure,
:global(:root[data-theme='dark']) .home-flow-card__visual {
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

:global(:root[data-theme='dark']) .home-role-card__visual,
:global(:root[data-theme='dark']) .home-role-handoff {
  background:
    radial-gradient(circle at top left, rgba(118, 186, 255, 0.18), transparent 40%),
    radial-gradient(circle at bottom right, rgba(123, 242, 211, 0.14), transparent 34%),
    linear-gradient(155deg, rgba(13, 24, 42, 0.98), rgba(8, 18, 32, 0.9));
}
@media (min-width: 768px) {
  .home-landing-hero__grid {
    grid-template-columns: minmax(0, 0.8fr) minmax(28rem, 1.2fr);
  }

  .home-trust-proof__grid {
    grid-template-columns: minmax(0, 1.02fr) minmax(0, 0.98fr);
  }

  .home-flow-sequence {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .home-role-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-items: stretch;
  }

  .home-role-card__body {
    min-block-size: 10.75rem;
  }
}

@media (max-width: 767px) {
  .home-hero-title {
    font-size: clamp(1.85rem, 8vw, 2.45rem);
  }

  .home-brand-hero__frame {
    min-height: 17.5rem;
  }

  .home-visual-panel__figure {
    min-height: 14rem;
  }

  .home-brand-hero__image {
    object-position: center top;
  }
}
</style>
