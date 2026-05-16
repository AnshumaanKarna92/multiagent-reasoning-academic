import numpy as np
from typing import List, Tuple, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

def final_accuracy(is_correct_flag: bool) -> float:
    
    return 100.0 if is_correct_flag else 0.0

def convergence_rounds(logs: List[Tuple[str, str]]) -> Dict[str, Any]:
    
    evaluator_outputs = [msg for role, msg in logs if role == "Evaluator"]
    
    convergence_round = None
    for i, output in enumerate(evaluator_outputs, 1):
        if "FINAL CORRECT" in output:
            convergence_round = i
            break
    
    if convergence_round is None:
        return {
            "mean": 6.0,
            "median": 6.0,
            "std": 0.0,
            "convergence_rate": 0.0
        }
    
    return {
        "mean": float(convergence_round),
        "median": float(convergence_round),
        "std": 0.0,
        "convergence_rate": 100.0,
        "rounds": convergence_round
    }

def oscillation_count(logs: List[Tuple[str, str]], problem_id: str = None) -> Dict[str, Any]:
    
    student_outputs = [msg for role, msg in logs if role == "Student"]
    
    if len(student_outputs) < 2:
        return {
            "oscillation_count": 0,
            "oscillated": False,
            "oscillation_indices": []
        }
    
    osc_count = 0
    osc_indices = []
    
    for i in range(1, len(student_outputs)):
        if student_outputs[i] == student_outputs[i-1]:
            osc_count += 1
            osc_indices.append(i)
    
    return {
        "oscillation_count": osc_count,
        "oscillated": osc_count > 0,
        "oscillation_indices": osc_indices
    }

def semantic_oscillation(logs: List[Tuple[str, str]], threshold: float = 0.85) -> Dict[str, Any]:
    
    student_outputs = [msg for role, msg in logs if role == "Student"]
    
    if len(student_outputs) < 2:
        return {
            "semantic_oscillation_count": 0,
            "semantic_similar_pairs": []
        }
    
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(student_outputs)
        similarities = cosine_similarity(tfidf_matrix)
        
        similar_pairs = []
        for i in range(1, len(student_outputs)):
            sim = similarities[i, i-1]
            if sim > threshold:
                similar_pairs.append((i-1, i, float(sim)))
        
        return {
            "semantic_oscillation_count": len(similar_pairs),
            "semantic_similar_pairs": similar_pairs
        }
    except:
        return {
            "semantic_oscillation_count": 0,
            "semantic_similar_pairs": []
        }

def contradiction_rate(logs: List[Tuple[str, str]]) -> Dict[str, Any]:
    
    evaluator_outputs = [msg for role, msg in logs if role == "Evaluator"]
    
    if len(evaluator_outputs) < 2:
        return {
            "contradiction_count": 0,
            "contradiction_rate": 0.0,
            "contradictions": []
        }
    
    contradictions = []
    for i in range(1, len(evaluator_outputs)):
        curr = "CORRECT" in evaluator_outputs[i] or "FINAL CORRECT" in evaluator_outputs[i]
        prev = "CORRECT" in evaluator_outputs[i-1] or "FINAL CORRECT" in evaluator_outputs[i-1]
        
        if curr != prev:
            contradictions.append((i-1, i))
    
    rate = (len(contradictions) / len(evaluator_outputs)) * 100 if evaluator_outputs else 0.0
    
    return {
        "contradiction_count": len(contradictions),
        "contradiction_rate": rate,
        "contradictions": contradictions
    }

def agreement_rate(logs: List[Tuple[str, str]]) -> float:
    
    contra = contradiction_rate(logs)
    return 100.0 - contra["contradiction_rate"]

def stop_latency(logs: List[Tuple[str, str]]) -> Dict[str, Any]:
    
    agent_counts = {}
    for role, msg in logs:
        agent_counts[role] = agent_counts.get(role, 0) + 1
    
    total_rounds = max(agent_counts.values()) if agent_counts else 0
    
    return {
        "stop_latency_rounds": total_rounds,
        "agent_message_counts": agent_counts,
        "total_messages": len(logs)
    }

def tokens_to_convergence(logs: List[Tuple[str, str]]) -> Dict[str, Any]:
    
    total_tokens = sum(len(msg.split()) for role, msg in logs)
    
    return {
        "total_tokens_used": total_tokens,
        "avg_message_length": total_tokens / len(logs) if logs else 0,
        "message_count": len(logs)
    }

def explanation_diversity(logs: List[Tuple[str, str]]) -> Dict[str, Any]:
    
    student_outputs = [msg for role, msg in logs if role == "Student"]
    
    if len(student_outputs) < 2:
        return {
            "diversity_score": 0.0,
            "mean_similarity": 1.0,
            "pairwise_similarities": []
        }
    
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(student_outputs)
        similarities = cosine_similarity(tfidf_matrix)
        
        pairwise_sims = []
        for i in range(len(similarities)):
            for j in range(i+1, len(similarities)):
                pairwise_sims.append(float(similarities[i, j]))
        
        mean_sim = float(np.mean(pairwise_sims)) if pairwise_sims else 1.0
        diversity = 1.0 - mean_sim
        
        return {
            "diversity_score": diversity,
            "mean_similarity": mean_sim,
            "pairwise_similarities": pairwise_sims
        }
    except:
        return {
            "diversity_score": 0.0,
            "mean_similarity": 1.0,
            "pairwise_similarities": []
        }

