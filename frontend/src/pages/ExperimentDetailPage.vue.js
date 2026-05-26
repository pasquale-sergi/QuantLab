import Chart from "chart.js/auto";
import { computed, defineComponent, h, nextTick, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { getExperiment } from "../api/client";
const route = useRoute();
const detail = ref(null);
const loading = ref(true);
const error = ref(null);
const equityChartRef = ref(null);
let chart = null;
const experimentId = computed(() => Number(route.params.id));
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
    }
    catch (err) {
        error.value = err instanceof Error ? err.message : "Failed to load experiment";
    }
    finally {
        loading.value = false;
    }
});
watch(detail, async (newDetail) => {
    if (!newDetail)
        return;
    await nextTick();
    if (!equityChartRef.value)
        return;
    if (chart)
        chart.destroy();
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
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "grid" },
    ...{ style: {} },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
if (__VLS_ctx.loading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "notice info" },
    });
}
else if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "notice error" },
    });
    (__VLS_ctx.error);
}
else if (!__VLS_ctx.detail) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "notice info" },
    });
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "grid grid-3" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.detail.experiment_id);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.detail.symbol);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.detail.strategy);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.detail.start_date);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.detail.end_date);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.formatCurrency(__VLS_ctx.detail.initial_cash));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.detail.transaction_cost_bps);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (JSON.stringify(__VLS_ctx.detail.parameters));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "grid grid-3" },
    });
    const __VLS_0 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0({
        label: "Final Equity",
        value: (__VLS_ctx.formatCurrency(__VLS_ctx.detail.final_equity)),
    }));
    const __VLS_2 = __VLS_1({
        label: "Final Equity",
        value: (__VLS_ctx.formatCurrency(__VLS_ctx.detail.final_equity)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_1));
    const __VLS_4 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_5 = __VLS_asFunctionalComponent(__VLS_4, new __VLS_4({
        label: "Total Return",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.total_return)),
    }));
    const __VLS_6 = __VLS_5({
        label: "Total Return",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.total_return)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_5));
    const __VLS_8 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_9 = __VLS_asFunctionalComponent(__VLS_8, new __VLS_8({
        label: "Annualized Return",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.annualized_return)),
    }));
    const __VLS_10 = __VLS_9({
        label: "Annualized Return",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.annualized_return)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_9));
    const __VLS_12 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_13 = __VLS_asFunctionalComponent(__VLS_12, new __VLS_12({
        label: "Annualized Volatility",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.annualized_volatility)),
    }));
    const __VLS_14 = __VLS_13({
        label: "Annualized Volatility",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.annualized_volatility)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_13));
    const __VLS_16 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_17 = __VLS_asFunctionalComponent(__VLS_16, new __VLS_16({
        label: "Sharpe Ratio",
        value: (__VLS_ctx.formatNum(__VLS_ctx.detail.metrics.sharpe_ratio)),
    }));
    const __VLS_18 = __VLS_17({
        label: "Sharpe Ratio",
        value: (__VLS_ctx.formatNum(__VLS_ctx.detail.metrics.sharpe_ratio)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_17));
    const __VLS_20 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_21 = __VLS_asFunctionalComponent(__VLS_20, new __VLS_20({
        label: "Max Drawdown",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.max_drawdown)),
    }));
    const __VLS_22 = __VLS_21({
        label: "Max Drawdown",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.max_drawdown)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_21));
    const __VLS_24 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_25 = __VLS_asFunctionalComponent(__VLS_24, new __VLS_24({
        label: "VaR 95%",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.historical_var_95)),
    }));
    const __VLS_26 = __VLS_25({
        label: "VaR 95%",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.historical_var_95)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_25));
    const __VLS_28 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_29 = __VLS_asFunctionalComponent(__VLS_28, new __VLS_28({
        label: "Expected Shortfall 95%",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.expected_shortfall_95)),
    }));
    const __VLS_30 = __VLS_29({
        label: "Expected Shortfall 95%",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.expected_shortfall_95)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_29));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "grid grid-3" },
    });
    const __VLS_32 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_33 = __VLS_asFunctionalComponent(__VLS_32, new __VLS_32({
        label: "Number of Trades",
        value: (String(__VLS_ctx.detail.metrics.number_of_trades)),
    }));
    const __VLS_34 = __VLS_33({
        label: "Number of Trades",
        value: (String(__VLS_ctx.detail.metrics.number_of_trades)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_33));
    const __VLS_36 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_37 = __VLS_asFunctionalComponent(__VLS_36, new __VLS_36({
        label: "Buy Trades",
        value: (String(__VLS_ctx.detail.metrics.buy_trades)),
    }));
    const __VLS_38 = __VLS_37({
        label: "Buy Trades",
        value: (String(__VLS_ctx.detail.metrics.buy_trades)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_37));
    const __VLS_40 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_41 = __VLS_asFunctionalComponent(__VLS_40, new __VLS_40({
        label: "Sell Trades",
        value: (String(__VLS_ctx.detail.metrics.sell_trades)),
    }));
    const __VLS_42 = __VLS_41({
        label: "Sell Trades",
        value: (String(__VLS_ctx.detail.metrics.sell_trades)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_41));
    const __VLS_44 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_45 = __VLS_asFunctionalComponent(__VLS_44, new __VLS_44({
        label: "Time in Market",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.time_in_market_pct)),
    }));
    const __VLS_46 = __VLS_45({
        label: "Time in Market",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.time_in_market_pct)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_45));
    const __VLS_48 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_49 = __VLS_asFunctionalComponent(__VLS_48, new __VLS_48({
        label: "Best Day",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.best_day)),
    }));
    const __VLS_50 = __VLS_49({
        label: "Best Day",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.best_day)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_49));
    const __VLS_52 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_53 = __VLS_asFunctionalComponent(__VLS_52, new __VLS_52({
        label: "Worst Day",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.worst_day)),
    }));
    const __VLS_54 = __VLS_53({
        label: "Worst Day",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.worst_day)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_53));
    const __VLS_56 = {}.MetricCard;
    /** @type {[typeof __VLS_components.MetricCard, ]} */ ;
    // @ts-ignore
    const __VLS_57 = __VLS_asFunctionalComponent(__VLS_56, new __VLS_56({
        label: "Average Daily Return",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.average_daily_return)),
    }));
    const __VLS_58 = __VLS_57({
        label: "Average Daily Return",
        value: (__VLS_ctx.formatPct(__VLS_ctx.detail.metrics.average_daily_return)),
    }, ...__VLS_functionalComponentArgsRest(__VLS_57));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.canvas, __VLS_intrinsicElements.canvas)({
        ref: "equityChartRef",
    });
    /** @type {typeof __VLS_ctx.equityChartRef} */ ;
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "card table-wrap" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.table, __VLS_intrinsicElements.table)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.thead, __VLS_intrinsicElements.thead)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.tr, __VLS_intrinsicElements.tr)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.tbody, __VLS_intrinsicElements.tbody)({});
    for (const [trade] of __VLS_getVForSourceType((__VLS_ctx.detail.trades))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.tr, __VLS_intrinsicElements.tr)({
            key: (`${trade.date}-${trade.side}-${trade.price}`),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (trade.date);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (trade.side);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (trade.price.toFixed(2));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (trade.shares);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (trade.transaction_cost.toFixed(4));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (trade.cash_after_trade.toFixed(2));
    }
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
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-3']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-3']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['table-wrap']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            detail: detail,
            loading: loading,
            error: error,
            equityChartRef: equityChartRef,
            formatCurrency: formatCurrency,
            formatPct: formatPct,
            formatNum: formatNum,
            MetricCard: MetricCard,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
