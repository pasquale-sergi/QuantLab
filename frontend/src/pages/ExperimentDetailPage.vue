<template>
  <section class="grid" style="gap: 1rem">
    <h2>Experiment Detail</h2>

    <div v-if="loading" class="notice info">Loading experiment...</div>
    <div v-else-if="error" class="notice error">{{ error }}</div>
    <div v-else-if="!detail" class="notice info">No experiment found.</div>

    <template v-else>
      <div class="card">
        <h3>Configuration</h3>
        <div class="grid grid-3">
          <div><strong>ID:</strong> {{ detail.experiment_id }}</div>
          <div><strong>Symbol:</strong> {{ detail.symbol }}</div>
          <div><strong>Strategy:</strong> {{ detail.strategy }}</div>
          <div><strong>Start:</strong> {{ detail.start_date }}</div>
          <div><strong>End:</strong> {{ detail.end_date }}</div>
          <div><strong>Initial Cash:</strong> {{ formatCurrency(detail.initial_cash) }}</div>
          <div><strong>Transaction Cost (bps):</strong> {{ detail.transaction_cost_bps }}</div>
          <div><strong>Parameters:</strong> {{ JSON.stringify(detail.parameters) }}</div>
        </div>
      </div>

      <div class="card">
        <h3>Performance & Risk Metrics</h3>
        <div class="grid grid-3">
          <MetricCard label="Final Equity" :value="formatCurrency(detail.final_equity)" />
          <MetricCard label="Total Return" :value="formatPct(detail.metrics.total_return)" />
          <MetricCard label="Annualized Return" :value="formatPct(detail.metrics.annualized_return)" />
          <MetricCard label="Annualized Volatility" :value="formatPct(detail.metrics.annualized_volatility)" />
          <MetricCard label="Sharpe Ratio" :value="formatNum(detail.metrics.sharpe_ratio)" />
          <MetricCard label="Max Drawdown" :value="formatPct(detail.metrics.max_drawdown)" />
          <MetricCard label="VaR 95%" :value="formatPct(detail.metrics.historical_var_95)" />
          <MetricCard label="Expected Shortfall 95%" :value="formatPct(detail.metrics.expected_shortfall_95)" />
        </div>
      </div>

      <div class="card">
        <h3>Behavior Summary</h3>
        <div class="grid grid-3">
          <MetricCard label="Number of Trades" :value="String(detail.metrics.number_of_trades)" />
          <MetricCard label="Buy Trades" :value="String(detail.metrics.buy_trades)" />
          <MetricCard label="Sell Trades" :value="String(detail.metrics.sell_trades)" />
          <MetricCard label="Time in Market" :value="formatPct(detail.metrics.time_in_market_pct)" />
          <MetricCard label="Best Day" :value="formatPct(detail.metrics.best_day)" />
          <MetricCard label="Worst Day" :value="formatPct(detail.metrics.worst_day)" />
          <MetricCard label="Average Daily Return" :value="formatPct(detail.metrics.average_daily_return)" />
        </div>
      </div>

      <div class="card">
        <h3>Equity Curve</h3>
        <canvas ref="equityChartRef"></canvas>
      </div>

      <div class="card table-wrap">
        <h3>Trades</h3>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Side</th>
              <th>Price</th>
              <th>Shares</th>
              <th>Transaction Cost</th>
              <th>Cash After Trade</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="trade in detail.trades" :key="`${trade.date}-${trade.side}-${trade.price}`">
              <td>{{ trade.date }}</td>
              <td>{{ trade.side }}</td>
              <td>{{ trade.price.toFixed(2) }}</td>
              <td>{{ trade.shares }}</td>
              <td>{{ trade.transaction_cost.toFixed(4) }}</td>
              <td>{{ trade.cash_after_trade.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import Chart from "chart.js/auto";
import { computed, defineComponent, h, nextTick, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import { getExperiment } from "../api/client";
import type { ExperimentDetail } from "../types";

const route = useRoute();
const detail = ref<ExperimentDetail | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const equityChartRef = ref<HTMLCanvasElement | null>(null);
let chart: Chart | null = null;

const experimentId = computed(() => Number(route.params.id));

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

const MetricCard = defineComponent({
  name: "MetricCard",
  props: {
    label: { type: String, required: true },
    value: { type: String, required: true },
  },
  setup(props) {
    return () => h("div", { class: "card", style: "padding:0.75rem" }, [
      h("div", props.label),
      h("div", { class: "metric-value" }, props.value),
    ]);
  },
});

onMounted(async () => {
  try {
    detail.value = await getExperiment(experimentId.value);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to load experiment";
  } finally {
    loading.value = false;
  }
});

watch(detail, async (newDetail) => {
  if (!newDetail) return;
  await nextTick();
  if (!equityChartRef.value) return;
  if (chart) chart.destroy();

  chart = new Chart(equityChartRef.value, {
    type: "line",
    data: {
      labels: newDetail.equity_curve.map((point) => point.date),
      datasets: [
        {
          label: "Total Equity",
          data: newDetail.equity_curve.map((point) => point.total_equity),
          borderColor: "#16a34a",
          backgroundColor: "rgba(22,163,74,0.2)",
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
