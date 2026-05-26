<template>
  <section class="grid" style="gap: 1rem">
    <h2>Run Backtest</h2>

    <div v-if="symbolsLoading" class="notice info">Loading ingested symbols...</div>
    <div v-else-if="symbolsError" class="notice error">{{ symbolsError }}</div>
    <div v-else-if="availableSymbols.length === 0" class="notice info">
      No ingested symbols found. Go to <RouterLink to="/ingest">Ingest Data</RouterLink> first.
    </div>

    <form class="card grid grid-3" @submit.prevent="onSubmit">
      <div>
        <label for="symbol">Symbol</label>
        <select id="symbol" v-model="form.symbol" :disabled="symbolsLoading || availableSymbols.length === 0" required>
          <option disabled value="">Select a symbol</option>
          <option v-for="symbol in availableSymbols" :key="symbol" :value="symbol">{{ symbol }}</option>
        </select>
      </div>
      <div>
        <label for="start_date">Start Date</label>
        <input id="start_date" v-model="form.start_date" type="date" required />
      </div>
      <div>
        <label for="end_date">End Date</label>
        <input id="end_date" v-model="form.end_date" type="date" required />
      </div>
      <div>
        <label for="short_window">Short Window</label>
        <input id="short_window" v-model.number="form.short_window" type="number" min="1" required />
      </div>
      <div>
        <label for="long_window">Long Window</label>
        <input id="long_window" v-model.number="form.long_window" type="number" min="2" required />
      </div>
      <div>
        <label for="initial_cash">Initial Cash</label>
        <input id="initial_cash" v-model.number="form.initial_cash" type="number" min="1" required />
      </div>
      <div>
        <label for="transaction_cost_bps">Transaction Cost (bps)</label>
        <input id="transaction_cost_bps" v-model.number="form.transaction_cost_bps" type="number" min="0" required />
      </div>
      <div style="display: flex; align-items: end">
        <button :disabled="loading || symbolsLoading || availableSymbols.length === 0" type="submit">
          {{ loading ? "Running..." : "Run Backtest" }}
        </button>
      </div>
    </form>

    <div v-if="error" class="notice error">
      <template v-if="isMissingSymbolError">
        This symbol has not been ingested yet. Go to Ingest Data first, then run the backtest.
        <RouterLink to="/ingest">Go to Ingest Data</RouterLink>
      </template>
      <template v-else>
        {{ error }}
      </template>
    </div>
    <div v-if="loading" class="notice info">Running backtest...</div>

    <div v-if="result" class="grid" style="gap: 1rem">
      <div class="card">
        <h3>Result Summary</h3>
        <div class="grid grid-3">
          <div>
            <div>Experiment ID</div>
            <div class="metric-value">{{ result.experiment_id }}</div>
          </div>
          <div>
            <div>Final Equity</div>
            <div class="metric-value">{{ formatCurrency(result.final_equity) }}</div>
          </div>
          <div>
            <div>Total Return</div>
            <div class="metric-value">{{ formatPct(result.metrics.total_return) }}</div>
          </div>
          <div>
            <div>Sharpe Ratio</div>
            <div class="metric-value">{{ formatNum(result.metrics.sharpe_ratio) }}</div>
          </div>
          <div>
            <div>Max Drawdown</div>
            <div class="metric-value">{{ formatPct(result.metrics.max_drawdown) }}</div>
          </div>
          <div>
            <div>Number of Trades</div>
            <div class="metric-value">{{ result.metrics.number_of_trades }}</div>
          </div>
          <div>
            <div>Time in Market</div>
            <div class="metric-value">{{ formatPct(result.metrics.time_in_market_pct) }}</div>
          </div>
        </div>
      </div>

      <div class="card">
        <h3>Equity Curve</h3>
        <canvas ref="equityChartRef"></canvas>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import Chart from "chart.js/auto";
import { computed, nextTick, onMounted, ref, watch } from "vue";

import { getIngestedSymbols, runBacktest } from "../api/client";
import type { BacktestRunResponse } from "../types";

const form = ref({
  symbol: "",
  start_date: "2020-01-01",
  end_date: "2024-12-31",
  short_window: 20,
  long_window: 100,
  initial_cash: 10000,
  transaction_cost_bps: 10,
});

const availableSymbols = ref<string[]>([]);
const symbolsLoading = ref(false);
const symbolsError = ref<string | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);
const result = ref<BacktestRunResponse | null>(null);
const equityChartRef = ref<HTMLCanvasElement | null>(null);
let chart: Chart | null = null;

const isMissingSymbolError = computed(() => {
  const message = error.value?.toLowerCase() ?? "";
  return message.includes("symbol") && message.includes("does not exist");
});

function formatCurrency(value: number): string {
  return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 2 }).format(value);
}

function formatPct(value: number | null): string {
  if (value == null) return "-";
  return `${(value * 100).toFixed(2)}%`;
}

function formatNum(value: number | null): string {
  if (value == null) return "-";
  return value.toFixed(3);
}

async function onSubmit(): Promise<void> {
  error.value = null;
  result.value = null;
  loading.value = true;
  try {
    if (!form.value.symbol) {
      throw new Error("Please select an ingested symbol before running the backtest");
    }
    if (form.value.short_window >= form.value.long_window) {
      throw new Error("short_window must be smaller than long_window");
    }
    result.value = await runBacktest({
      symbol: form.value.symbol,
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      strategy: "moving_average_crossover",
      parameters: {
        short_window: form.value.short_window,
        long_window: form.value.long_window,
      },
      initial_cash: form.value.initial_cash,
      transaction_cost_bps: form.value.transaction_cost_bps,
    });
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to run backtest";
  } finally {
    loading.value = false;
  }
}

async function loadSymbols(): Promise<void> {
  symbolsError.value = null;
  symbolsLoading.value = true;

  try {
    availableSymbols.value = await getIngestedSymbols();
    if (availableSymbols.value.length > 0 && !availableSymbols.value.includes(form.value.symbol)) {
      form.value.symbol = availableSymbols.value[0];
    }
  } catch (err) {
    symbolsError.value = err instanceof Error ? err.message : "Failed to load ingested symbols";
  } finally {
    symbolsLoading.value = false;
  }
}

onMounted(async () => {
  await loadSymbols();
});

watch(result, async (newValue) => {
  if (!newValue) return;
  await nextTick();
  if (!equityChartRef.value) return;
  if (chart) chart.destroy();

  chart = new Chart(equityChartRef.value, {
    type: "line",
    data: {
      labels: newValue.equity_curve.map((point) => point.date),
      datasets: [
        {
          label: "Total Equity",
          data: newValue.equity_curve.map((point) => point.total_equity),
          borderColor: "#2563eb",
          backgroundColor: "rgba(37,99,235,0.2)",
          pointRadius: 0,
          tension: 0.2,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: { y: { beginAtZero: false } },
    },
  });
});
</script>