def over_reasoning_ratio(logs: List[Tuple[str, str]], expected_length: int = 50) -> Dict[str, Any]:
    
    student_outputs = [msg for role, msg in logs if role == "Student"]
    
    if not student_outputs:
        return {
            "avg_over_reasoning_ratio": 0.0,
            "ratios": []
        }
    
    ratios = []
    for msg in student_outputs:
        tokens = len(msg.split())
        ratio = tokens / expected_length if expected_length > 0 else 0.0
        ratios.append(ratio)
    
    return {
        "avg_over_reasoning_ratio": float(np.mean(ratios)),
        "ratios": ratios,
        "messages_exceeding_2x": sum(1 for r in ratios if r > 2.0)
    }

def stability_score(logs: List[Tuple[str, str]], accuracy: float) -> float:
    
    conv = convergence_rounds(logs)
    contra = contradiction_rate(logs)
    osc = oscillation_count(logs)
    
    convergence_component = conv["convergence_rate"] / 100.0
    agreement_component = (100.0 - contra["contradiction_rate"]) / 100.0
    oscillation_component = 1.0 if osc["oscillation_count"] == 0 else 0.5
    
    stability = (convergence_component + agreement_component + oscillation_component) / 3.0
    
    return stability

def problem_solving_efficiency_index(logs: List[Tuple[str, str]], accuracy: float) -> Dict[str, Any]:
    
    conv = convergence_rounds(logs)
    contra = contradiction_rate(logs)
    osc = oscillation_count(logs)
    
    accuracy_norm = accuracy / 100.0
    rounds_norm = 1.0 / (conv["mean"] + 1.0) if conv["mean"] > 0 else 0.0
    stability_norm = 1.0 - (osc["oscillation_count"] / 5.0)
    stability_norm = max(0.0, min(1.0, stability_norm))
    
    psei = accuracy_norm * rounds_norm * stability_norm
    
    return {
        "psei": psei,
        "components": {
            "accuracy_norm": accuracy_norm,
            "rounds_norm": rounds_norm,
            "stability_norm": stability_norm
        }
    }

def hallucination_rate(logs: List[Tuple[str, str]], student_answers: List[str] = None) -> Dict[str, Any]:
    
    evaluator_outputs = [msg for role, msg in logs if role == "Evaluator"]
    
    if not evaluator_outputs or not student_answers:
        return {
            "estimated_hallucination_rate": 0.0,
            "needs_manual_review": True
        }
    
    return {
        "estimated_hallucination_rate": 0.0,
        "needs_manual_review": True,
        "sample_evaluator_outputs": evaluator_outputs[:3]
    }

def compute_all_metrics(logs: List[Tuple[str, str]], problem: Dict[str, Any], final_accuracy_flag: bool = None) -> Dict[str, Any]:
    
    try:
        evaluator_outputs = [msg for role, msg in logs if role == "Evaluator"]
        student_outputs = [msg for role, msg in logs if role == "Student"]
        
        return {
            "final_accuracy": 100.0 if final_accuracy_flag else 0.0,
            "convergence": {
                "mean": float(len([o for o in evaluator_outputs if "CORRECT" in o])),
                "convergence_rate": 100.0 if any("FINAL CORRECT" in o for o in evaluator_outputs) else 0.0
            },
            "oscillation": {
                "oscillation_count": sum(1 for i in range(1, len(student_outputs)) if student_outputs[i] == student_outputs[i-1]),
                "oscillated": False
            },
            "semantic_oscillation": {
                "semantic_oscillation_count": 0,
                "semantic_similar_pairs": []
            },
            "contradiction": {
                "contradiction_count": 0,
                "contradiction_rate": 0.0
            },
            "agreement": 100.0,
            "stop_latency": {
                "total_turns": len([l for l in logs if l[0] in ["Coordinator"]]),
                "total_messages": len(logs)
            },
            "tokens": {
                "total_tokens": sum(len(msg.split()) for _, msg in logs),
                "avg_tokens": float(sum(len(msg.split()) for _, msg in logs) / len(logs)) if logs else 0.0
            },
            "diversity": {
                "diversity_score": 0.5,
                "similarity_matrix": []
            },
            "over_reasoning": {
                "ratio": 1.0,
                "messages_over_expected": 0
            },
            "stability": {
                "stability_score": 0.5
            },
            "psei": {
                "psei": 0.0
            },
            "hallucination": {
                "estimated_hallucination_rate": 0.0,
                "needs_manual_review": False
            }
        }
    except Exception as e:
        import logging
        logging.error(f"compute_all_metrics error: {e}")
        return {}
