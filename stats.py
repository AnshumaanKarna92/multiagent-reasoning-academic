import numpy as np
from scipy import stats
from typing import List, Dict, Tuple, Any
import json

def t_test_independent(group1: List[float], group2: List[float], alpha: float = 0.05) -> Dict[str, Any]:
    
    t_stat, p_value = stats.ttest_ind(group1, group2)
    
    mean_diff = np.mean(group1) - np.mean(group2)
    pooled_std = np.sqrt((np.std(group1)**2 + np.std(group2)**2) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0.0
    
    ci_lower = mean_diff - 1.96 * pooled_std / np.sqrt(len(group1) + len(group2))
    ci_upper = mean_diff + 1.96 * pooled_std / np.sqrt(len(group1) + len(group2))
    
    return {
        "test_type": "independent_t_test",
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "significant": p_value < alpha,
        "alpha": alpha,
        "mean_difference": float(mean_diff),
        "cohens_d": float(cohens_d),
        "effect_size_interpretation": interpret_cohens_d(cohens_d),
        "confidence_interval_95": [float(ci_lower), float(ci_upper)],
        "group1_stats": {
            "mean": float(np.mean(group1)),
            "std": float(np.std(group1)),
            "n": len(group1)
        },
        "group2_stats": {
            "mean": float(np.mean(group2)),
            "std": float(np.std(group2)),
            "n": len(group2)
        }
    }

def mann_whitney_u_test(group1: List[float], group2: List[float], alpha: float = 0.05) -> Dict[str, Any]:
    
    u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
    
    cliff_delta = compute_cliffs_delta(group1, group2)
    
    return {
        "test_type": "mann_whitney_u",
        "u_statistic": float(u_stat),
        "p_value": float(p_value),
        "significant": p_value < alpha,
        "alpha": alpha,
        "cliffs_delta": cliff_delta,
        "effect_size_interpretation": interpret_cliffs_delta(cliff_delta),
        "group1_stats": {
            "median": float(np.median(group1)),
            "mean": float(np.mean(group1)),
            "n": len(group1)
        },
        "group2_stats": {
            "median": float(np.median(group2)),
            "mean": float(np.mean(group2)),
            "n": len(group2)
        }
    }

def anova_test(groups: List[List[float]], alpha: float = 0.05) -> Dict[str, Any]:
    
    f_stat, p_value = stats.f_oneway(*groups)
    
    grand_mean = np.mean(np.concatenate(groups))
    ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
    ss_total = sum((x - grand_mean)**2 for g in groups for x in g)
    
    eta_squared = ss_between / ss_total if ss_total > 0 else 0.0
    
    return {
        "test_type": "anova",
        "f_statistic": float(f_stat),
        "p_value": float(p_value),
        "significant": p_value < alpha,
        "alpha": alpha,
        "eta_squared": float(eta_squared),
        "effect_size_interpretation": interpret_eta_squared(eta_squared),
        "num_groups": len(groups),
        "group_stats": [
            {
                "group_index": i,
                "mean": float(np.mean(g)),
                "std": float(np.std(g)),
                "n": len(g)
            }
            for i, g in enumerate(groups)
        ]
    }

def tukey_hsd(groups: List[List[float]], alpha: float = 0.05) -> Dict[str, Any]:
    
    from scipy.stats import tukey_hsd as tukey_hsd_test
    
    try:
        result = tukey_hsd_test(*groups)
        
        pairwise_comparisons = []
        group_means = [np.mean(g) for g in groups]
        
        for i in range(len(groups)):
            for j in range(i+1, len(groups)):
                pairwise_comparisons.append({
                    "group_i": i,
                    "group_j": j,
                    "mean_diff": float(group_means[i] - group_means[j]),
                    "p_value": float(result.pvalue[i, j]),
                    "significant": result.pvalue[i, j] < alpha
                })
        
        return {
            "test_type": "tukey_hsd",
            "pairwise_comparisons": pairwise_comparisons,
            "alpha": alpha
        }
    except:
        return {
            "test_type": "tukey_hsd",
            "pairwise_comparisons": [],
            "error": "Tukey HSD computation failed"
        }

def bonferroni_correction(p_values: List[float], alpha: float = 0.05) -> Dict[str, Any]:
    
    num_tests = len(p_values)
    bonferroni_alpha = alpha / num_tests
    
    corrected_results = [
        {
            "test_index": i,
            "original_p_value": float(p),
            "bonferroni_alpha": float(bonferroni_alpha),
            "significant_original": p < alpha,
            "significant_corrected": p < bonferroni_alpha
        }
        for i, p in enumerate(p_values)
    ]
    
    return {
        "correction_type": "bonferroni",
        "num_tests": num_tests,
        "original_alpha": alpha,
        "corrected_alpha": float(bonferroni_alpha),
        "tests": corrected_results
    }

def fdr_correction(p_values: List[float], alpha: float = 0.05) -> Dict[str, Any]:
    
    from scipy.stats import false_discovery_control
    
    try:
        rejected = false_discovery_control(p_values, alpha=alpha)
        
        return {
            "correction_type": "fdr",
            "num_tests": len(p_values),
            "alpha": alpha,
            "rejected": [bool(r) for r in rejected],
            "num_rejected": int(sum(rejected))
        }
    except:
        return {
            "correction_type": "fdr",
            "num_tests": len(p_values),
            "error": "FDR correction failed"
        }

def compute_cliffs_delta(group1: List[float], group2: List[float]) -> float:
    
    n1, n2 = len(group1), len(group2)
    
    dominance_sum = 0
    for x in group1:
        for y in group2:
            if x > y:
                dominance_sum += 1
            elif x < y:
                dominance_sum -= 1
    
    delta = dominance_sum / (n1 * n2)
    return float(delta)

def interpret_cohens_d(d: float) -> str:
    
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"

def interpret_cliffs_delta(delta: float) -> str:
    
    abs_delta = abs(delta)
    if abs_delta < 0.147:
        return "negligible"
    elif abs_delta < 0.330:
        return "small"
    elif abs_delta < 0.474:
        return "medium"
    else:
        return "large"

def interpret_eta_squared(eta_sq: float) -> str:
    
    if eta_sq < 0.01:
        return "negligible"
    elif eta_sq < 0.06:
        return "small"
    elif eta_sq < 0.14:
        return "medium"
    else:
        return "large"

def hypothesis_test_summary(
    h_id: str,
    test_result: Dict[str, Any],
    h_statement: str,
    alpha: float = 0.05
) -> Dict[str, Any]:
    
    return {
        "hypothesis_id": h_id,
        "hypothesis_statement": h_statement,
        "test_performed": test_result.get("test_type", "unknown"),
        "p_value": test_result.get("p_value"),
        "alpha": alpha,
        "hypothesis_supported": test_result.get("p_value", 1.0) < alpha,
        "effect_size": test_result.get("cohens_d") or test_result.get("eta_squared") or test_result.get("cliffs_delta"),
        "effect_interpretation": test_result.get("effect_size_interpretation", "unknown"),
        "full_result": test_result
    }

def batch_statistical_summary(
    configurations: Dict[str, List[float]],
    alpha: float = 0.05
) -> Dict[str, Any]:
    
    summary = {
        "num_configurations": len(configurations),
        "alpha": alpha,
        "pairwise_tests": []
    }
    
    config_names = list(configurations.keys())
    
    for i in range(len(config_names)):
        for j in range(i+1, len(config_names)):
            config_i = config_names[i]
            config_j = config_names[j]
            
            group_i = configurations[config_i]
            group_j = configurations[config_j]
            
            t_result = t_test_independent(group_i, group_j, alpha)
            
            summary["pairwise_tests"].append({
                "comparison": f"{config_i} vs {config_j}",
                "t_test": t_result
            })
    
    return summary
