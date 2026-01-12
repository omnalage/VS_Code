import os
import sys
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import csv
import pickle
import random

# Import the existing simulation components
from main import Router, Publisher, Subscriber, InterestPacket, DataPacket, ContentIDManager
from router_selection_system import RouterSelectionSystem

class IntegratedSimulationSystem:
    """
    Integrated simulation system that combines the existing NDN simulation
    with the new router selection and AI recommendation system.
    """
    
    def __init__(self):
        self.router_selection_system = RouterSelectionSystem()
        self.simulation_data = []
        self.network_metrics = {}
        self.performance_tables = {}
        
    def setup_network_with_selection(self, num_routers, num_subscribers):
        """
        Setup network with integrated router selection system
        """
        print("Setting up integrated network with router selection system...")
        
        # Create routers with enhanced capabilities
        routers = []
        for i in range(1, num_routers + 1):
            router = Router(f'Router{i}')
            routers.append(router)
        
        # Create publishers
        publisher1 = Publisher('Publisher1', 'cats')
        publisher2 = Publisher('Publisher2', 'dogs')
        publishers = [publisher1, publisher2]
        
        # Create subscribers
        subscribers = []
        for i in range(1, num_subscribers + 1):
            subscriber = Subscriber(f'Subscriber{i}')
            subscriber.connected_router = routers[(i-1) % len(routers)]
            subscribers.append(subscriber)
        
        # Initialize content ID manager
        ContentIDManager.initialize_index(publishers)
        
        # Setup FIB with enhanced routing
        self.setup_enhanced_fib(routers, publishers)
        
        # Calculate initial network metrics
        self.calculate_network_metrics(routers)
        
        return routers, publishers, subscribers
    
    def setup_enhanced_fib(self, routers, publishers):
        """
        Setup enhanced FIB with multiple paths and load balancing
        """
        for i, router in enumerate(routers):
            # Connect to next router in sequence
            if i < len(routers) - 1:
                router.fib.update({f"cat_image{j}.jpg": routers[i + 1] for j in range(1, 51)})
                router.fib.update({f"dog_image{j}.jpg": routers[i + 1] for j in range(1, 51)})
            
            # Add additional paths for load balancing
            for j in range(i + 2, min(i + 4, len(routers))):
                router.fib.update({f"cat_image{k}.jpg": routers[j] for k in range(1, 51)})
                router.fib.update({f"dog_image{k}.jpg": routers[j] for k in range(1, 51)})
        
        # Last router connects to publishers
        routers[-1].fib.update({f"cat_image{j}.jpg": publishers[0] for j in range(1, 51)})
        routers[-1].fib.update({f"dog_image{j}.jpg": publishers[1] for j in range(1, 51)})
    
    def calculate_network_metrics(self, routers):
        """
        Calculate network topology metrics for router selection
        """
        # Create network graph
        G = nx.Graph()
        
        # Add routers as nodes
        for router in routers:
            G.add_node(router.name)
        
        # Add edges based on FIB connections
        for router in routers:
            for content, next_hop in router.fib.items():
                if hasattr(next_hop, 'name') and next_hop.name in [r.name for r in routers]:
                    G.add_edge(router.name, next_hop.name)
        
        # Calculate centrality measures
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        closeness_centrality = nx.closeness_centrality(G)
        
        self.network_metrics = {
            'degree_centrality': degree_centrality,
            'betweenness_centrality': betweenness_centrality,
            'closeness_centrality': closeness_centrality,
            'graph': G
        }
        
        print("Network metrics calculated successfully")
    
    def run_integrated_simulation(self, routers, publishers, subscribers, iterations):
        """
        Run simulation with integrated router selection and AI recommendation
        """
        print(f"Starting integrated simulation with {iterations} iterations...")
        
        contents = [f"cat_image{i}.jpg" for i in range(1, 51)] + [f"dog_image{i}.jpg" for i in range(1, 51)]
        
        for iteration in range(iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Select active subscribers
            active_subscribers = [s for s in subscribers if random.random() < 0.9]
            
            if active_subscribers:
                # Select random subscriber and content
                subscriber = random.choice(active_subscribers)
                content_request = random.choice(contents)
                
                print(f"Subscriber {subscriber.name} requesting {content_request}")
                
                # Create interest packet
                interest_packet = InterestPacket(name=content_request)
                interest_packet.original_hop_count = len(routers)
                
                # MANUAL PROCESS: Router selection through tracing
                print("\n1. MANUAL PROCESS:")
                manual_selection = self.router_selection_system.manual_router_selection(
                    routers, self.network_metrics, content_request
                )
                
                # AI RECOMMENDER PROCESS: AI-based router selection
                print("\n2. AI RECOMMENDER PROCESS:")
                ai_recommendation = self.router_selection_system.ai_recommender_process(
                    routers, self.network_metrics, content_request
                )
                
                # Process the request through the network
                subscriber.send_interest(interest_packet, subscriber.connected_router)
                
                # Update network metrics after request processing
                self.calculate_network_metrics(routers)
                
                # Save performance data
                self.save_performance_data(routers, iteration, manual_selection, ai_recommendation)
                
                # Update task migration leader if AI recommendation is different
                if ai_recommendation and ai_recommendation['router_name'] != self.router_selection_system.get_task_migration_leader():
                    print(f"Task migration leader updated to: {ai_recommendation['router_name']}")
        
        # Generate final reports
        self.generate_final_reports()
        
        return self.simulation_data
    
    def save_performance_data(self, routers, iteration, manual_selection, ai_recommendation):
        """
        Save performance data for each iteration
        """
        # Calculate overall network performance
        total_requests = sum(router.cache_hits + router.publisher_hits for router in routers)
        total_cache_hits = sum(router.cache_hits for router in routers)
        avg_cache_hit_ratio = (total_cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate average latency
        avg_latency = sum(router.total_cache_access_time for router in routers) / len(routers)
        
        # Calculate hop reduction
        hop_reduction = 0  # This would be calculated based on actual vs expected hops
        
        iteration_data = {
            'iteration': iteration + 1,
            'timestamp': datetime.now(),
            'total_requests': total_requests,
            'cache_hits': total_cache_hits,
            'cache_hit_ratio': avg_cache_hit_ratio,
            'avg_latency': avg_latency,
            'hop_reduction': hop_reduction,
            'manual_selection': manual_selection['router_name'] if manual_selection else None,
            'ai_recommendation': ai_recommendation['router_name'] if ai_recommendation else None,
            'task_migration_leader': self.router_selection_system.get_task_migration_leader()
        }
        
        self.simulation_data.append(iteration_data)
        
        # Save individual router performance
        self.save_router_performance_table(routers, iteration)
    
    def save_router_performance_table(self, routers, iteration):
        """
        Save detailed router performance table
        """
        os.makedirs('Data_Tables/Router_Performance', exist_ok=True)
        
        filename = f"Data_Tables/Router_Performance/router_performance_iter_{iteration + 1}.csv"
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Router', 'Cache_Occupancy', 'cmBA_Score', 'Latency', 'Cache_Hit_Ratio', 'Total_Requests', 'Cache_Hits'])
            
            for router in routers:
                # Calculate performance metrics
                cache_occupancy = (len(router.cs) / router.CACHE_LIMIT) * 100
                total_requests = router.cache_hits + router.publisher_hits
                cache_hit_ratio = (router.cache_hits / total_requests * 100) if total_requests > 0 else 0
                
                # Get cmBA score from network metrics
                cmba_score = self.network_metrics['degree_centrality'].get(router.name, 0)
                
                # Calculate latency
                latency = router.total_cache_access_time / max(total_requests, 1)
                
                writer.writerow([
                    router.name,
                    f"{cache_occupancy:.2f}%",
                    f"{cmba_score:.4f}",
                    f"{latency:.4f}s",
                    f"{cache_hit_ratio:.2f}%",
                    total_requests,
                    router.cache_hits
                ])
        
        print(f"Router performance table saved: {filename}")
    
    def generate_final_reports(self):
        """
        Generate comprehensive final reports
        """
        print("\n=== GENERATING FINAL REPORTS ===")
        
        # Save simulation summary
        self.save_simulation_summary()
        
        # Save comparison between manual and AI selections
        self.router_selection_system.generate_comparison_report()
        
        # Save performance summary
        self.save_performance_summary()
        
        # Generate visualization plots
        self.generate_visualization_plots()
        
        print("All reports generated successfully!")
    
    def save_simulation_summary(self):
        """
        Save comprehensive simulation summary
        """
        os.makedirs('Data_Tables/Simulation_Summary', exist_ok=True)
        
        filename = f"Data_Tables/Simulation_Summary/simulation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Iteration', 'Timestamp', 'Total_Requests', 'Cache_Hits', 'Cache_Hit_Ratio', 
                            'Avg_Latency', 'Hop_Reduction', 'Manual_Selection', 'AI_Recommendation', 'Task_Migration_Leader'])
            
            for data in self.simulation_data:
                writer.writerow([
                    data['iteration'],
                    data['timestamp'],
                    data['total_requests'],
                    data['cache_hits'],
                    f"{data['cache_hit_ratio']:.2f}%",
                    f"{data['avg_latency']:.4f}s",
                    f"{data['hop_reduction']:.4f}",
                    data['manual_selection'],
                    data['ai_recommendation'],
                    data['task_migration_leader']
                ])
        
        print(f"Simulation summary saved: {filename}")
    
    def save_performance_summary(self):
        """
        Save overall performance summary
        """
        if not self.simulation_data:
            return
            
        os.makedirs('Data_Tables/Performance_Summary', exist_ok=True)
        
        filename = f"Data_Tables/Performance_Summary/overall_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Calculate summary statistics
        total_iterations = len(self.simulation_data)
        avg_cache_hit_ratio = sum(data['cache_hit_ratio'] for data in self.simulation_data) / total_iterations
        avg_latency = sum(data['avg_latency'] for data in self.simulation_data) / total_iterations
        total_requests = sum(data['total_requests'] for data in self.simulation_data)
        total_cache_hits = sum(data['cache_hits'] for data in self.simulation_data)
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total_Iterations', total_iterations])
            writer.writerow(['Total_Requests', total_requests])
            writer.writerow(['Total_Cache_Hits', total_cache_hits])
            writer.writerow(['Average_Cache_Hit_Ratio', f"{avg_cache_hit_ratio:.2f}%"])
            writer.writerow(['Average_Latency', f"{avg_latency:.4f}s"])
            writer.writerow(['Final_Task_Migration_Leader', self.router_selection_system.get_task_migration_leader()])
        
        print(f"Performance summary saved: {filename}")
    
    def generate_visualization_plots(self):
        """
        Generate visualization plots for the simulation results
        """
        if not self.simulation_data:
            return
            
        os.makedirs('Data_Tables/Visualizations', exist_ok=True)
        
        # Extract data for plotting
        iterations = [data['iteration'] for data in self.simulation_data]
        cache_hit_ratios = [data['cache_hit_ratio'] for data in self.simulation_data]
        latencies = [data['avg_latency'] for data in self.simulation_data]
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Cache Hit Ratio over iterations
        ax1.plot(iterations, cache_hit_ratios, 'b-', marker='o', linewidth=2)
        ax1.set_title('Cache Hit Ratio Over Iterations', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('Cache Hit Ratio (%)')
        ax1.grid(True, alpha=0.3)
        
        # Latency over iterations
        ax2.plot(iterations, latencies, 'r-', marker='s', linewidth=2)
        ax2.set_title('Average Latency Over Iterations', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Iteration')
        ax2.set_ylabel('Latency (seconds)')
        ax2.grid(True, alpha=0.3)
        
        # Manual vs AI selection comparison
        manual_selections = [data['manual_selection'] for data in self.simulation_data]
        ai_recommendations = [data['ai_recommendation'] for data in self.simulation_data]
        
        # Count selections by router
        manual_counts = {}
        ai_counts = {}
        
        for selection in manual_selections:
            if selection:
                manual_counts[selection] = manual_counts.get(selection, 0) + 1
        
        for recommendation in ai_recommendations:
            if recommendation:
                ai_counts[recommendation] = ai_counts.get(recommendation, 0) + 1
        
        # Plot selection comparison
        routers = list(set(list(manual_counts.keys()) + list(ai_counts.keys())))
        manual_values = [manual_counts.get(router, 0) for router in routers]
        ai_values = [ai_counts.get(router, 0) for router in routers]
        
        x = np.arange(len(routers))
        width = 0.35
        
        ax3.bar(x - width/2, manual_values, width, label='Manual Selection', alpha=0.8)
        ax3.bar(x + width/2, ai_values, width, label='AI Recommendation', alpha=0.8)
        ax3.set_title('Router Selection Comparison', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Router')
        ax3.set_ylabel('Selection Count')
        ax3.set_xticks(x)
        ax3.set_xticklabels(routers, rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Task migration leader changes
        task_leaders = [data['task_migration_leader'] for data in self.simulation_data]
        leader_changes = []
        current_leader = None
        
        for leader in task_leaders:
            if leader != current_leader:
                leader_changes.append(1)
                current_leader = leader
            else:
                leader_changes.append(0)
        
        ax4.plot(iterations, leader_changes, 'g-', marker='^', linewidth=2)
        ax4.set_title('Task Migration Leader Changes', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Iteration')
        ax4.set_ylabel('Leader Change (1=Yes, 0=No)')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the plot
        plot_filename = f"Data_Tables/Visualizations/simulation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Visualization plots saved: {plot_filename}")

def main():
    """
    Main function to run the integrated simulation system
    """
    print("=== INTEGRATED SIMULATION SYSTEM ===")
    print("This system combines NDN simulation with router selection and AI recommendation")
    
    # Initialize the integrated system
    integrated_system = IntegratedSimulationSystem()
    
    # Get simulation parameters
    try:
        num_routers = int(input("Enter number of routers: "))
        num_subscribers = int(input("Enter number of subscribers: "))
        iterations = int(input("Enter number of simulation iterations: "))
    except ValueError:
        print("Invalid input. Using default values.")
        num_routers = 5
        num_subscribers = 3
        iterations = 10
    
    # Setup network
    routers, publishers, subscribers = integrated_system.setup_network_with_selection(
        num_routers, num_subscribers
    )
    
    print(f"\nNetwork setup complete:")
    print(f"- Routers: {len(routers)}")
    print(f"- Publishers: {len(publishers)}")
    print(f"- Subscribers: {len(subscribers)}")
    
    # Run integrated simulation
    simulation_results = integrated_system.run_integrated_simulation(
        routers, publishers, subscribers, iterations
    )
    
    print(f"\nSimulation completed successfully!")
    print(f"Total iterations: {len(simulation_results)}")
    print(f"Final task migration leader: {integrated_system.router_selection_system.get_task_migration_leader()}")
    
    # Display summary statistics
    if simulation_results:
        avg_cache_hit = sum(result['cache_hit_ratio'] for result in simulation_results) / len(simulation_results)
        avg_latency = sum(result['avg_latency'] for result in simulation_results) / len(simulation_results)
        
        print(f"\nSummary Statistics:")
        print(f"- Average Cache Hit Ratio: {avg_cache_hit:.2f}%")
        print(f"- Average Latency: {avg_latency:.4f}s")
        print(f"- Total Requests: {sum(result['total_requests'] for result in simulation_results)}")
        print(f"- Total Cache Hits: {sum(result['cache_hits'] for result in simulation_results)}")

if __name__ == "__main__":
    main()
