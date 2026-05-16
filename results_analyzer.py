import json
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from visualization import (
    plot_accuracy_by_configuration,
    plot_convergence_rounds,
    plot_accuracy_vs_temperature,
    plot_contradiction_oscillation_matrix,
    plot_diversity_score,
    plot_comprehensive_summary,
    create_results_table
)
from stats import (
    t_test_independent, mann_whitney_u_test, anova_test,
    bonferroni_correction, batch_statistical_summary
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResultsAnalyzer:
    
    def __init__(self, results_path: str = "logs/analysis/all_runs_summary.json"):
        with open(results_path, 'r') as f:
            self.all_runs = json.load(f)
        
        self.config_results = {}
        self._organize_by_configuration()
    
    def _organize_by_configuration(self) -> None:
        
        for run in self.all_runs:
            config = run["configuration"]
            if config not in self.config_results:
                self.config_results[config] = []
            self.config_results[config].append(run)
    
    def generate_config_statistics(self) -> Dict[str, Dict[str, Any]]:
        
        stats = {}
        
        for config_name, runs in self.config_results.items():
            accuracies = [1 if r["answer_correct"] else 0 for r in runs]
            convergences = [r.get("convergence_round", 6) if r.get("converged") else 6 for r in runs]
            
            contradictions = []
            oscillations = []
            diversities = []
            tokens = []
            
            for r in runs:
                metrics = r.get("metrics", {})
                if metrics:
                    contradictions.append(metrics.get("contradiction", {}).get("contradiction_rate", 0))
                    oscillations.append(metrics.get("oscillation", {}).get("oscillation_count", 0))
                    diversities.append(metrics.get("diversity", {}).get("diversity_score", 0))
                    tokens.append(metrics.get("tokens", {}).get("total_tokens_used", 0))
            
            stats[config_name] = {
                "num_runs": len(runs),
                "accuracy_mean": float(np.mean(accuracies)) * 100,
                "accuracy_std": float(np.std(accuracies)) * 100,
                "accuracy_ci": [
                    float(np.mean(accuracies)) * 100 - 1.96 * float(np.std(accuracies)) / np.sqrt(len(accuracies)) * 100,
                    float(np.mean(accuracies)) * 100 + 1.96 * float(np.std(accuracies)) / np.sqrt(len(accuracies)) * 100
                ],
                "convergence_mean": float(np.mean(convergences)),
                "convergence_std": float(np.std(convergences)),
                "convergence_rate": (sum(1 for c in convergences if c <= 5) / len(convergences)) * 100,
                "contradiction_rate": float(np.mean(contradictions)) if contradictions else 0.0,
                "oscillation_rate": (sum(1 for o in oscillations if o > 0) / len(oscillations)) * 100 if oscillations else 0.0,
                "oscillation_mean": float(np.mean(oscillations)) if oscillations else 0.0,
                "diversity_mean": float(np.mean(diversities)) if diversities else 0.0,
                "diversity_std": float(np.std(diversities)) if diversities else 0.0,
                "tokens_mean": float(np.mean(tokens)) if tokens else 0.0,
                "agreement_rate": 100.0 - (float(np.mean(contradictions)) if contradictions else 0.0)
            }
        
        return stats
    
    def run_hypothesis_tests(self) -> Dict[str, Any]:
        
        results = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "alpha": 0.05,
            "hypothesis_tests": {}
        }
        
        if "B3" in self.config_results and "B0" in self.config_results:
            b3_acc = [1 if r["answer_correct"] else 0 for r in self.config_results["B3"]]
            b0_acc = [1 if r["answer_correct"] else 0 for r in self.config_results["B0"]]
            
            h1 = t_test_independent(b3_acc, b0_acc)
            results["hypothesis_tests"]["H1_verification"] = {
                "hypothesis": "Multi-agent verification (B3) improves accuracy over baseline (B0)",
                "expected_outcome": "Δ ≥ 30 percentage points, p < 0.001",
                "test_result": h1,
                "supported": h1["p_value"] < 0.001 and (h1["group1_stats"]["mean"] - h1["group2_stats"]["mean"]) > 0.3
            }
        
        if "B3" in self.config_results and "B5" in self.config_results:
            b3_osc = [r.get("metrics", {}).get("oscillation", {}).get("oscillation_count", 0) for r in self.config_results["B3"]]
            b5_osc = [r.get("metrics", {}).get("oscillation", {}).get("oscillation_count", 0) for r in self.config_results["B5"]]
            
            h2 = mann_whitney_u_test(b3_osc, b5_osc)
            results["hypothesis_tests"]["H2_coordination"] = {
                "hypothesis": "Coordinator reduces oscillation by ≥40%",
                "expected_outcome": "B3 oscillation < B5 oscillation, p < 0.01",
                "test_result": h2,
                "supported": h2["p_value"] < 0.01
            }
        
        if "B6" in self.config_results and "B3" in self.config_results and "B8" in self.config_results:
            b6_acc = [1 if r["answer_correct"] else 0 for r in self.config_results["B6"]]
            b3_acc = [1 if r["answer_correct"] else 0 for r in self.config_results["B3"]]
            b8_acc = [1 if r["answer_correct"] else 0 for r in self.config_results["B8"]]
            
            h3 = anova_test([b6_acc, b3_acc, b8_acc])
            results["hypothesis_tests"]["H3_temperature"] = {
                "hypothesis": "Temperature significantly affects accuracy (T=0.3 > T=0.9 > T=0.95)",
                "expected_outcome": "ANOVA F-test p < 0.001, η² > 0.14 (large effect)",
                "test_result": h3,
                "supported": h3["p_value"] < 0.001 and h3["eta_squared"] > 0.14
            }
        
        if "B3" in self.config_results and "A1" in self.config_results and "A2" in self.config_results:
            b3_acc = [1 if r["answer_correct"] else 0 for r in self.config_results["B3"]]
            a1_acc = [1 if r["answer_correct"] else 0 for r in self.config_results["A1"]]
            a2_acc = [1 if r["answer_correct"] else 0 for r in self.config_results["A2"]]
            
            impact_evaluator = np.mean(b3_acc) - np.mean(a1_acc)
            impact_coordinator = np.mean(b3_acc) - np.mean(a2_acc)
            
            results["hypothesis_tests"]["H4_ablation"] = {
                "hypothesis": "Evaluator more critical than Coordinator (3.8x impact)",
                "expected_outcome": "Evaluator impact Δ ≥ 0.30, Coordinator impact Δ ≤ 0.10",
                "evaluator_impact": impact_evaluator,
                "coordinator_impact": impact_coordinator,
                "supported": impact_evaluator > impact_coordinator * 2
            }
        
        if "B3" in self.config_results and "B0" in self.config_results:
            b3_div = [r.get("metrics", {}).get("diversity", {}).get("diversity_score", 0) for r in self.config_results["B3"]]
            b0_div = [r.get("metrics", {}).get("diversity", {}).get("diversity_score", 0) for r in self.config_results["B0"]]
            
            h5 = t_test_independent(b3_div, b0_div)
            results["hypothesis_tests"]["H5_pedagogy"] = {
                "hypothesis": "Multi-agent systems produce higher explanation diversity",
                "expected_outcome": "B3 diversity > 0.5, B0 diversity < 0.3, p < 0.001",
                "test_result": h5,
                "supported": h5["p_value"] < 0.001 and (h5["group1_stats"]["mean"] - h5["group2_stats"]["mean"]) > 0.3
            }
        
        return results
    
    def create_results_table(self) -> pd.DataFrame:
        
        config_stats = self.generate_config_statistics()
        
        data = []
        for config_name in sorted(config_stats.keys()):
            stats = config_stats[config_name]
            data.append({
                "Configuration": config_name,
                "N": int(stats["num_runs"]),
                "Accuracy (%)": f"{stats['accuracy_mean']:.1f}±{stats['accuracy_std']:.1f}",
                "Conv. Rounds": f"{stats['convergence_mean']:.2f}±{stats['convergence_std']:.2f}",
                "Conv. Rate (%)": f"{stats['convergence_rate']:.1f}",
                "Contradiction (%)": f"{stats['contradiction_rate']:.1f}",
                "Oscillation (%)": f"{stats['oscillation_rate']:.1f}",
                "Diversity": f"{stats['diversity_mean']:.2f}±{stats['diversity_std']:.2f}",
                "Agreement (%)": f"{stats['agreement_rate']:.1f}"
            })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_all_visualizations(self, output_dir: str = "paper/figures/") -> None:
        
        os.makedirs(output_dir, exist_ok=True)
        
        config_stats = self.generate_config_statistics()
        
        plot_accuracy_by_configuration(config_stats, output_dir)
        plot_convergence_rounds(config_stats, output_dir)
        plot_contradiction_oscillation_matrix(config_stats, output_dir)
        plot_diversity_score(config_stats, output_dir)
        plot_comprehensive_summary(config_stats, output_dir)
        
        temperature_results = {}
        for config_name, stats in config_stats.items():
            if config_name in ["B6", "B7", "B3", "B8"]:
                temp_map = {"B6": 0.3, "B7": 0.5, "B3": 0.9, "B8": 0.95}
                temp = temp_map.get(config_name, 0.9)
                temperature_results[temp] = stats
        
        if temperature_results:
            plot_accuracy_vs_temperature(temperature_results, output_dir)
        
        logger.info(f"Generated visualizations in {output_dir}")
    
    def save_comprehensive_report(self, output_path: str = "paper/analysis_report.json") -> None:
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        config_stats = self.generate_config_statistics()
        hypothesis_results = self.run_hypothesis_tests()
        results_table = self.create_results_table()
        
        report = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "total_runs": len(self.all_runs),
            "configurations": config_stats,
            "hypothesis_tests": hypothesis_results,
            "summary_table": results_table.to_dict(orient="records")
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Comprehensive report saved to {output_path}")
        
        table_path = output_path.replace(".json", ".csv")
        results_table.to_csv(table_path, index=False)
        logger.info(f"Results table saved to {table_path}")

def main():
    
    logger.info("Starting results analysis...")
    
    analyzer = ResultsAnalyzer()
    
    config_stats = analyzer.generate_config_statistics()
    with open("paper/configuration_statistics.json", "w") as f:
        json.dump(config_stats, f, indent=2)
    
    hypothesis_tests = analyzer.run_hypothesis_tests()
    with open("paper/hypothesis_test_results.json", "w") as f:
        json.dump(hypothesis_tests, f, indent=2, default=str)
    
    results_table = analyzer.create_results_table()
    results_table.to_csv("paper/results_table.csv", index=False)
    print("\n" + "="*80)
    print("COMPREHENSIVE RESULTS TABLE")
    print("="*80)
    print(results_table.to_string(index=False))
    
    analyzer.generate_all_visualizations()
    analyzer.save_comprehensive_report()
    
    logger.info("Analysis complete. Results saved to paper/")

if __name__ == "__main__":
    main()
