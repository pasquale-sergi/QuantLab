<template>
  <section class="grid" style="gap: 1rem">
    <h2>Experiments</h2>

    <div v-if="loading" class="notice info">Loading experiments...</div>
    <div v-else-if="error" class="notice error">{{ error }}</div>
    <div v-else-if="rows.length === 0" class="notice info">No experiments found yet.</div>

    <div v-else class="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>Experiment ID</th>
            <th>Symbol</th>
            <th>Strategy</th>
            <th>Start</th>
            <th>End</th>
            <th>Final Equity</th>
            <th>Total Return</th>
            <th>Sharpe</th>
            <th>Max Drawdown</th>
            <th># Trades</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.experiment_id">
            <td>
              <RouterLink :to="`/experiments/${row.experiment_id}`">{{ row.experiment_id }}</RouterLink>
            </td>
            <td>{{ row.symbol }}</td>
            <td>{{ row.strategy }}</td>
            <td>{{ row.start_date }}</td>
            <td>{{ row.end_date }}</td>
            <td>{{ formatCurrency(row.final_equity) }}</td>
            <td>{{ formatPct(row.total_return) }}</td>
            <td>{{ formatNum(row.sharpe_ratio) }}</td>
            <td>{{ formatPct(row.max_drawdown) }}</td>
            <td>{{ row.number_of_trades ?? "-" }}</td>
            <td>{{ row.created_at }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

import { getExperiment, listExperiments } from "../api/client";

type ExperimentRow = {
  experiment_id: number;
  symbol: string;
  strategy: string;
  start_date: string;
  end_date: string;
  final_equity: number;
  created_at: string;
  total_return: number | null;
  sharpe_ratio: number | null;
  max_drawdown: number | null;
  number_of_trades: number | null;
};

const loading = ref(true);
const error = ref<string | null>(null);
const rows = ref<ExperimentRow[]>([]);

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

onMounted(async () => {
  try {
    const experiments = await listExperiments();
    const details = await Promise.all(experiments.map((item) => getExperiment(item.experiment_id)));

    rows.value = experiments.map((item, index) => {
      const detail = details[index];
      return {
        experiment_id: item.experiment_id,
        symbol: item.symbol,
        strategy: item.strategy,
        start_date: item.start_date,
        end_date: item.end_date,
        final_equity: item.final_equity,
        created_at: item.created_at,
        total_return: detail.metrics.total_return,
        sharpe_ratio: detail.metrics.sharpe_ratio,
        max_drawdown: detail.metrics.max_drawdown,
        number_of_trades: detail.metrics.number_of_trades,
      };
    });
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Failed to load experiments";
  } finally {
    loading.value = false;
  }
});
</script>
