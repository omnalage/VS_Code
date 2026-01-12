import os
import csv
import datetime
import random
import math

class EnhancedRouterSelectionSystem:
    """
    Enhanced router selection system with clearly distinct manual and AI processes.
    User can choose which process to use.
    """
    
    def __init__(self):
        self.manual_selection_history = []
        self.ai_recommendation_history = []
        self.task_migration_leader = None
        self.data_tables = {}
        
    def display_process_menu(self):
        """
        Display menu for user to choose between manual and AI processes
        """
        print("\n" + "="*60)
        print("ROUTER SELECTION SYSTEM")
        print("="*60)
        print("Choose the process you want to use:")
        print("1. MANUAL PROCESS")
        print("   - Path tracing through routers")
        print("   - Calculate cmBA and average")
        print("   - Manual router selection for caching")
        print()
        print("2. AI RECOMMENDER PROCESS")
        print("   - Calculate net performance (CO, cmBA, Latency, CHR)")
        print("   - Apply Ensemble Learning with Pruning")
        print("   - AI recommendation for router selection")
        print("   - Assign task migration leader")
        print()
        print("3. COMPARISON MODE")
        print("   - Run both processes and compare results")
        print()
        
        while True:
            try:
                choice = int(input("Enter your choice (1, 2, or 3): "))
                if choice in [1, 2, 3]:
                    return choice
                else:
                    print("Please enter 1, 2, or 3")
            except ValueError:
                print("Please enter a valid number")
    
    def manual_process(self, routers, network_metrics, content_request):
        """
        MANUAL PROCESS:
        1. Selection of Path Router through tracing
        2. Calculate cmBA and also average
        3. Selection of router to cache the content
        """
        print("\n" + "="*50)
        print("MANUAL PROCESS - ROUTER SELECTION")
        print("="*50)
        
        # Step 1: Path tracing
        print(f"Step 1: Tracing path for content request: {content_request}")
        traced_path = self.trace_content_path_manual(routers, content_request)
        print(f"Traced path: {' -> '.join(traced_path)}")
        
        # Step 2: Calculate cmBA for each router in path
        print(f"\nStep 2: Calculating cmBA for routers in path...")
        path_router_metrics = []
        for router_name in traced_path:
            router = next((r for r in routers if r.name == router_name), None)
            if router:
                # Calculate manual metrics
                cache_occupancy = (len(router.cs) / router.CACHE_LIMIT) * 100
                cmba_score = self.calculate_manual_cmba(router, network_metrics)
                latency = self.calculate_manual_latency(router)
                cache_hit_ratio = self.calculate_manual_chr(router)
                
                metrics = {
                    'router_name': router_name,
                    'cache_occupancy': cache_occupancy,
                    'cmba_score': cmba_score,
                    'latency': latency,
                    'cache_hit_ratio': cache_hit_ratio
                }
                path_router_metrics.append(metrics)
                
                print(f"  {router_name}: CO={cache_occupancy:.1f}%, cmBA={cmba_score:.3f}, "
                      f"Latency={latency:.3f}s, CHR={cache_hit_ratio:.1f}%")
        
        # Step 3: Calculate average cmBA
        if path_router_metrics:
            avg_cmba = sum(metric['cmba_score'] for metric in path_router_metrics) / len(path_router_metrics)
            print(f"\nStep 3: Average cmBA for path: {avg_cmba:.3f}")
        
        # Step 4: Manual router selection (simple weighted scoring)
        print(f"\nStep 4: Manual router selection...")
        selected_router = self.select_router_manual(path_router_metrics)
        
        if selected_router:
            print(f"MANUAL SELECTION RESULT: {selected_router['router_name']}")
            print(f"  - Cache Occupancy: {selected_router['cache_occupancy']:.1f}%")
            print(f"  - cmBA Score: {selected_router['cmba_score']:.3f}")
            print(f"  - Latency: {selected_router['latency']:.3f}s")
            print(f"  - Cache Hit Ratio: {selected_router['cache_hit_ratio']:.1f}%")
        else:
            print("No router selected")
        
        # Save manual selection data
        manual_data = {
            'timestamp': datetime.datetime.now(),
            'content_request': content_request,
            'traced_path': traced_path,
            'path_metrics': path_router_metrics,
            'avg_cmba': avg_cmba if path_router_metrics else 0,
            'selected_router': selected_router['router_name'] if selected_router else None
        }
        
        self.manual_selection_history.append(manual_data)
        self.save_manual_selection_table(manual_data)
        
        return selected_router
    
    def ai_recommender_process(self, routers, network_metrics, content_request):
        """
        AI RECOMMENDER PROCESS:
        1. Calculate net performance: CO, cmBA, Latency, CHR of path routers only
        2. Apply Ensemble Learning with Pruning
        3. Recommend appropriate protocol router to cache content
        4. Assign router as computation lead for task migration
        """
        print("\n" + "="*50)
        print("AI RECOMMENDER PROCESS")
        print("="*50)
        
        # Step 1: Calculate performance for all routers
        print(f"Step 1: Calculating net performance for all routers...")
        all_router_metrics = []
        for router in routers:
            # AI-based performance calculation (different from manual)
            cache_occupancy = self.calculate_ai_cache_occupancy(router)
            cmba_score = self.calculate_ai_cmba(router, network_metrics)
            latency = self.calculate_ai_latency(router, network_metrics)
            cache_hit_ratio = self.calculate_ai_chr(router)
            
            metrics = {
                'router_name': router.name,
                'cache_occupancy': cache_occupancy,
                'cmba_score': cmba_score,
                'latency': latency,
                'cache_hit_ratio': cache_hit_ratio
            }
            all_router_metrics.append(metrics)
            
            print(f"  {router.name}: CO={cache_occupancy:.1f}%, cmBA={cmba_score:.3f}, "
                  f"Latency={latency:.3f}s, CHR={cache_hit_ratio:.1f}%")
        
        # Step 2: Apply Ensemble Learning with Pruning
        print(f"\nStep 2: Applying Ensemble Learning with Pruning...")
        ensemble_scores = self.apply_ensemble_learning(all_router_metrics)
        print(f"Ensemble scores calculated for {len(ensemble_scores)} routers")
        
        # Step 3: AI Recommendation
        print(f"\nStep 3: AI Recommendation...")
        recommended_router = self.get_ai_recommendation(ensemble_scores, all_router_metrics)
        
        if recommended_router:
            print(f"AI RECOMMENDATION: {recommended_router['router_name']}")
            print(f"  - Cache Occupancy: {recommended_router['cache_occupancy']:.1f}%")
            print(f"  - cmBA Score: {recommended_router['cmba_score']:.3f}")
            print(f"  - Latency: {recommended_router['latency']:.3f}s")
            print(f"  - Cache Hit Ratio: {recommended_router['cache_hit_ratio']:.1f}%")
            print(f"  - Ensemble Score: {recommended_router.get('ensemble_score', 0):.3f}")
        else:
            print("No router recommended")
        
        # Step 4: Assign task migration leader
        if recommended_router:
            self.task_migration_leader = recommended_router['router_name']
            print(f"\nStep 4: Task Migration Leader assigned: {self.task_migration_leader}")
            print("This router will take the lead for computation and task migration.")
        
        # Save AI recommendation data
        ai_data = {
            'timestamp': datetime.datetime.now(),
            'content_request': content_request,
            'all_router_metrics': all_router_metrics,
            'ensemble_scores': ensemble_scores,
            'recommended_router': recommended_router['router_name'] if recommended_router else None,
            'task_migration_leader': self.task_migration_leader
        }
        
        self.ai_recommendation_history.append(ai_data)
        self.save_ai_recommendation_table(ai_data)
        
        return recommended_router
    
    def trace_content_path_manual(self, routers, content_request):
        """
        Manual path tracing - simple sequential path
        """
        path = []
        current_router = routers[0]  # Start from first router
        
        while current_router and len(path) < len(routers):
            path.append(current_router.name)
            
            # Simple path: move to next router
            current_index = routers.index(current_router)
            if current_index < len(routers) - 1:
                current_router = routers[current_index + 1]
            else:
                break
                
        return path
    
    def calculate_manual_cmba(self, router, network_metrics):
        """
        Manual cmBA calculation - simple centrality-based
        """
        # Simple cmBA based on router position and cache performance
        position_factor = (routers.index(router) + 1) / len(routers)
        cache_factor = len(router.cs) / router.CACHE_LIMIT
        cmba = (position_factor + cache_factor) / 2
        return cmba
    
    def calculate_manual_latency(self, router):
        """
        Manual latency calculation - based on router position
        """
        # Simple latency based on router position
        base_latency = 0.01
        position_penalty = routers.index(router) * 0.005
        return base_latency + position_penalty
    
    def calculate_manual_chr(self, router):
        """
        Manual CHR calculation - based on cache hits
        """
        total_requests = router.cache_hits + router.publisher_hits
        if total_requests > 0:
            return (router.cache_hits / total_requests) * 100
        return 0
    
    def calculate_ai_cache_occupancy(self, router):
        """
        AI-based cache occupancy calculation
        """
        # More sophisticated calculation considering cache efficiency
        base_occupancy = (len(router.cs) / router.CACHE_LIMIT) * 100
        efficiency_factor = 1.0 + (router.cache_hits / max(router.cache_hits + router.publisher_hits, 1)) * 0.2
        return base_occupancy * efficiency_factor
    
    def calculate_ai_cmba(self, router, network_metrics):
        """
        AI-based cmBA calculation using network centrality
        """
        # More sophisticated cmBA using network metrics
        degree_centrality = network_metrics.get('degree_centrality', {}).get(router.name, 0.5)
        betweenness_centrality = network_metrics.get('betweenness_centrality', {}).get(router.name, 0.5)
        closeness_centrality = network_metrics.get('closeness_centrality', {}).get(router.name, 0.5)
        
        # Weighted combination with cache performance
        cache_performance = len(router.cs) / router.CACHE_LIMIT
        cmba = (0.3 * degree_centrality + 
                0.4 * betweenness_centrality + 
                0.3 * closeness_centrality) * (1 + cache_performance)
        
        return cmba
    
    def calculate_ai_latency(self, router, network_metrics):
        """
        AI-based latency calculation considering network topology
        """
        # More sophisticated latency calculation
        base_latency = 0.01
        centrality_factor = network_metrics.get('degree_centrality', {}).get(router.name, 0.5)
        load_factor = len(router.cs) / router.CACHE_LIMIT
        
        # Central routers have lower latency, loaded routers have higher latency
        latency = base_latency * (2 - centrality_factor) * (1 + load_factor * 0.5)
        return latency
    
    def calculate_ai_chr(self, router):
        """
        AI-based CHR calculation with predictive elements
        """
        # More sophisticated CHR calculation
        total_requests = router.cache_hits + router.publisher_hits
        if total_requests > 0:
            base_chr = (router.cache_hits / total_requests) * 100
            # Add predictive factor based on cache size
            predictive_factor = min(1.2, 1.0 + (len(router.cs) / router.CACHE_LIMIT) * 0.2)
            return base_chr * predictive_factor
        return 0
    
    def apply_ensemble_learning(self, router_metrics):
        """
        Apply ensemble learning with pruning
        """
        ensemble_scores = []
        
        for metrics in router_metrics:
            # Multiple learning algorithms (simplified)
            # Algorithm 1: Weighted scoring
            score1 = (0.25 * metrics['cache_occupancy'] + 
                     0.35 * metrics['cmba_score'] * 100 + 
                     0.25 * (100 - metrics['latency'] * 1000) + 
                     0.15 * metrics['cache_hit_ratio'])
            
            # Algorithm 2: Performance-based scoring
            score2 = (metrics['cache_hit_ratio'] * 0.4 + 
                     (100 - metrics['latency'] * 1000) * 0.3 + 
                     metrics['cmba_score'] * 100 * 0.3)
            
            # Algorithm 3: Efficiency-based scoring
            efficiency = metrics['cache_hit_ratio'] / max(metrics['latency'] * 1000, 0.1)
            score3 = efficiency * metrics['cmba_score'] * 100
            
            # Ensemble voting (weighted average)
            ensemble_score = (0.4 * score1 + 0.35 * score2 + 0.25 * score3)
            
            metrics['ensemble_score'] = ensemble_score
            ensemble_scores.append(metrics)
        
        # Pruning: Remove routers with very low scores
        threshold = max(score['ensemble_score'] for score in ensemble_scores) * 0.3
        pruned_scores = [score for score in ensemble_scores if score['ensemble_score'] >= threshold]
        
        print(f"Ensemble learning applied. Pruned from {len(ensemble_scores)} to {len(pruned_scores)} routers.")
        
        return pruned_scores
    
    def get_ai_recommendation(self, ensemble_scores, router_metrics):
        """
        Get AI recommendation based on ensemble scores
        """
        if not ensemble_scores:
            return None
        
        # Select router with highest ensemble score
        best_router = max(ensemble_scores, key=lambda x: x['ensemble_score'])
        return best_router
    
    def select_router_manual(self, router_metrics):
        """
        Manual router selection using simple weighted scoring
        """
        if not router_metrics:
            return None
        
        best_router = None
        best_score = -1
        
        for metrics in router_metrics:
            # Manual scoring: prioritize cache hit ratio and low latency
            score = (metrics['cache_hit_ratio'] * 0.4 + 
                    (100 - metrics['latency'] * 1000) * 0.3 + 
                    metrics['cmba_score'] * 100 * 0.3)
            
            if score > best_score:
                best_score = score
                best_router = metrics
        
        return best_router
    
    def comparison_mode(self, routers, network_metrics, content_request):
        """
        Run both processes and compare results
        """
        print("\n" + "="*60)
        print("COMPARISON MODE - BOTH PROCESSES")
        print("="*60)
        
        # Run manual process
        print("\n--- RUNNING MANUAL PROCESS ---")
        manual_result = self.manual_process(routers, network_metrics, content_request)
        
        # Run AI process
        print("\n--- RUNNING AI RECOMMENDER PROCESS ---")
        ai_result = self.ai_recommender_process(routers, network_metrics, content_request)
        
        # Compare results
        print("\n" + "="*50)
        print("COMPARISON RESULTS")
        print("="*50)
        
        if manual_result and ai_result:
            print(f"Manual Selection: {manual_result['router_name']}")
            print(f"AI Recommendation: {ai_result['router_name']}")
            
            if manual_result['router_name'] == ai_result['router_name']:
                print("✓ MATCH: Both processes selected the same router")
            else:
                print("✗ DIFFERENT: Processes selected different routers")
                
                # Show detailed comparison
                print(f"\nDetailed Comparison:")
                print(f"Manual - CO: {manual_result['cache_occupancy']:.1f}%, "
                      f"cmBA: {manual_result['cmba_score']:.3f}, "
                      f"Latency: {manual_result['latency']:.3f}s, "
                      f"CHR: {manual_result['cache_hit_ratio']:.1f}%")
                
                print(f"AI - CO: {ai_result['cache_occupancy']:.1f}%, "
                      f"cmBA: {ai_result['cmba_score']:.3f}, "
                      f"Latency: {ai_result['latency']:.3f}s, "
                      f"CHR: {ai_result['cache_hit_ratio']:.1f}%")
        else:
            print("One or both processes failed to select a router")
        
        # Save comparison data
        self.save_comparison_table(manual_result, ai_result, content_request)
        
        return manual_result, ai_result
    
    def save_manual_selection_table(self, selection_data):
        """Save manual selection data to CSV"""
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
                f"{selection_data['avg_cmba']:.3f}"
            ])
        
        print(f"Manual selection table saved: {filename}")
    
    def save_ai_recommendation_table(self, recommendation_data):
        """Save AI recommendation data to CSV"""
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
                f"{recommendation_data['recommended_router'].get('ensemble_score', 0):.3f}" if recommendation_data['recommended_router'] else "N/A"
            ])
        
        print(f"AI recommendation table saved: {filename}")
    
    def save_comparison_table(self, manual_result, ai_result, content_request):
        """Save comparison data to CSV"""
        os.makedirs('Data_Tables/Comparison_Reports', exist_ok=True)
        filename = f"Data_Tables/Comparison_Reports/comparison_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Content_Request', 'Manual_Selection', 'AI_Recommendation', 'Match'])
            
            match = "Yes" if (manual_result and ai_result and 
                            manual_result['router_name'] == ai_result['router_name']) else "No"
            
            writer.writerow([
                datetime.datetime.now(),
                content_request,
                manual_result['router_name'] if manual_result else "None",
                ai_result['router_name'] if ai_result else "None",
                match
            ])
        
        print(f"Comparison table saved: {filename}")
    
    def get_task_migration_leader(self):
        """Get current task migration leader"""
        return self.task_migration_leader
    
    def run_interactive_demo(self):
        """
        Run interactive demonstration
        """
        print("ENHANCED ROUTER SELECTION SYSTEM")
        print("This system provides two distinct processes for router selection:")
        print("1. Manual Process - Traditional path tracing and manual selection")
        print("2. AI Recommender Process - Machine learning-based recommendations")
        
        # Create example routers (simplified)
        class SimpleRouter:
            def __init__(self, name):
                self.name = name
                self.cs = ['content1', 'content2']  # Mock cache
                self.CACHE_LIMIT = 20
                self.cache_hits = random.randint(5, 20)
                self.publisher_hits = random.randint(10, 30)
        
        routers = [SimpleRouter(f'Router{i}') for i in range(1, 5)]
        
        # Mock network metrics
        network_metrics = {
            'degree_centrality': {f'Router{i}': random.random() for i in range(1, 5)},
            'betweenness_centrality': {f'Router{i}': random.random() for i in range(1, 5)},
            'closeness_centrality': {f'Router{i}': random.random() for i in range(1, 5)}
        }
        
        content_requests = ['cat_image1.jpg', 'dog_image15.jpg', 'cat_image30.jpg']
        
        while True:
            choice = self.display_process_menu()
            
            if choice == 1:
                # Manual Process
                for content_request in content_requests:
                    print(f"\n--- Processing: {content_request} ---")
                    self.manual_process(routers, network_metrics, content_request)
                    
            elif choice == 2:
                # AI Recommender Process
                for content_request in content_requests:
                    print(f"\n--- Processing: {content_request} ---")
                    self.ai_recommender_process(routers, network_metrics, content_request)
                    
            elif choice == 3:
                # Comparison Mode
                for content_request in content_requests:
                    print(f"\n--- Processing: {content_request} ---")
                    self.comparison_mode(routers, network_metrics, content_request)
            
            # Ask if user wants to continue
            continue_choice = input("\nDo you want to run another process? (y/n): ").lower()
            if continue_choice != 'y':
                break
        
        print("\nSession completed. All data tables have been saved.")
        print(f"Final task migration leader: {self.get_task_migration_leader()}")

if __name__ == "__main__":
    system = EnhancedRouterSelectionSystem()
    system.run_interactive_demo()
