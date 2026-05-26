<template>
  <section class="grid" style="gap: 1rem">
    <h2>Compare Experiments</h2>

    <div class="card grid" style="grid-template-columns: 1fr auto; align-items: end">
      <div>
        <label for="ids">Experiment IDs (comma-separated)</label>
        <input id="ids" v-model="idsInput" placeholder="1,2,3" />
      </div>
      <button :disabled="loading" @click="onCompare">{{ loading ? "Comparing..." : "Compare" }}</button>
    </div>

    <div v-if="error" class="notice error">{{ error }}</div>
    <div v-if="loading" class="notice info">Loading comparison...</div>
    <div v-else-if="rows.length === 0" class="notice info">Enter experiment IDs to compare.</div>

    <template v-else>
      <div class="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Symbol</th>
              <th>Final Equity</th>
              <th>Total Return</th>
              <th>Annualized Return</th>
              <th>Sharpe</th>
              <th>Max Drawdown</th>
              <th>VaR 95%</th>
              <th>ES 95%</th>
              <th># Trades</th>
              <th>Time in Market</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.experiment_id">
              <td>{{ row.experiment_id }}</td>
              <td>{{ row.symbol }}</td>
              <td>{{ formatCurrency(row.final_equity) }}</td>
              <td>{{ formatPct(row.total_return) }}</td>
              <td>{{ formatPct(row.annualized_return) }}</td>
              <td>{{ formatNum(row.sharpe_ratio) }}</td>
              <td>{{ formatPct(row.max_drawdown) }}</td>
              <td>{{ formatPct(row.historical_var_95) }}</td>
              <td>{{ formatPct(row.expected_shortfall_95) }}</td>
              <td>{{ row.number_of_trades }}</td>
              <td>{{ formatPct(row.time_in_market_pct) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <h3>Comparison Bar Chart</h3>
        <canvas ref="compareChartRef"></canvas>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import Chart from "chart.js/auto";
import { nextTick, ref, watch } from "vue";

import { compareExperiments } from "../api/client";
import type { CompareExperimentsResponse } from "../types";

const idsInput = ref("1,2,3");
const loading = ref(false);
const error = ref<string | null>(null);
const rows = ref<CompareExperimentsResponse["experiments"]>([]);
const compareChartRef = ref<HTMLCanvasElement | null>(null);
let chart: Chart | null = null;

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

function parseIds(input: string): number[] {
  return input
    .split(",")
    .map((item) => Number(item.trim()))
    .filter((value) => Number.isInteger(value) && value > 0);
}

async function onCompare(): Promise<void> {
  error.value = null;
  loading.value = true;
  try {
    const ids = parseIds(idsInput.value);
    if (ids.length === 0) {
      throw new Error("Please provide at least one valid experiment ID");
    }
    const response = await compareExperiments(ids);
    rows.value = response.experiments;
  } catch (err) {
    rows.value = [];
    error.value = err instanceof Error ? err.message : "Failed to compare experiments";
  } finally {
    loading.value = false;
  }
}

watch(rows, async (newRows) => {
  if (!newRows.length) return;
  await nextTick();
  if (!compareChartRef.value) return;
  if (chart) chart.destroy();

  chart = new Chart(compareChartRef.value, {
    type: "bar",
    data: {
      labels: newRows.map((row) => String(row.experiment_id)),
      datasets: [
        {
          label: "Total Return",
          data: newRows.map((row) => row.total_return ?? 0),
          backgroundColor: "rgba(37,99,235,0.75)",
        },
        {
          label: "Sharpe Ratio",
          data: newRows.map((row) => row.sharpe_ratio ?? 0),
          backgroundColor: "rgba(16,185,129,0.75)",
        },
        {
          label: "Max Drawdown",
          data: newRows.map((row) => row.max_drawdown ?? 0),
          backgroundColor: "rgba(244,63,94,0.75)",
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: { y: { beginAtZero: true } },
    },
  });
});
</script>
