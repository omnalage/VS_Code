import os
import glob
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
import pickle
import datetime
import csv
from collections import defaultdict
import random

class RouterSelectionSystem:
    """
    Comprehensive router selection system implementing both manual and AI recommender processes.
    """
    
    def __init__(self, network_topology=None):
        self.network_topology = network_topology
        self.router_performance_data = {}
        self.manual_selection_history = []
        self.ai_recommendation_history = []
        self.ensemble_model = None
        self.task_migration_leader = None
        self.data_tables = {}
        
    def calculate_router_performance(self, router, network_metrics):
        """
        Calculate comprehensive router performance metrics:
        CO (Cache Occupancy), cmBA (Centrality-based Multi-metric Balanced Assessment), 
        Latency, CHR (Cache Hit Ratio)
        """
        # Cache Occupancy (CO) - percentage of cache used
        cache_occupancy = (len(router.cs) / router.CACHE_LIMIT) * 100
        
        network_metrics = network_metrics or {}
        degree_metrics = network_metrics.get('degree_centrality', {})
        betweenness_metrics = network_metrics.get('betweenness_centrality', {})
        closeness_metrics = network_metrics.get('closeness_centrality', {})
        
        # Calculate cmBA using centrality measures
        cmba_score = self.calculate_cmba_score(router, network_metrics)
        
        # Latency calculation (simulated based on network position and load)
        latency = self.calculate_latency(router, network_metrics)
        
        # Cache Hit Ratio (CHR)
        total_requests = router.cache_hits + router.publisher_hits
        chr_score = (router.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        performance_data = {
            'router_name': router.name,
            'cache_occupancy': cache_occupancy,
            'cmba_score': cmba_score,
            'latency': latency,
            'cache_hit_ratio': chr_score,
            'degree_centrality': degree_metrics.get(router.name, 0),
            'betweenness_centrality': betweenness_metrics.get(router.name, 0),
            'closeness_centrality': closeness_metrics.get(router.name, 0),
            'timestamp': datetime.datetime.now()
        }
        
        self.router_performance_data[router.name] = performance_data
        return performance_data

    def _get_router_by_name(self, routers, router_name):
        return next((router for router in routers if router.name == router_name), None)

    def _calculate_manual_score(self, metrics):
        """
        Manual weighted score used for selecting routers in manual mode.
        """
        return (
            0.20 * metrics['cache_occupancy'] +
            0.30 * metrics['cmba_score'] * 100 +
            0.25 * (100 - metrics['latency'] * 1000) +
            0.25 * metrics['cache_hit_ratio']
        )

    def _save_process_metrics(self, metrics, iteration, policy, mode, score_key, content_request, network_metrics=None):
        """
        Save per-router metrics for a specific path/iteration to CSV.
        """
        if not metrics:
            return None

        base_dir = f"Data_Tables/{mode}_Process"
        os.makedirs(base_dir, exist_ok=True)
        filename = os.path.join(
            base_dir,
            f"{mode.lower()}_performance_{policy}_iter_{iteration}.csv"
        )

        cache_vals = [m['cache_occupancy'] for m in metrics]
        cmba_vals = [m['cmba_score'] for m in metrics]
        latency_vals = [m['latency'] for m in metrics]
        chr_vals = [m['cache_hit_ratio'] for m in metrics]
        score_vals = [m[score_key] for m in metrics]
        degree_vals = [m.get('degree_centrality', 0) for m in metrics]
        betweenness_vals = [m.get('betweenness_centrality', 0) for m in metrics]
        closeness_vals = [m.get('closeness_centrality', 0) for m in metrics]

        averages = {
            'cache': sum(cache_vals) / len(cache_vals),
            'cmba': sum(cmba_vals) / len(cmba_vals),
            'latency': sum(latency_vals) / len(latency_vals),
            'chr': sum(chr_vals) / len(chr_vals),
            'score': sum(score_vals) / len(score_vals),
            'degree': sum(degree_vals) / len(degree_vals),
            'betweenness': sum(betweenness_vals) / len(betweenness_vals),
            'closeness': sum(closeness_vals) / len(closeness_vals)
        }

        header = [
            'Iteration',
            'Policy',
            'Content_Request',
            'Router',
            'Cache_Occupancy',
            'CMBA_Score',
            'Latency',
            'Cache_Hit_Ratio',
            'Manual_Score' if score_key == 'manual_score' else 'Ensemble_Score',
            'Net_Performance',
            'Closeness_Centrality',
            'Degree_Centrality',
            'Betweenness_Centrality'
        ]

        network_metrics = network_metrics or {}
        closeness_map = network_metrics.get('closeness_centrality', {})
        degree_map = network_metrics.get('degree_centrality', {})
        betweenness_map = network_metrics.get('betweenness_centrality', {})

        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for m in metrics:
                router_name = m['router_name']
                closeness_val = closeness_map.get(router_name, m.get('closeness_centrality', 0))
                degree_val = degree_map.get(router_name, m.get('degree_centrality', 0))
                betweenness_val = betweenness_map.get(router_name, m.get('betweenness_centrality', 0))
                writer.writerow([
                    iteration,
                    policy,
                    content_request,
                    router_name,
                    m['cache_occupancy'],
                    m['cmba_score'],
                    m['latency'],
                    m['cache_hit_ratio'],
                    m[score_key],
                    m[score_key],
                    closeness_val,
                    degree_val,
                    betweenness_val
                ])

            writer.writerow([
                iteration,
                policy,
                content_request,
                'PATH_AVERAGE',
                averages['cache'],
                averages['cmba'],
                averages['latency'],
                averages['chr'],
                averages['score'],
                averages['score'],
                averages['closeness'],
                averages['degree'],
                averages['betweenness']
            ])

        return filename

    def process_manual_path(self, routers, traced_path, network_metrics, iteration, policy, content_request):
        """
        Process manual metrics for routers along a traced path,
        save per-iteration CSV, and return the best router.
        """
        if not traced_path:
            return None

        path_router_metrics = []
        for router_name in traced_path:
            router = self._get_router_by_name(routers, router_name)
            if not router:
                continue
            performance = self.calculate_router_performance(router, network_metrics)
            performance['manual_score'] = self._calculate_manual_score(performance)
            path_router_metrics.append(performance)

        if not path_router_metrics:
            return None

        # Save per-iteration table
        self._save_process_metrics(
            path_router_metrics,
            iteration=iteration,
            policy=policy,
            mode='Manual',
            score_key='manual_score',
            content_request=content_request,
            network_metrics=network_metrics
        )

        avg_cmba = sum(metric['cmba_score'] for metric in path_router_metrics) / len(path_router_metrics)
        selected_router = max(path_router_metrics, key=lambda m: m['manual_score'])

        manual_selection_data = {
            'timestamp': datetime.datetime.now(),
            'content_request': content_request,
            'traced_path': traced_path,
            'path_metrics': path_router_metrics,
            'avg_cmba': avg_cmba,
            'selected_router': selected_router['router_name'] if selected_router else None
        }

        self.manual_selection_history.append(manual_selection_data)
        self.save_manual_selection_table(manual_selection_data)

        return {
            'selected_router': selected_router,
            'metrics': path_router_metrics,
            'avg_cmba': avg_cmba
        }

    def process_ai_path(self, routers, traced_path, network_metrics, iteration, policy, content_request):
        """
        Process AI recommender metrics for routers along a traced path,
        apply ensemble learning with pruning, persist CSV, and return the best router.
        """
        if not traced_path:
            return None

        path_router_metrics = []
        for router_name in traced_path:
            router = self._get_router_by_name(routers, router_name)
            if not router:
                continue
            performance = self.calculate_router_performance(router, network_metrics)
            path_router_metrics.append(performance)

        if not path_router_metrics:
            return None

        scored_metrics = self.apply_ensemble_learning(path_router_metrics)
        if not scored_metrics:
            return None

        self._save_process_metrics(
            scored_metrics,
            iteration=iteration,
            policy=policy,
            mode='AI',
            score_key='ensemble_score',
            content_request=content_request,
            network_metrics=network_metrics
        )

        best_router = max(scored_metrics, key=lambda m: m['ensemble_score'])
        self.task_migration_leader = best_router['router_name']

        ai_recommendation_data = {
            'timestamp': datetime.datetime.now(),
            'content_request': content_request,
            'all_router_metrics': scored_metrics,
            'recommended_router': best_router['router_name'],
            'task_migration_leader': self.task_migration_leader,
            'ensemble_score': best_router['ensemble_score']
        }

        self.ai_recommendation_history.append(ai_recommendation_data)
        self.save_ai_recommendation_table(ai_recommendation_data)

        return best_router
    
    def calculate_cmba_score(self, router, network_metrics):
        """
        Calculate Centrality-based Multi-metric Balanced Assessment (cmBA) score
        """
        # Get centrality measures from network metrics
        degree_centrality = network_metrics.get('degree_centrality', {}).get(router.name, 0)
        betweenness_centrality = network_metrics.get('betweenness_centrality', {}).get(router.name, 0)
        closeness_centrality = network_metrics.get('closeness_centrality', {}).get(router.name, 0)
        
        # Calculate cmBA as weighted average of centrality measures
        cmba_score = (
            0.3 * degree_centrality +
            0.4 * betweenness_centrality +
            0.3 * closeness_centrality
        )
        
        return cmba_score
    
    def calculate_latency(self, router, network_metrics):
        """
        Calculate latency based on router position and network load
        """
        base_latency = random.uniform(0.01, 0.1)  # Base latency in seconds
        
        # Adjust based on cache hit ratio (higher CHR = lower latency)
        chr_factor = 1 - (router.cache_hits / max(router.cache_hits + router.publisher_hits, 1))
        
        # Adjust based on network position (central routers have lower latency)
        centrality_factor = network_metrics.get('degree_centrality', {}).get(router.name, 0.5)
        
        latency = base_latency * chr_factor * (2 - centrality_factor)
        return latency
    
    def manual_router_selection(self, routers, network_metrics, content_request):
        """
        Manual Process:
        1. Selection of Path Router through tracing
        2. Calculate cmBA and average
        3. Selection of router to cache the content
        """
        print("=== MANUAL ROUTER SELECTION PROCESS ===")
        
        # Step 1: Path tracing to find potential routers
        traced_path = self.trace_content_path(routers, content_request)
        print(f"Traced path for {content_request}: {traced_path}")

        iteration_id = len(self.manual_selection_history) + 1
        manual_result = self.process_manual_path(
            routers=routers,
            traced_path=traced_path,
            network_metrics=network_metrics,
            iteration=iteration_id,
            policy="Manual_Mode",
            content_request=content_request
        )

        if not manual_result:
            print("Manual process could not evaluate any routers.")
            return None

        path_router_metrics = manual_result['metrics']
        selected_router = manual_result['selected_router']
        avg_cmba = manual_result['avg_cmba']

        for performance in path_router_metrics:
            router_name = performance['router_name']
            print(f"Router {router_name} - CO: {performance['cache_occupancy']:.2f}%, "
                  f"cmBA: {performance['cmba_score']:.4f}, "
                  f"Latency: {performance['latency']:.4f}s, "
                  f"CHR: {performance['cache_hit_ratio']:.2f}%, "
                  f"Score: {performance.get('manual_score', 0):.2f}")

        print(f"Average cmBA for path: {avg_cmba:.4f}")
        print(f"Manual selection: {selected_router['router_name'] if selected_router else 'None'}")
        return selected_router
    
    def trace_content_path(self, routers, content_request):
        """
        Trace the path that content request would take through the network
        """
        path = []
        current_router = routers[0]  # Start from first router
        
        while current_router and len(path) < len(routers):
            path.append(current_router.name)
            
            # Find next hop for this content
            next_hop = current_router.fib.get(content_request)
            if next_hop and hasattr(next_hop, 'name'):
                # Find the router object
                current_router = next((r for r in routers if r.name == next_hop.name), None)
            else:
                break
                
        return path
    
    def select_best_router_manual(self, router_metrics):
        """
        Select the best router using manual criteria (weighted scoring)
        """
        if not router_metrics:
            return None
            
        best_router = None
        best_score = -1
        
        for metrics in router_metrics:
            # Weighted scoring: CO (20%), cmBA (30%), Latency (25%), CHR (25%)
            # Higher CO, cmBA, CHR are better; lower latency is better
            score = self._calculate_manual_score(metrics)
            
            if score > best_score:
                best_score = score
                best_router = metrics
                
        return best_router
    
    def ai_recommender_process(self, routers, network_metrics, content_request):
        """
        AI Recommender Process:
        1. Calculate net performance: CO, cmBA, Latency, CHR of path routers only
        2. Apply Ensemble Learning with Pruning
        3. Recommend appropriate protocol router to cache content
        4. Assign router as computation lead for task migration
        """
        print("=== AI RECOMMENDER PROCESS ===")

        traced_path = self.trace_content_path(routers, content_request)
        print(f"Traced path for AI processing: {traced_path}")
        if not traced_path:
            print("No traced path found for AI processing.")
            return None

        iteration_id = len(self.ai_recommendation_history) + 1
        policy_name = "AI_Mode"

        recommended_router = self.process_ai_path(
            routers=routers,
            traced_path=traced_path,
            network_metrics=network_metrics,
            iteration=iteration_id,
            policy=policy_name,
            content_request=content_request
        )

        if recommended_router:
            print(f"AI recommendation: {recommended_router['router_name']} "
                  f"(Ensemble Score: {recommended_router.get('ensemble_score', 0):.3f})")
            print(f"Task migration leader set to: {self.task_migration_leader}")
        else:
            print("AI process could not determine a router.")

        return recommended_router
    
    def prepare_ai_features(self, router_metrics, network_metrics):
        """
        Prepare features for AI model input
        """
        features = []
        for metrics in router_metrics:
            feature_vector = [
                metrics['cache_occupancy'],
                metrics['cmba_score'],
                metrics['latency'],
                metrics['cache_hit_ratio']
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def create_ensemble_model(self):
        """
        Create ensemble learning model with pruning
        """
        # Create base models
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        dt_model = DecisionTreeClassifier(random_state=42)
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        
        # Create ensemble with voting
        ensemble = VotingClassifier(
            estimators=[
                ('rf', rf_model),
                ('dt', dt_model),
                ('lr', lr_model)
            ],
            voting='soft'
        )
        
        return ensemble

    def apply_ensemble_learning(self, router_metrics):
        """
        Apply ensemble-style scoring with pruning to router metrics.
        """
        if not router_metrics:
            return []

        scored = []
        for metrics in router_metrics:
            score1 = (
                0.25 * metrics['cache_occupancy'] +
                0.35 * metrics['cmba_score'] * 100 +
                0.25 * (100 - metrics['latency'] * 1000) +
                0.15 * metrics['cache_hit_ratio']
            )

            score2 = (
                metrics['cache_hit_ratio'] * 0.4 +
                (100 - metrics['latency'] * 1000) * 0.3 +
                metrics['cmba_score'] * 100 * 0.3
            )

            latency_component = max(metrics['latency'] * 1000, 0.1)
            efficiency = metrics['cache_hit_ratio'] / latency_component
            score3 = efficiency * metrics['cmba_score'] * 100

            ensemble_score = (0.4 * score1) + (0.35 * score2) + (0.25 * score3)
            metrics['ensemble_score'] = ensemble_score
            scored.append(metrics)

        if not scored:
            return []

        max_score = max(item['ensemble_score'] for item in scored)
        threshold = max_score * 0.3
        pruned = [item for item in scored if item['ensemble_score'] >= threshold]
        return pruned
    
    def get_ai_recommendation(self, features, router_metrics):
        """
        Get AI recommendation using ensemble learning
        """
        if len(features) == 0:
            return None
            
        # For now, use a simple scoring approach
        # In a real implementation, this would use the trained ensemble model
        best_router = None
        best_score = -1
        
        for i, metrics in enumerate(router_metrics):
            # AI-based scoring with different weights than manual
            score = (
                0.15 * metrics['cache_occupancy'] +
                0.35 * metrics['cmba_score'] * 100 +
                0.30 * (100 - metrics['latency'] * 1000) +
                0.20 * metrics['cache_hit_ratio']
            )
            
            if score > best_score:
                best_score = score
                best_router = metrics
                
        return best_router
    
    def save_manual_selection_table(self, selection_data):
        """
        Save manual selection data to CSV table
        """
        os.makedirs('Data_Tables/Manual_Selection', exist_ok=True)
        
        filename = f"Data_Tables/Manual_Selection/manual_selection_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Content_Request', 'Traced_Path', 'Selected_Router', 'Avg_cmBA'])
            writer.writerow([
                selection_data['timestamp'],
                selection_data['content_request'],
                ' -> '.join(selection_data['traced_path']),
                selection_data['selected_router'],
                selection_data['avg_cmba']
            ])
        
        print(f"Manual selection table saved: {filename}")
    
    def save_ai_recommendation_table(self, recommendation_data):
        """
        Save AI recommendation data to CSV table
        """
        os.makedirs('Data_Tables/AI_Recommendation', exist_ok=True)
        
        filename = f"Data_Tables/AI_Recommendation/ai_recommendation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Content_Request', 'Recommended_Router', 'Task_Migration_Leader', 'Ensemble_Score'])
            writer.writerow([
                recommendation_data['timestamp'],
                recommendation_data['content_request'],
                recommendation_data['recommended_router'],
                recommendation_data['task_migration_leader'],
                recommendation_data.get('ensemble_score', 0)
            ])
        
        print(f"AI recommendation table saved: {filename}")
    
    def save_performance_summary_table(self, routers, network_metrics):
        """
        Save comprehensive performance summary table
        """
        os.makedirs('Data_Tables/Performance_Summary', exist_ok=True)
        
        filename = f"Data_Tables/Performance_Summary/performance_summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Router', 'Cache_Occupancy', 'cmBA_Score', 'Latency', 'Cache_Hit_Ratio', 'Timestamp'])
            
            for router in routers:
                performance = self.calculate_router_performance(router, network_metrics)
                writer.writerow([
                    performance['router_name'],
                    f"{performance['cache_occupancy']:.2f}%",
                    f"{performance['cmba_score']:.4f}",
                    f"{performance['latency']:.4f}s",
                    f"{performance['cache_hit_ratio']:.2f}%",
                    performance['timestamp']
                ])
        
        print(f"Performance summary table saved: {filename}")
    
    def generate_comparison_report(self):
        """
        Generate comparison report between manual and AI recommendations
        """
        os.makedirs('Data_Tables/Comparison_Reports', exist_ok=True)
        
        filename = f"Data_Tables/Comparison_Reports/comparison_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Content_Request', 'Manual_Selection', 'AI_Recommendation', 'Match'])
            
            # Compare manual and AI selections
            for i, manual_data in enumerate(self.manual_selection_history):
                ai_data = self.ai_recommendation_history[i] if i < len(self.ai_recommendation_history) else None
                
                match = "Yes" if (manual_data['selected_router'] == ai_data['recommended_router']) else "No" if ai_data else "N/A"
                
                writer.writerow([
                    manual_data['timestamp'],
                    manual_data['content_request'],
                    manual_data['selected_router'],
                    ai_data['recommended_router'] if ai_data else "N/A",
                    match
                ])
        
        print(f"Comparison report saved: {filename}")
    
    def get_task_migration_leader(self):
        """
        Get the current task migration leader
        """
        return self.task_migration_leader
    
    def update_network_topology(self, new_topology):
        """
        Update network topology for the selection system
        """
        self.network_topology = new_topology
        print("Network topology updated for router selection system")

    def _load_process_dataframe(self, mode):
        mode = mode.capitalize()
        base_dir = f"Data_Tables/{mode}_Process"
        if not os.path.isdir(base_dir):
            return pd.DataFrame()
        pattern = os.path.join(base_dir, f"{mode.lower()}_performance_*.csv")
        csv_files = sorted(glob.glob(pattern))
        frames = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                df['Iteration'] = pd.to_numeric(df['Iteration'], errors='coerce')
                df['Mode'] = mode
                df['Source_File'] = os.path.basename(csv_file)
                frames.append(df)
            except Exception as exc:
                print(f"[process-load] Failed to read {csv_file}: {exc}")
        if not frames:
            return pd.DataFrame()
        combined = pd.concat(frames, ignore_index=True)
        combined = combined.dropna(subset=['Iteration'])
        combined['Iteration'] = combined['Iteration'].astype(int)
        return combined

    def _plot_metric_lines(self, df, metric, title, ylabel, output_path):
        if metric not in df.columns:
            return
        metric_df = df[['Iteration', 'Router', metric]].copy()
        metric_df[metric] = pd.to_numeric(metric_df[metric], errors='coerce')
        metric_df = metric_df.dropna(subset=[metric])
        if metric_df.empty:
            return
        pivot = metric_df.pivot_table(index='Iteration', columns='Router', values=metric, aggfunc='mean')
        pivot = pivot.dropna(how='all', axis=1).sort_index()
        if pivot.empty:
            return
        plt.figure(figsize=(10, 5))
        for router_name in pivot.columns:
            plt.plot(pivot.index, pivot[router_name], marker='o', linewidth=1.8, label=router_name)
        plt.title(title)
        plt.xlabel('Iteration')
        plt.ylabel(ylabel)
        plt.grid(True, linestyle='--', linewidth=0.5)
        plt.legend(loc='best', fontsize='x-small', frameon=False)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()

    def generate_process_graphs(self, mode="Manual"):
        """
        Generate line graphs for manual or AI process metrics using saved CSV tables.
        """
        mode = mode.capitalize()
        df = self._load_process_dataframe(mode)
        if df.empty:
            print(f"[process-graphs] No data available for {mode} mode.")
            return

        graph_dir = f"Graphs/{mode}_Process"
        os.makedirs(graph_dir, exist_ok=True)

        router_df = df[df['Router'] != 'PATH_AVERAGE'].copy()
        if router_df.empty:
            print(f"[process-graphs] Router-level data unavailable for {mode}.")
            return

        metrics = [
            ('Cache_Occupancy', 'Cache Occupancy (%)'),
            ('CMBA_Score', 'CMBA Score'),
            ('Latency', 'Latency (s)'),
            ('Cache_Hit_Ratio', 'Cache Hit Ratio (%)'),
            ('Net_Performance', 'Net Performance Score'),
            ('Closeness_Centrality', 'Closeness Centrality'),
            ('Degree_Centrality', 'Degree Centrality'),
            ('Betweenness_Centrality', 'Betweenness Centrality')
        ]

        for column, title in metrics:
            output_path = os.path.join(graph_dir, f"{mode.lower()}_{column.lower()}_line.png")
            self._plot_metric_lines(router_df, column, f"{mode} Process - {title}", title, output_path)

    def generate_combined_process_graphs(self):
        """
        Generate combined line graphs comparing Manual vs AI PATH averages for each metric.
        """
        manual_df = self._load_process_dataframe("Manual")
        ai_df = self._load_process_dataframe("AI")

        if manual_df.empty or ai_df.empty:
            print("[combined-graphs] Skipping combined graphs due to missing data.")
            return

        manual_avg = manual_df[manual_df['Router'] == 'PATH_AVERAGE'].copy()
        ai_avg = ai_df[ai_df['Router'] == 'PATH_AVERAGE'].copy()
        if manual_avg.empty or ai_avg.empty:
            print("[combined-graphs] PATH_AVERAGE rows missing; cannot create combined graph.")
            return

        metrics = [
            ('Cache_Occupancy', 'Cache Occupancy (%)'),
            ('CMBA_Score', 'CMBA Score'),
            ('Latency', 'Latency (s)'),
            ('Cache_Hit_Ratio', 'Cache Hit Ratio (%)'),
            ('Net_Performance', 'Net Performance Score'),
            ('Closeness_Centrality', 'Closeness Centrality'),
            ('Degree_Centrality', 'Degree Centrality'),
            ('Betweenness_Centrality', 'Betweenness Centrality')
        ]

        graph_dir = "Graphs/Combined_Process"
        os.makedirs(graph_dir, exist_ok=True)

        for column, title in metrics:
            if column not in manual_avg.columns and column not in ai_avg.columns:
                continue
            plt.figure(figsize=(8, 4.5))
            if column in manual_avg.columns:
                plt.plot(manual_avg['Iteration'], manual_avg[column], marker='o', linewidth=2, label='Manual', color='#1f77b4')
            if column in ai_avg.columns:
                plt.plot(ai_avg['Iteration'], ai_avg[column], marker='s', linewidth=2, label='AI', color='#ff7f0e')
            plt.title(f"Manual vs AI - {title}")
            plt.xlabel('Iteration')
            plt.ylabel(title)
            plt.grid(True, linestyle='--', linewidth=0.5)
            plt.legend()
            plt.tight_layout()
            output_path = os.path.join(graph_dir, f"combined_{column.lower()}_line.png")
            plt.savefig(output_path, dpi=200, bbox_inches='tight')
            plt.close()
