import { sampleBenchmarkReport, sampleCatalog, sampleResults, sampleWorkflows } from "../data/seedData.js";

export function createLocalJsonClient() {
  return {
    async loadAll() {
      return {
        catalog: sampleCatalog,
        workflows: sampleWorkflows,
        results: sampleResults,
        benchmark: sampleBenchmarkReport,
      };
    },
  };
}
