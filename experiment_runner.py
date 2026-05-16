import json
import os
import yaml
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime
import numpy as np
from main import run_simulation
from metrics import compute_all_metrics
from stats import (
    t_test_independent, mann_whitney_u_test, anova_test,
    bonferroni_correction, hypothesis_test_summary
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExperimentRunner:
    
    def __init__(self, config_path: str = "configs/baseline.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.problems = self._load_problems()
        self.results = {}
        self.all_run_summaries = []
    
    def _load_problems(self) -> List[Dict[str, Any]]:
        
        with open("benchmarks/problems.json", 'r') as f:
            problems = json.load(f)
        
        num_problems = self.config.get("problem_selection", {}).get("min_problems", 30)
        selected = problems[:num_problems]
        
        logger.info(f"Loaded {len(selected)} problems for experiment")
        return selected
    
    def _get_config_spec(self, config_name: str) -> Dict[str, Any]:
        
        return self.config["configurations"].get(config_name, {})
    
    def run_tier_1_experiments(self) -> None:
        
        tier_1_configs = self.config["experiment_matrix"]["tier_1_mandatory"]
        seeds = self.config["seeds"]["primary"]
        
        logger.info(f"Running Tier 1 (Mandatory): {tier_1_configs}")
        
        for config_name in tier_1_configs:
            self._run_configuration(config_name, seeds)
    
    def run_tier_2_experiments(self) -> None:
        
        tier_2_configs = self.config["experiment_matrix"]["tier_2_recommended"]
        seeds = self.config["seeds"]["primary"]
        
        logger.info(f"Running Tier 2 (Recommended): {tier_2_configs}")
        
        for config_name in tier_2_configs:
            self._run_configuration(config_name, seeds)
    
    def run_tier_3_experiments(self) -> None:
        
        tier_3_configs = self.config["experiment_matrix"]["tier_3_optional"]
        seeds = self.config["seeds"]["primary"]
        
        logger.info(f"Running Tier 3 (Optional): {tier_3_configs}")
        
        for config_name in tier_3_configs:
            self._run_configuration(config_name, seeds)
    
    def _run_configuration(self, config_name: str, seeds: List[int]) -> None:
        
        spec = self._get_config_spec(config_name)
        temperature = spec.get("temperature", 0.9)
        
        logger.info(f"\nRunning configuration: {config_name} | Temp: {temperature}")
        
        config_results = []
        
        for problem in self.problems:
            for seed in seeds:
                run_id = f"{config_name}_problem_{problem['problem_id']}_seed_{seed}"
                
                try:
                    logs, summary = run_simulation(
                        question=problem["statement"],
                        problem_id=problem["problem_id"],
                        expected_answer=problem["expected_answer"],
                        config=config_name,
                        temperature=temperature,
                        seed=seed,
                        max_rounds=spec.get("max_rounds", 5),
                        run_id=run_id
                    )
                    
                    config_results.append(summary)
                    self.all_run_summaries.append(summary)
                    
                except Exception as e:
                    logger.error(f"Failed to run {run_id}: {str(e)}")
                    continue
        
        self._process_configuration_results(config_name, config_results)
    
    def _process_configuration_results(self, config_name: str, results: List[Dict[str, Any]]) -> None:
        
        if not results:
            logger.warning(f"No results for configuration {config_name}")
            return
        
        accuracies = [1.0 if r["answer_correct"] else 0.0 for r in results]
        convergences = [r.get("convergence_round", 6) if r.get("converged") else 6 for r in results]
        
        config_stats = {
            "configuration": config_name,
            "num_runs": len(results),
            "accuracy_mean": float(np.mean(accuracies)) * 100,
            "accuracy_std": float(np.std(accuracies)) * 100,
            "accuracy_min": float(np.min(accuracies)) * 100,
            "accuracy_max": float(np.max(accuracies)) * 100,
            "convergence_mean": float(np.mean(convergences)),
            "convergence_std": float(np.std(convergences)),
            "convergence_rate": (sum(1 for r in results if r.get("converged")) / len(results)) * 100,
            "contradiction_mean": float(np.mean([r.get("metrics", {}).get("contradiction", {}).get("contradiction_rate", 0) for r in results])),
            "oscillation_mean": float(np.mean([r.get("metrics", {}).get("oscillation", {}).get("oscillation_count", 0) for r in results])),
            "diversity_mean": float(np.mean([r.get("metrics", {}).get("diversity", {}).get("diversity_score", 0) for r in results]))
        }
        
        self.results[config_name] = config_stats
        
        logger.info(f"Configuration {config_name} complete:")
        logger.info(f"  Accuracy: {config_stats['accuracy_mean']:.1f}% ± {config_stats['accuracy_std']:.1f}%")
        logger.info(f"  Convergence: {config_stats['convergence_mean']:.2f} ± {config_stats['convergence_std']:.2f} rounds")
        logger.info(f"  Contradiction Rate: {config_stats['contradiction_mean']:.1f}%")
    
    def compute_hypothesis_tests(self) -> Dict[str, Any]:
        
        hypothesis_results = {}
        
        if "B3" in self.results and "B0" in self.results:
            b3_acc = [r["answer_correct"] for r in self.all_run_summaries if r["configuration"] == "B3"]
            b0_acc = [r["answer_correct"] for r in self.all_run_summaries if r["configuration"] == "B0"]
            
            h1_test = t_test_independent(
                [1 if a else 0 for a in b3_acc],
                [1 if a else 0 for a in b0_acc]
            )
            
            hypothesis_results["H1_verification"] = hypothesis_test_summary(
                "H1",
                h1_test,
                "Verification (B3) improves accuracy over single-agent baseline (B0)"
            )
        
        if "B3" in self.results and "B5" in self.results:
            b3_osc = [r.get("metrics", {}).get("oscillation", {}).get("oscillation_count", 0) for r in self.all_run_summaries if r["configuration"] == "B3"]
            b5_osc = [r.get("metrics", {}).get("oscillation", {}).get("oscillation_count", 0) for r in self.all_run_summaries if r["configuration"] == "B5"]
            
            h2_test = mann_whitney_u_test(b3_osc, b5_osc)
            
            hypothesis_results["H2_coordination"] = hypothesis_test_summary(
                "H2",
                h2_test,
                "Coordinator reduces oscillation (B3 vs B5)"
            )
        
        temperature_groups = []
        temp_configs = ["B6", "B3", "B8"]
        for config in temp_configs:
            accs = [1 if r["answer_correct"] else 0 for r in self.all_run_summaries if r["configuration"] == config]
            if accs:
                temperature_groups.append(accs)
        
        if len(temperature_groups) == 3:
            h3_test = anova_test(temperature_groups)
            
            hypothesis_results["H3_temperature"] = hypothesis_test_summary(
                "H3",
                h3_test,
                "Lower temperature (0.3) improves accuracy vs high temperature (0.95)"
            )
        
        return hypothesis_results
    
    def generate_statistical_summary(self) -> None:
        
        os.makedirs("logs/analysis", exist_ok=True)
        
        config_summary = {}
        for config_name, stats in self.results.items():
            config_summary[config_name] = stats
        
        with open("logs/analysis/configuration_statistics.json", "w") as f:
            json.dump(config_summary, f, indent=2, default=str)
        
        hypothesis_tests = self.compute_hypothesis_tests()
        
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.bool_, np.integer, np.floating)):
                return obj.item()
            return obj
        
        hypothesis_tests = convert_numpy_types(hypothesis_tests)
        
        with open("logs/analysis/hypothesis_tests.json", "w") as f:
            json.dump(hypothesis_tests, f, indent=2)
        
        logger.info("Statistical summary saved to logs/analysis/")
    
    def save_all_results(self) -> None:
        
        os.makedirs("logs/analysis", exist_ok=True)
        
        with open("logs/analysis/all_runs_summary.json", "w") as f:
            json.dump(self.all_run_summaries, f, indent=2)
        
        logger.info(f"Saved {len(self.all_run_summaries)} run summaries")

def main():
    
    runner = ExperimentRunner()
    
    logger.info("="*60)
    logger.info("STARTING TIER 1 EXPERIMENTS (MANDATORY)")
    logger.info("="*60)
    runner.run_tier_1_experiments()
    
    logger.info("\n" + "="*60)
    logger.info("SAVING RESULTS")
    logger.info("="*60)
    runner.save_all_results()
    runner.generate_statistical_summary()
    
    logger.info("\nTier 1 complete. Results saved to logs/analysis/")
    
    logger.info("\n" + "="*60)
    logger.info("STARTING TIER 2 EXPERIMENTS (RECOMMENDED)")
    logger.info("="*60)
    runner.run_tier_2_experiments()
    runner.save_all_results()
    runner.generate_statistical_summary()
    
    logger.info("\nTier 2 complete.")

if __name__ == "__main__":
    main()
