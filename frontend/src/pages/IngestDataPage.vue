<template>
  <section class="grid" style="gap: 1rem">
    <h2>Ingest Data</h2>

    <form class="card grid grid-3" @submit.prevent="onSubmit">
      <div>
        <label for="symbol">Symbol</label>
        <input id="symbol" v-model="form.symbol" required />
      </div>
      <div>
        <label for="start_date">Start Date</label>
        <input id="start_date" v-model="form.start_date" type="date" required />
      </div>
      <div>
        <label for="end_date">End Date</label>
        <input id="end_date" v-model="form.end_date" type="date" required />
      </div>
      <div style="display: flex; align-items: end">
        <button :disabled="loading" type="submit">{{ loading ? "Ingesting..." : "Ingest Data" }}</button>
      </div>
    </form>

    <div v-if="error" class="notice error">{{ error }}</div>
    <div v-if="loading" class="notice info">Ingesting market data...</div>

    <div v-if="result" class="card grid grid-2">
      <div>
        <div>Symbol</div>
        <div class="metric-value">{{ result.symbol }}</div>
      </div>
      <div>
        <div>Rows Inserted</div>
        <div class="metric-value">{{ result.rows_inserted }}</div>
      </div>
      <div>
        <div>Start Date</div>
        <div class="metric-value">{{ result.start_date }}</div>
      </div>
      <div>
        <div>End Date</div>
        <div class="metric-value">{{ result.end_date }}</div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";

import { ingestMarketData } from "../api/client";
import type { IngestMarketDataResponse } from "../types";

const form = ref({
  symbol: "MSFT",
  start_date: "2020-01-01",
  end_date: "2024-12-31",
});

const loading = ref(false);
const error = ref<string | null>(null);
const result = ref<IngestMarketDataResponse | null>(null);

async function onSubmit(): Promise<void> {
  error.value = null;
  result.value = null;
  loading.value = true;

  try {
    result.value = await ingestMarketData({
      symbol: form.value.symbol,
      start_date: form.value.start_date,
      end_date: form.value.end_date,
    });
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to ingest market data";
  } finally {
    loading.value = false;
  }
}
</script>
