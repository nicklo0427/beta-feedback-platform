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
          裝置設定檔
        </NuxtLink>
        <h1 class="resource-shell__title">裝置設定檔詳情</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一測試裝置設定檔的核心欄位，提供後續 eligibility、task 與 feedback 流程可依附的裝置上下文。
        </p>
        <div
          v-if="deviceProfile"
          class="resource-shell__meta"
        >
          <span class="resource-shell__meta-chip">
            平台 {{ formatPlatformLabel(deviceProfile.platform) }}
          </span>
          <span class="resource-shell__meta-chip">
            {{
              deviceProfile.install_channel
                ? `安裝來源 ${deviceProfile.install_channel}`
                : '尚未提供安裝來源'
            }}
          </span>
          <NuxtLink
            class="resource-action"
            data-testid="device-profile-edit-link"
            :to="`/device-profiles/${deviceProfile.id}/edit`"
          >
            編輯裝置設定檔
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="device-profile-detail-loading"
      >
        <h2 class="resource-state__title">載入裝置設定檔詳情中</h2>
        <p class="resource-state__description">
          正在從 API 載入測試裝置設定檔詳情。
        </p>
      </section>

      <section
        v-else-if="error || !deviceProfile"
        class="resource-state"
        data-testid="device-profile-detail-error"
      >
        <h2 class="resource-state__title">無法載入裝置設定檔詳情</h2>
        <p class="resource-state__description">
          {{ error?.message || '找不到指定的裝置設定檔。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" to="/device-profiles">
            返回裝置設定檔列表
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="detail-layout"
        data-testid="device-profile-detail-layout"
      >
        <div class="detail-layout__main">
          <section
            class="resource-section"
            data-testid="device-profile-reputation-section"
          >
            <span class="resource-section__eyebrow">Performance Signals</span>
            <h2 class="resource-section__title">信譽摘要</h2>

            <div
              v-if="reputationPending"
              class="resource-state"
              data-testid="device-profile-reputation-loading"
            >
              <h3 class="resource-state__title">載入信譽摘要中</h3>
              <p class="resource-state__description">
                正在根據既有 tasks 與 feedback 推導這個 device profile 的最小 reputation summary。
              </p>
            </div>

            <div
              v-else-if="reputationError"
              class="resource-state"
              data-testid="device-profile-reputation-error"
            >
              <h3 class="resource-state__title">無法載入信譽摘要</h3>
              <p class="resource-state__description">
                {{ reputationError.message }}
              </p>
              <div class="resource-state__actions">
                <button class="resource-action" type="button" @click="refreshReputation()">
                  重試
                </button>
              </div>
            </div>

            <div
              v-else-if="reputation && !hasReputationSignals"
              class="resource-state"
              data-testid="device-profile-reputation-zero"
            >
              <h3 class="resource-state__title">目前還沒有信譽訊號</h3>
              <p class="resource-state__description">
                這個裝置設定檔還沒有累積任何指派、提交或回饋紀錄，目前摘要維持在零狀態。
              </p>
            </div>

            <div
              v-else-if="reputation"
              class="resource-section"
              data-testid="device-profile-reputation-panel"
            >
              <div class="resource-shell__meta">
                <span class="resource-shell__meta-chip">
                  提交率 {{ reputation.submission_rate.toFixed(2) }}
                </span>
                <span class="resource-shell__meta-chip">
                  回饋數 {{ reputation.feedback_submitted_count }}
                </span>
              </div>

              <div class="resource-key-value">
                <div class="resource-key-value__row">
                  <span class="resource-key-value__label">已指派任務數</span>
                  <span class="resource-key-value__value">
                    {{ reputation.tasks_assigned_count }}
                  </span>
                </div>
                <div class="resource-key-value__row">
                  <span class="resource-key-value__label">已提交任務數</span>
                  <span class="resource-key-value__value">
                    {{ reputation.tasks_submitted_count }}
                  </span>
                </div>
                <div class="resource-key-value__row">
                  <span class="resource-key-value__label">已提交回饋數</span>
                  <span class="resource-key-value__value">
                    {{ reputation.feedback_submitted_count }}
                  </span>
                </div>
                <div class="resource-key-value__row">
                  <span class="resource-key-value__label">最近回饋時間</span>
                  <span class="resource-key-value__value">
                    {{ reputation.last_feedback_at || '尚未提交任何回饋。' }}
                  </span>
                </div>
                <div class="resource-key-value__row">
                  <span class="resource-key-value__label">更新時間</span>
                  <span class="resource-key-value__value">{{ reputation.updated_at }}</span>
                </div>
              </div>
            </div>
          </section>
        </div>

        <aside class="detail-layout__rail">
          <section
            class="resource-section"
            data-testid="device-profile-detail-panel"
          >
            <span class="resource-section__eyebrow">Device Profile</span>
            <h2 class="resource-section__title">{{ deviceProfile.name }}</h2>

            <div class="resource-shell__meta">
              <span class="resource-shell__meta-chip">{{ deviceProfile.device_model }}</span>
              <span class="resource-shell__meta-chip">{{ deviceProfile.os_name }}</span>
            </div>

            <div class="resource-key-value">
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">裝置設定檔 ID</span>
                <span class="resource-key-value__value">{{ deviceProfile.id }}</span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">裝置型號</span>
                <span class="resource-key-value__value">{{ deviceProfile.device_model }}</span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">擁有者帳號</span>
                <span class="resource-key-value__value">
                  {{ deviceProfile.owner_account_id || '目前尚未建立擁有者基線。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">作業系統名稱</span>
                <span class="resource-key-value__value">{{ deviceProfile.os_name }}</span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">安裝來源 / 發佈渠道</span>
                <span class="resource-key-value__value">
                  {{ deviceProfile.install_channel || '尚未提供。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">作業系統版本</span>
                <span class="resource-key-value__value">
                  {{ deviceProfile.os_version || '尚未提供。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">瀏覽器名稱</span>
                <span class="resource-key-value__value">
                  {{ deviceProfile.browser_name || '尚未提供。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">瀏覽器版本</span>
                <span class="resource-key-value__value">
                  {{ deviceProfile.browser_version || '尚未提供。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">語系</span>
                <span class="resource-key-value__value">
                  {{ deviceProfile.locale || '尚未提供。' }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">更新時間</span>
                <span class="resource-key-value__value">{{ deviceProfile.updated_at }}</span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">建立時間</span>
                <span class="resource-key-value__value">{{ deviceProfile.created_at }}</span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">備註</span>
                <span class="resource-key-value__value">
                  {{ deviceProfile.notes || '目前沒有備註。' }}
                </span>
              </div>
            </div>
          </section>
        </aside>
      </section>
    </section>
  </main>
</template>
