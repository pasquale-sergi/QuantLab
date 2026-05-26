import { createRouter, createWebHistory } from "vue-router";

import RunBacktestPage from "./pages/RunBacktestPage.vue";
import ExperimentsPage from "./pages/ExperimentsPage.vue";
import ExperimentDetailPage from "./pages/ExperimentDetailPage.vue";
import ComparePage from "./pages/ComparePage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/run-backtest" },
    { path: "/run-backtest", component: RunBacktestPage },
    { path: "/experiments", component: ExperimentsPage },
    { path: "/experiments/:id", component: ExperimentDetailPage },
    { path: "/compare", component: ComparePage },
  ],
});

export default router;
