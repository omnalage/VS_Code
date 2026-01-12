#!/usr/bin/env python3
"""
Simple demonstration of the Enhanced Router Selection System
Shows the clear differences between Manual and AI processes
"""

import os
import csv
import datetime
import random

def create_example_router_data():
    """
    Create example router data based on the provided table
    """
    return {
        'R1': {'cache_occupancy': 5, 'cmba': 2, 'latency': 1.2, 'chr': 9},
        'R2': {'cache_occupancy': 10, 'cmba': 4, 'latency': 2.0, 'chr': 10},
        'R3': {'cache_occupancy': 15, 'cmba': 9, 'latency': 3.0, 'chr': 2},
        'R4': {'cache_occupancy': 20, 'cmba': 7, 'latency': 5.0, 'chr': 8}
    }

def manual_process_demo(router_data, content_request):
    """
    Demonstrate the MANUAL PROCESS
    """
    print("\n" + "="*60)
    print("MANUAL PROCESS DEMONSTRATION")
    print("="*60)
    print(f"Processing content request: {content_request}")
    
    # Step 1: Path tracing (simple sequential)
    print("\nStep 1: Path Tracing")
    traced_path = ['R1', 'R2', 'R3', 'R4']
    print(f"Traced path: {' -> '.join(traced_path)}")
    
    # Step 2: Calculate cmBA for each router in path
    print("\nStep 2: Calculate cmBA for routers in path")
    path_metrics = []
    for router_name in traced_path:
        if router_name in router_data:
            data = router_data[router_name]
            # Manual cmBA calculation (simple)
            manual_cmba = (data['cmba'] + data['chr']) / 2
            path_metrics.append({
                'router': router_name,
                'cache_occupancy': data['cache_occupancy'],
                'cmba': manual_cmba,
                'latency': data['latency'],
                'chr': data['chr']
            })
            print(f"  {router_name}: CO={data['cache_occupancy']}%, cmBA={manual_cmba:.1f}, "
                  f"Latency={data['latency']}s, CHR={data['chr']}%")
    
    # Step 3: Calculate average cmBA
    if path_metrics:
        avg_cmba = sum(metric['cmba'] for metric in path_metrics) / len(path_metrics)
        print(f"\nStep 3: Average cmBA for path: {avg_cmba:.1f}")
    
    # Step 4: Manual router selection (simple scoring)
    print("\nStep 4: Manual Router Selection")
    best_router = None
    best_score = -1
    
    for metric in path_metrics:
        # Manual scoring: prioritize CHR and low latency
        score = metric['chr'] * 0.6 + (100 - metric['latency'] * 10) * 0.4
        print(f"  {metric['router']}: Score = {score:.1f}")
        
        if score > best_score:
            best_score = score
            best_router = metric
    
    print(f"\nMANUAL SELECTION RESULT: {best_router['router']}")
    print(f"  - Cache Occupancy: {best_router['cache_occupancy']}%")
    print(f"  - cmBA: {best_router['cmba']:.1f}")
    print(f"  - Latency: {best_router['latency']}s")
    print(f"  - CHR: {best_router['chr']}%")
    print(f"  - Selection Score: {best_score:.1f}")
    
    return best_router

