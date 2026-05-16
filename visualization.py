import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Any
import os

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def plot_accuracy_by_configuration(config_results: Dict[str, Dict[str, float]], output_path: str = "figures/") -> None:
    
    os.makedirs(output_path, exist_ok=True)
    
    configs = list(config_results.keys())
    means = [config_results[c]["accuracy_mean"] for c in configs]
    stds = [config_results[c]["accuracy_std"] for c in configs]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x_pos = np.arange(len(configs))
    ax.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color='steelblue', edgecolor='black')
    
    ax.set_xlabel('Configuration', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('Final Accuracy by Configuration', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(configs, rotation=45, ha='right')
    ax.set_ylim(0, 105)
    
    for i, (mean, std) in enumerate(zip(means, stds)):
        ax.text(i, mean + std + 2, f'{mean:.1f}%', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{output_path}figure1_accuracy_by_config.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_convergence_rounds(config_results: Dict[str, Dict[str, float]], output_path: str = "figures/") -> None:
    
    os.makedirs(output_path, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    configs = list(config_results.keys())
    means = [config_results[c]["convergence_mean"] for c in configs]
    stds = [config_results[c]["convergence_std"] for c in configs]
    
    x_pos = np.arange(len(configs))
    ax.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color='coral', edgecolor='black')
    
    ax.set_xlabel('Configuration', fontsize=12, fontweight='bold')
    ax.set_ylabel('Convergence Rounds', fontsize=12, fontweight='bold')
    ax.set_title('Convergence Rounds by Configuration', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(configs, rotation=45, ha='right')
    ax.set_ylim(0, 6)
    
    for i, (mean, std) in enumerate(zip(means, stds)):
        ax.text(i, mean + std + 0.2, f'{mean:.2f}', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{output_path}figure2_convergence_rounds.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_accuracy_vs_temperature(temperature_results: Dict[float, Dict[str, float]], output_path: str = "figures/") -> None:
    
    os.makedirs(output_path, exist_ok=True)
    
    temps = sorted(temperature_results.keys())
    means = [temperature_results[t]["accuracy_mean"] for t in temps]
    stds = [temperature_results[t]["accuracy_std"] for t in temps]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.errorbar(temps, means, yerr=stds, marker='o', linestyle='-', linewidth=2, markersize=8, capsize=5, color='green', label='Accuracy')
    
    z = np.polyfit(temps, means, 2)
    p = np.poly1d(z)
    temps_smooth = np.linspace(min(temps), max(temps), 100)
    ax.plot(temps_smooth, p(temps_smooth), '--', alpha=0.5, color='green', label='Trend')
    
    ax.set_xlabel('Temperature', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('Accuracy vs. Temperature', fontsize=14, fontweight='bold')
    ax.set_ylim(40, 95)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f"{output_path}figure3_accuracy_vs_temperature.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_contradiction_oscillation_matrix(config_results: Dict[str, Dict[str, float]], output_path: str = "figures/") -> None:
    
    os.makedirs(output_path, exist_ok=True)
    
    configs = list(config_results.keys())
    contradiction_rates = [config_results[c].get("contradiction_rate", 0) for c in configs]
    oscillation_rates = [config_results[c].get("oscillation_rate", 0) for c in configs]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x_pos = np.arange(len(configs))
    width = 0.35
    
    ax.bar(x_pos - width/2, contradiction_rates, width, label='Contradiction Rate (%)', alpha=0.7, color='red', edgecolor='black')
    ax.bar(x_pos + width/2, oscillation_rates, width, label='Oscillation Rate (%)', alpha=0.7, color='orange', edgecolor='black')
    
    ax.set_xlabel('Configuration', fontsize=12, fontweight='bold')
    ax.set_ylabel('Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Contradiction and Oscillation Rates by Configuration', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(configs, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f"{output_path}figure4_contradiction_oscillation.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_diversity_score(config_results: Dict[str, Dict[str, float]], output_path: str = "figures/") -> None:
    
    os.makedirs(output_path, exist_ok=True)
    
    configs = list(config_results.keys())
    diversity = [config_results[c].get("diversity_mean", 0) for c in configs]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x_pos = np.arange(len(configs))
    ax.bar(x_pos, diversity, alpha=0.7, color='purple', edgecolor='black')
    
    ax.set_xlabel('Configuration', fontsize=12, fontweight='bold')
    ax.set_ylabel('Diversity Score (0-1)', fontsize=12, fontweight='bold')
    ax.set_title('Explanation Diversity by Configuration', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(configs, rotation=45, ha='right')
    ax.set_ylim(0, 1)
    ax.axhline(y=0.5, color='green', linestyle='--', label='Diversity Threshold', alpha=0.5)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f"{output_path}figure5_diversity.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_comprehensive_summary(all_results: Dict[str, Dict[str, Any]], output_path: str = "figures/") -> None:
    
    os.makedirs(output_path, exist_ok=True)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Comprehensive Multi-Agent System Analysis', fontsize=16, fontweight='bold')
    
    configs = list(all_results.keys())
    
    accuracy = [all_results[c]["accuracy_mean"] for c in configs]
    convergence = [all_results[c]["convergence_mean"] for c in configs]
    contradiction = [all_results[c].get("contradiction_rate", 0) for c in configs]
    oscillation = [all_results[c].get("oscillation_rate", 0) for c in configs]
    diversity = [all_results[c].get("diversity_mean", 0) for c in configs]
    tokens = [all_results[c].get("tokens_mean", 0) for c in configs]
    
    x_pos = np.arange(len(configs))
    
    axes[0, 0].bar(x_pos, accuracy, alpha=0.7, color='steelblue')
    axes[0, 0].set_title('Accuracy (%)')
    axes[0, 0].set_xticks(x_pos)
    axes[0, 0].set_xticklabels(configs, rotation=45, ha='right', fontsize=8)
    axes[0, 0].set_ylim(0, 105)
    
    axes[0, 1].bar(x_pos, convergence, alpha=0.7, color='coral')
    axes[0, 1].set_title('Convergence Rounds')
    axes[0, 1].set_xticks(x_pos)
    axes[0, 1].set_xticklabels(configs, rotation=45, ha='right', fontsize=8)
    
    axes[0, 2].bar(x_pos, contradiction, alpha=0.7, color='red')
    axes[0, 2].set_title('Contradiction Rate (%)')
    axes[0, 2].set_xticks(x_pos)
    axes[0, 2].set_xticklabels(configs, rotation=45, ha='right', fontsize=8)
    
    axes[1, 0].bar(x_pos, oscillation, alpha=0.7, color='orange')
    axes[1, 0].set_title('Oscillation Rate (%)')
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(configs, rotation=45, ha='right', fontsize=8)
    
    axes[1, 1].bar(x_pos, diversity, alpha=0.7, color='purple')
    axes[1, 1].set_title('Diversity Score')
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(configs, rotation=45, ha='right', fontsize=8)
    axes[1, 1].set_ylim(0, 1)
    
    axes[1, 2].bar(x_pos, tokens, alpha=0.7, color='green')
    axes[1, 2].set_title('Avg Tokens Used')
    axes[1, 2].set_xticks(x_pos)
    axes[1, 2].set_xticklabels(configs, rotation=45, ha='right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f"{output_path}figure_comprehensive_summary.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_results_table(config_results: Dict[str, Dict[str, float]], output_path: str = "tables/") -> None:
    
    os.makedirs(output_path, exist_ok=True)
    
    data = []
    for config, metrics in config_results.items():
        data.append({
            'Configuration': config,
            'Accuracy (%)': f"{metrics['accuracy_mean']:.1f} ± {metrics['accuracy_std']:.1f}",
            'Conv. Rounds': f"{metrics['convergence_mean']:.2f} ± {metrics['convergence_std']:.2f}",
            'Contradiction (%)': f"{metrics.get('contradiction_rate', 0):.1f}",
            'Oscillation (%)': f"{metrics.get('oscillation_rate', 0):.1f}",
            'Diversity': f"{metrics.get('diversity_mean', 0):.2f}",
            'Agreement (%)': f"{100 - metrics.get('contradiction_rate', 0):.1f}"
        })
    
    df = pd.DataFrame(data)
    df.to_csv(f"{output_path}table1_aggregate_metrics.csv", index=False)
    
    return df
