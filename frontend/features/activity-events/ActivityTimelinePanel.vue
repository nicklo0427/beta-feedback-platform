<script setup lang="ts">
import { computed } from 'vue'

import { useAppI18n } from '~/features/i18n/use-app-i18n'
import type { ActivityEventItem } from './types'

const props = withDefaults(defineProps<{
  title: string
  description: string
  pending: boolean
  errorMessage?: string | null
  events?: ActivityEventItem[] | null
  emptyMessage?: string
  testIdPrefix: string
}>(), {
  errorMessage: null,
  events: () => [],
  emptyMessage: undefined
})

const { t } = useAppI18n()
const items = computed(() => props.events ?? [])
const resolvedEmptyMessage = computed(
  () => props.emptyMessage || t('timeline.emptyTitle')
)
</script>

<template>
  <section
    class="resource-section"
    :data-testid="`${testIdPrefix}-panel`"
  >
    <h2 class="resource-section__title">{{ title }}</h2>
    <p class="resource-section__description">{{ description }}</p>

    <section
      v-if="pending"
      class="resource-state"
      :data-testid="`${testIdPrefix}-loading`"
    >
      <h3 class="resource-state__title">{{ t('timeline.loadingTitle') }}</h3>
      <p class="resource-state__description">
        {{ t('timeline.loadingDescription') }}
      </p>
    </section>

    <section
      v-else-if="errorMessage"
      class="resource-state"
      :data-testid="`${testIdPrefix}-error`"
    >
      <h3 class="resource-state__title">{{ t('timeline.errorTitle') }}</h3>
      <p class="resource-state__description">{{ errorMessage }}</p>
    </section>

    <section
      v-else-if="!items.length"
      class="resource-state"
      :data-testid="`${testIdPrefix}-empty`"
    >
      <h3 class="resource-state__title">{{ t('timeline.emptyTitle') }}</h3>
      <p class="resource-state__description">{{ resolvedEmptyMessage }}</p>
    </section>

    <section
      v-else
      class="timeline-list"
      :data-testid="`${testIdPrefix}-list`"
    >
      <article
        v-for="event in items"
        :key="event.id"
        class="timeline-list__item"
        :data-testid="`${testIdPrefix}-event-${event.id}`"
      >
        <span class="timeline-list__eyebrow">{{ t('timeline.eyebrow') }}</span>
        <h3 class="resource-section__title">{{ event.summary }}</h3>
        <div class="resource-card__meta">
          <span class="resource-card__chip">
            {{ t('timeline.actorLabel') }} {{ event.actor_account_display_name || event.actor_account_id }}
          </span>
          <span class="resource-card__chip">{{ t('timeline.occurredAtLabel') }} {{ event.created_at }}</span>
        </div>
      </article>
    </section>
  </section>
</template>