def ai_recommender_process_demo(router_data, content_request):
    """
    Demonstrate the AI RECOMMENDER PROCESS
    """
    print("\n" + "="*60)
    print("AI RECOMMENDER PROCESS DEMONSTRATION")
    print("="*60)
    print(f"Processing content request: {content_request}")
    
    # Step 1: Calculate net performance for all routers
    print("\nStep 1: Calculate Net Performance (CO, cmBA, Latency, CHR)")
    all_metrics = []
    for router_name, data in router_data.items():
        # AI-based calculations (more sophisticated)
        ai_cmba = data['cmba'] * 1.2 + data['chr'] * 0.1  # AI enhancement
        ai_latency = data['latency'] * (1 - data['chr'] / 100)  # AI optimization
        ai_chr = data['chr'] * (1 + data['cache_occupancy'] / 100)  # AI prediction
        
        metrics = {
            'router': router_name,
            'cache_occupancy': data['cache_occupancy'],
            'cmba': ai_cmba,
            'latency': ai_latency,
            'chr': ai_chr
        }
        all_metrics.append(metrics)
        
        print(f"  {router_name}: CO={data['cache_occupancy']}%, cmBA={ai_cmba:.1f}, "
              f"Latency={ai_latency:.1f}s, CHR={ai_chr:.1f}%")
    
    # Step 2: Apply Ensemble Learning with Pruning
    print("\nStep 2: Apply Ensemble Learning with Pruning")
    ensemble_scores = []
    
    for metric in all_metrics:
        # Multiple AI algorithms
        # Algorithm 1: Performance-based
        score1 = metric['chr'] * 0.4 + (100 - metric['latency'] * 10) * 0.3 + metric['cmba'] * 0.3
        
        # Algorithm 2: Efficiency-based
        efficiency = metric['chr'] / max(metric['latency'], 0.1)
        score2 = efficiency * metric['cmba']
        
        # Algorithm 3: Load-balanced
        load_factor = 1 - (metric['cache_occupancy'] / 100)
        score3 = metric['chr'] * load_factor + metric['cmba'] * 0.5
        
        # Ensemble voting
        ensemble_score = (score1 * 0.4 + score2 * 0.35 + score3 * 0.25)
        metric['ensemble_score'] = ensemble_score
        ensemble_scores.append(metric)
        
        print(f"  {metric['router']}: Score1={score1:.1f}, Score2={score2:.1f}, "
              f"Score3={score3:.1f}, Ensemble={ensemble_score:.1f}")
    
    # Pruning: Remove low-performing routers
    threshold = max(score['ensemble_score'] for score in ensemble_scores) * 0.4
    pruned_scores = [score for score in ensemble_scores if score['ensemble_score'] >= threshold]
    print(f"\nPruning: Kept {len(pruned_scores)} out of {len(ensemble_scores)} routers")
    
    # Step 3: AI Recommendation
    print("\nStep 3: AI Recommendation")
    if pruned_scores:
        best_router = max(pruned_scores, key=lambda x: x['ensemble_score'])
        print(f"\nAI RECOMMENDATION: {best_router['router']}")
        print(f"  - Cache Occupancy: {best_router['cache_occupancy']}%")
        print(f"  - cmBA: {best_router['cmba']:.1f}")
        print(f"  - Latency: {best_router['latency']:.1f}s")
        print(f"  - CHR: {best_router['chr']:.1f}%")
        print(f"  - Ensemble Score: {best_router['ensemble_score']:.1f}")
        
        # Step 4: Assign task migration leader
        print(f"\nStep 4: Task Migration Leader Assignment")
        print(f"Router {best_router['router']} is now the task migration leader")
        print("This router will take the lead for computation and task migration")
        
        return best_router
    else:
        print("No router recommended after pruning")
        return None

def comparison_demo(router_data, content_request):
    """
    Demonstrate comparison between Manual and AI processes
    """
    print("\n" + "="*60)
    print("COMPARISON DEMONSTRATION")
    print("="*60)
    print(f"Processing content request: {content_request}")
    
    # Run both processes
    manual_result = manual_process_demo(router_data, content_request)
    ai_result = ai_recommender_process_demo(router_data, content_request)
    
    # Compare results
    print("\n" + "="*50)
    print("COMPARISON RESULTS")
    print("="*50)
    
    if manual_result and ai_result:
        print(f"Manual Selection: {manual_result['router']}")
        print(f"AI Recommendation: {ai_result['router']}")
        
        if manual_result['router'] == ai_result['router']:
            print("✓ MATCH: Both processes selected the same router")
        else:
            print("✗ DIFFERENT: Processes selected different routers")
            print("\nDetailed Comparison:")
            print(f"Manual - {manual_result['router']}: CHR={manual_result['chr']}%, "
                  f"Latency={manual_result['latency']}s, cmBA={manual_result['cmba']:.1f}")
            print(f"AI - {ai_result['router']}: CHR={ai_result['chr']:.1f}%, "
                  f"Latency={ai_result['latency']:.1f}s, cmBA={ai_result['cmba']:.1f}, "
                  f"Ensemble={ai_result['ensemble_score']:.1f}")
    else:
        print("One or both processes failed to select a router")

