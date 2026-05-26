<template>
  <div class="app-shell">
    <header class="top-nav">
      <h1>QuantLab</h1>
      <nav>
        <RouterLink to="/run-backtest">Run Backtest</RouterLink>
        <RouterLink to="/experiments">Experiments</RouterLink>
        <RouterLink to="/compare">Compare</RouterLink>
      </nav>
    </header>

    <main class="page-container">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts"></script>
