<script setup lang="ts">
import { computed } from 'vue'

import { fetchDeviceProfileDetail } from '~/features/device-profiles/api'
import { formatPlatformLabel } from '~/features/platform-display'
import { fetchDeviceProfileReputation } from '~/features/reputation/api'

const route = useRoute()
const deviceProfileId = computed(() => String(route.params.deviceProfileId))

const {
  data: deviceProfile,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `device-profile-detail-${deviceProfileId.value}`,
  () => fetchDeviceProfileDetail(deviceProfileId.value),
  {
    server: false,
    watch: [deviceProfileId],
    default: () => null
  }
)

const {
  data: reputation,
  pending: reputationPending,
  error: reputationError,
  refresh: refreshReputation
} = useAsyncData(
  () => `device-profile-reputation-${deviceProfileId.value}`,
  () => fetchDeviceProfileReputation(deviceProfileId.value),
  {
    server: false,
    watch: [deviceProfileId],
    default: () => null
  }
)

const hasReputationSignals = computed(() => {
  if (!reputation.value) {
    return false
  }

  return (
    reputation.value.tasks_assigned_count > 0
    || reputation.value.tasks_submitted_count > 0
    || reputation.value.feedback_submitted_count > 0
    || reputation.value.last_feedback_at !== null
  )
})
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/device-profiles">
          Device Profiles
        </NuxtLink>
        <h1 class="resource-shell__title">Device Profile Detail Shell</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一 Tester Device Profile 的核心欄位，提供後續 eligibility、task 與 feedback 流程可依附的裝置上下文。
        </p>
        <div
          v-if="deviceProfile"
          class="resource-state__actions"
        >
          <NuxtLink
            class="resource-action"
            data-testid="device-profile-edit-link"
            :to="`/device-profiles/${deviceProfile.id}/edit`"
          >
            Edit device profile
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="device-profile-detail-loading"
      >
        <h2 class="resource-state__title">Loading device profile detail</h2>
        <p class="resource-state__description">
          正在從 API 載入 Tester Device Profile detail。
        </p>
      </section>

      <section
        v-else-if="error || !deviceProfile"
        class="resource-state"
        data-testid="device-profile-detail-error"
      >
        <h2 class="resource-state__title">Device profile detail unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested device profile could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
          <NuxtLink class="resource-action" to="/device-profiles">
            Back to device profiles
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="device-profile-detail-panel"
      >
        <h2 class="resource-section__title">{{ deviceProfile.name }}</h2>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            Platform {{ formatPlatformLabel(deviceProfile.platform) }}
          </span>
          <span class="resource-shell__meta-chip">{{ deviceProfile.device_model }}</span>
          <span class="resource-shell__meta-chip">{{ deviceProfile.os_name }}</span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Device Profile ID</span>
            <span class="resource-key-value__value">{{ deviceProfile.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Device Model</span>
            <span class="resource-key-value__value">{{ deviceProfile.device_model }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">OS Name</span>
            <span class="resource-key-value__value">{{ deviceProfile.os_name }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">OS Version</span>
            <span class="resource-key-value__value">
              {{ deviceProfile.os_version || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Browser Name</span>
            <span class="resource-key-value__value">
              {{ deviceProfile.browser_name || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Browser Version</span>
            <span class="resource-key-value__value">
              {{ deviceProfile.browser_version || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Locale</span>
            <span class="resource-key-value__value">
              {{ deviceProfile.locale || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Updated At</span>
            <span class="resource-key-value__value">{{ deviceProfile.updated_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Created At</span>
            <span class="resource-key-value__value">{{ deviceProfile.created_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Notes</span>
            <span class="resource-key-value__value">
              {{ deviceProfile.notes || 'No notes provided yet.' }}
            </span>
          </div>
        </div>
      </section>

      <section
        v-if="!pending && !error && deviceProfile"
        class="resource-section"
        data-testid="device-profile-reputation-section"
      >
        <h2 class="resource-section__title">Reputation Summary</h2>

        <div
          v-if="reputationPending"
          class="resource-state"
          data-testid="device-profile-reputation-loading"
        >
          <h3 class="resource-state__title">Loading reputation summary</h3>
          <p class="resource-state__description">
            正在根據既有 tasks 與 feedback 推導這個 device profile 的最小 reputation summary。
          </p>
        </div>

        <div
          v-else-if="reputationError"
          class="resource-state"
          data-testid="device-profile-reputation-error"
        >
          <h3 class="resource-state__title">Reputation unavailable</h3>
          <p class="resource-state__description">
            {{ reputationError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshReputation()">
              Retry
            </button>
          </div>
        </div>

        <div
          v-else-if="reputation && !hasReputationSignals"
          class="resource-state"
          data-testid="device-profile-reputation-zero"
        >
          <h3 class="resource-state__title">No reputation signals yet</h3>
          <p class="resource-state__description">
            這個 device profile 還沒有累積任何 assignment、submission 或 feedback 紀錄，目前 summary 維持在 zero state。
          </p>
        </div>

        <div
          v-else-if="reputation"
          class="resource-section"
          data-testid="device-profile-reputation-panel"
        >
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              Submission rate {{ reputation.submission_rate.toFixed(2) }}
            </span>
            <span class="resource-shell__meta-chip">
              Feedback {{ reputation.feedback_submitted_count }}
            </span>
          </div>

          <div class="resource-key-value">
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Tasks Assigned</span>
              <span class="resource-key-value__value">
                {{ reputation.tasks_assigned_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Tasks Submitted</span>
              <span class="resource-key-value__value">
                {{ reputation.tasks_submitted_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Feedback Submitted</span>
              <span class="resource-key-value__value">
                {{ reputation.feedback_submitted_count }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Last Feedback At</span>
              <span class="resource-key-value__value">
                {{ reputation.last_feedback_at || 'No feedback submitted yet.' }}
              </span>
            </div>
            <div class="resource-key-value__row">
              <span class="resource-key-value__label">Updated At</span>
              <span class="resource-key-value__value">{{ reputation.updated_at }}</span>
            </div>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>