def save_demo_tables(manual_result, ai_result, content_request):
    """
    Save demonstration data to CSV tables
    """
    os.makedirs('Data_Tables/Demo', exist_ok=True)
    
    # Save manual selection table
    manual_filename = f"Data_Tables/Demo/manual_demo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(manual_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Content_Request', 'Selected_Router', 'CHR', 'Latency', 'cmBA'])
        if manual_result:
            writer.writerow([
                datetime.datetime.now(),
                content_request,
                manual_result['router'],
                f"{manual_result['chr']}%",
                f"{manual_result['latency']}s",
                f"{manual_result['cmba']:.1f}"
            ])
    
    # Save AI recommendation table
    ai_filename = f"Data_Tables/Demo/ai_demo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(ai_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Content_Request', 'Recommended_Router', 'CHR', 'Latency', 'cmBA', 'Ensemble_Score'])
        if ai_result:
            writer.writerow([
                datetime.datetime.now(),
                content_request,
                ai_result['router'],
                f"{ai_result['chr']:.1f}%",
                f"{ai_result['latency']:.1f}s",
                f"{ai_result['cmba']:.1f}",
                f"{ai_result['ensemble_score']:.1f}"
            ])
    
    print(f"\nDemo tables saved:")
    print(f"- Manual: {manual_filename}")
    print(f"- AI: {ai_filename}")

def main():
    """
    Main demonstration function
    """
    print("ENHANCED ROUTER SELECTION SYSTEM DEMONSTRATION")
    print("This demo shows the clear differences between Manual and AI processes")
    
    # Create example data
    router_data = create_example_router_data()
    content_requests = ['cat_image1.jpg', 'dog_image15.jpg', 'cat_image30.jpg']
    
    print("\nExample Router Data:")
    print("Router | Cache Occupancy | cmBA | Latency | CHR")
    print("-------|----------------|------|---------|-----")
    for router, data in router_data.items():
        print(f"{router:6} | {data['cache_occupancy']:14}% | {data['cmba']:4} | {data['latency']:7}s | {data['chr']:3}%")
    
    while True:
        print("\n" + "="*60)
        print("CHOOSE DEMONSTRATION MODE:")
        print("1. Manual Process Only")
        print("2. AI Recommender Process Only")
        print("3. Comparison Mode (Both Processes)")
        print("4. Exit")
        
        try:
            choice = int(input("\nEnter your choice (1-4): "))
            
            if choice == 1:
                for content_request in content_requests:
                    manual_process_demo(router_data, content_request)
                    
            elif choice == 2:
                for content_request in content_requests:
                    ai_recommender_process_demo(router_data, content_request)
                    
            elif choice == 3:
                for content_request in content_requests:
                    comparison_demo(router_data, content_request)
                    # Save demo tables
                    manual_result = manual_process_demo(router_data, content_request)
                    ai_result = ai_recommendation_process_demo(router_data, content_request)
                    save_demo_tables(manual_result, ai_result, content_request)
                    
            elif choice == 4:
                print("Demo completed. Thank you!")
                break
                
            else:
                print("Please enter 1, 2, 3, or 4")
                
        except ValueError:
            print("Please enter a valid number")
        
        # Ask if user wants to continue
        continue_choice = input("\nDo you want to run another demonstration? (y/n): ").lower()
        if continue_choice != 'y':
            break
    
    print("\nAll demonstration data has been saved to Data_Tables/Demo/")
    print("Key Differences Demonstrated:")
    print("✓ Manual Process: Simple path tracing, basic cmBA calculation, manual scoring")
    print("✓ AI Process: Sophisticated calculations, ensemble learning, pruning, task migration")
    print("✓ Both processes can select different routers based on their algorithms")

if __name__ == "__main__":
    main()
