import Chart from "chart.js/auto";
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { getIngestedSymbols, runBacktest } from "../api/client";
const form = ref({
    symbol: "",
    start_date: "2020-01-01",
    end_date: "2024-12-31",
    short_window: 20,
    long_window: 100,
    initial_cash: 10000,
    transaction_cost_bps: 10,
});
const availableSymbols = ref([]);
const symbolsLoading = ref(false);
const symbolsError = ref(null);
const loading = ref(false);
const error = ref(null);
const result = ref(null);
const equityChartRef = ref(null);
let chart = null;
const isMissingSymbolError = computed(() => {
    const message = error.value?.toLowerCase() ?? "";
    return message.includes("symbol") && message.includes("does not exist");
});
function formatCurrency(value) {
    return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 2 }).format(value);
}
function formatPct(value) {
    if (value == null)
        return "-";
    return `${(value * 100).toFixed(2)}%`;
}
function formatNum(value) {
    if (value == null)
        return "-";
    return value.toFixed(3);
}
async function onSubmit() {
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
    }
    catch (err) {
        error.value = err instanceof Error ? err.message : "Failed to run backtest";
    }
    finally {
        loading.value = false;
    }
}
async function loadSymbols() {
    symbolsError.value = null;
    symbolsLoading.value = true;
    try {
        availableSymbols.value = await getIngestedSymbols();
        if (availableSymbols.value.length > 0 && !availableSymbols.value.includes(form.value.symbol)) {
            form.value.symbol = availableSymbols.value[0];
        }
    }
    catch (err) {
        symbolsError.value = err instanceof Error ? err.message : "Failed to load ingested symbols";
    }
    finally {
        symbolsLoading.value = false;
    }
}
onMounted(async () => {
    await loadSymbols();
});
watch(result, async (newValue) => {
    if (!newValue)
        return;
    await nextTick();
    if (!equityChartRef.value)
        return;
    if (chart)
        chart.destroy();
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
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "grid" },
    ...{ style: {} },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
if (__VLS_ctx.symbolsLoading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "notice info" },
    });
}
else if (__VLS_ctx.symbolsError) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "notice error" },
    });
    (__VLS_ctx.symbolsError);
}
else if (__VLS_ctx.availableSymbols.length === 0) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "notice info" },
    });
    const __VLS_0 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    const __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0({
        to: "/ingest",
    }));
    const __VLS_2 = __VLS_1({
        to: "/ingest",
    }, ...__VLS_functionalComponentArgsRest(__VLS_1));
    __VLS_3.slots.default;
    var __VLS_3;
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.form, __VLS_intrinsicElements.form)({
    ...{ onSubmit: (__VLS_ctx.onSubmit) },
    ...{ class: "card grid grid-3" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
    for: "symbol",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    id: "symbol",
    value: (__VLS_ctx.form.symbol),
    disabled: (__VLS_ctx.symbolsLoading || __VLS_ctx.availableSymbols.length === 0),
    required: true,
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    disabled: true,
    value: "",
});
for (const [symbol] of __VLS_getVForSourceType((__VLS_ctx.availableSymbols))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        key: (symbol),
        value: (symbol),
    });
    (symbol);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
    for: "start_date",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    id: "start_date",
    type: "date",
    required: true,
});
(__VLS_ctx.form.start_date);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
    for: "end_date",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    id: "end_date",
    type: "date",
    required: true,
});
(__VLS_ctx.form.end_date);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
    for: "short_window",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    id: "short_window",
    type: "number",
    min: "1",
    required: true,
});
(__VLS_ctx.form.short_window);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
    for: "long_window",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    id: "long_window",
    type: "number",
    min: "2",
    required: true,
});
(__VLS_ctx.form.long_window);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
    for: "initial_cash",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    id: "initial_cash",
    type: "number",
    min: "1",
    required: true,
});
(__VLS_ctx.form.initial_cash);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
    for: "transaction_cost_bps",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    id: "transaction_cost_bps",
    type: "number",
    min: "0",
    required: true,
});
(__VLS_ctx.form.transaction_cost_bps);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ style: {} },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    disabled: (__VLS_ctx.loading || __VLS_ctx.symbolsLoading || __VLS_ctx.availableSymbols.length === 0),
    type: "submit",
});
(__VLS_ctx.loading ? "Running..." : "Run Backtest");
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "notice error" },
    });
    if (__VLS_ctx.isMissingSymbolError) {
        const __VLS_4 = {}.RouterLink;
        /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
        // @ts-ignore
        const __VLS_5 = __VLS_asFunctionalComponent(__VLS_4, new __VLS_4({
            to: "/ingest",
        }));
        const __VLS_6 = __VLS_5({
            to: "/ingest",
        }, ...__VLS_functionalComponentArgsRest(__VLS_5));
        __VLS_7.slots.default;
        var __VLS_7;
    }
    else {
        (__VLS_ctx.error);
    }
}
if (__VLS_ctx.loading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "notice info" },
    });
}
if (__VLS_ctx.result) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "grid" },
        ...{ style: {} },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "grid grid-3" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric-value" },
    });
    (__VLS_ctx.result.experiment_id);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric-value" },
    });
    (__VLS_ctx.formatCurrency(__VLS_ctx.result.final_equity));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric-value" },
    });
    (__VLS_ctx.formatPct(__VLS_ctx.result.metrics.total_return));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric-value" },
    });
    (__VLS_ctx.formatNum(__VLS_ctx.result.metrics.sharpe_ratio));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric-value" },
    });
    (__VLS_ctx.formatPct(__VLS_ctx.result.metrics.max_drawdown));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric-value" },
    });
    (__VLS_ctx.result.metrics.number_of_trades);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "metric-value" },
    });
    (__VLS_ctx.formatPct(__VLS_ctx.result.metrics.time_in_market_pct));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.canvas, __VLS_intrinsicElements.canvas)({
        ref: "equityChartRef",
    });
    /** @type {typeof __VLS_ctx.equityChartRef} */ ;
}
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['notice']} */ ;
/** @type {__VLS_StyleScopedClasses['info']} */ ;
/** @type {__VLS_StyleScopedClasses['notice']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['notice']} */ ;
/** @type {__VLS_StyleScopedClasses['info']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-3']} */ ;
/** @type {__VLS_StyleScopedClasses['notice']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['notice']} */ ;
/** @type {__VLS_StyleScopedClasses['info']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-3']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-value']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-value']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-value']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-value']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-value']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-value']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-value']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            form: form,
            availableSymbols: availableSymbols,
            symbolsLoading: symbolsLoading,
            symbolsError: symbolsError,
            loading: loading,
            error: error,
            result: result,
            equityChartRef: equityChartRef,
            isMissingSymbolError: isMissingSymbolError,
            formatCurrency: formatCurrency,
            formatPct: formatPct,
            formatNum: formatNum,
            onSubmit: onSubmit,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
