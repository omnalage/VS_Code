# Router Selection and AI Recommendation System

This system implements both manual and AI recommender processes for router selection and caching decisions in network environments, as specified in your requirements.

## Overview

The system provides two main processes:

### 1. Manual Process
- **Path Router Selection**: Through network tracing
- **cmBA Calculation**: Centrality-based Multi-metric Balanced Assessment
- **Router Selection**: For content caching based on performance metrics

### 2. AI Recommender Process
- **Performance Calculation**: CO (Cache Occupancy), cmBA, Latency, CHR (Cache Hit Ratio)
- **Ensemble Learning**: With pruning for optimal router selection
- **Protocol Router Recommendation**: For content caching
- **Task Migration**: Router takes lead for computation and task migration

## System Components

### Core Files

1. **`router_selection_system.py`** - Main router selection system
2. **`integrated_simulation_system.py`** - Integrated simulation with existing NDN system
3. **`demo_router_selection.py`** - Demonstration script
4. **`ROUTER_SELECTION_README.md`** - This documentation

### Key Features

- **Manual Router Selection**: Path tracing, cmBA calculation, router selection
- **AI Recommender**: Ensemble learning with pruning, performance-based recommendations
- **Data Table Management**: Automatic saving of all generated tables
- **Task Migration**: Dynamic assignment of computation leaders
- **Performance Metrics**: CO, cmBA, Latency, CHR calculations

## Usage

### Quick Start

1. **Run the demonstration**:
   ```bash
   python demo_router_selection.py
   ```

2. **Run the integrated simulation**:
   ```bash
   python integrated_simulation_system.py
   ```

### Manual Process Example

```python
from router_selection_system import RouterSelectionSystem

# Initialize the system
selection_system = RouterSelectionSystem()

# Manual router selection
manual_selection = selection_system.manual_router_selection(
    routers, network_metrics, content_request
)

print(f"Selected router: {manual_selection['router_name']}")
```

### AI Recommender Process Example

```python
# AI recommendation
ai_recommendation = selection_system.ai_recommender_process(
    routers, network_metrics, content_request
)

print(f"AI recommended router: {ai_recommendation['router_name']}")
print(f"Task migration leader: {selection_system.get_task_migration_leader()}")
```

## Data Tables Generated

The system automatically saves comprehensive data tables:

### 1. Manual Selection Tables
- **Location**: `Data_Tables/Manual_Selection/`
- **Content**: Timestamp, content request, traced path, selected router, average cmBA
- **Format**: CSV files with timestamps

### 2. AI Recommendation Tables
- **Location**: `Data_Tables/AI_Recommendation/`
- **Content**: Timestamp, content request, recommended router, task migration leader
- **Format**: CSV files with timestamps

### 3. Performance Summary Tables
- **Location**: `Data_Tables/Performance_Summary/`
- **Content**: Router performance metrics (CO, cmBA, Latency, CHR)
- **Format**: CSV files with detailed metrics

### 4. Router Performance Tables
- **Location**: `Data_Tables/Router_Performance/`
- **Content**: Per-iteration router performance data
- **Format**: CSV files for each iteration

### 5. Comparison Reports
- **Location**: `Data_Tables/Comparison_Reports/`
- **Content**: Manual vs AI selection comparisons
- **Format**: CSV files with match analysis

### 6. Visualization Plots
- **Location**: `Data_Tables/Visualizations/`
- **Content**: Performance plots and analysis charts
- **Format**: PNG files with comprehensive visualizations

## Example Data Processing

Based on your provided example:

| Router | Cache Occupancy | cmBA | Latency (s) | CHR |
|--------|----------------|------|-------------|-----|
| R1     | 5              | 2    | 1.2         | 9   |
| R2     | 10             | 4    | 2.0         | 10  |
| R3     | 15             | 9    | 3.0         | 2   |
| R4     | 20             | 7    | 5.0         | 8   |

The system will:

1. **Manual Process**:
   - Trace path through routers
   - Calculate cmBA for each router
   - Select best router based on weighted scoring

2. **AI Process**:
   - Calculate net performance metrics
   - Apply ensemble learning with pruning
   - Recommend optimal router
   - Assign task migration leader

## Performance Metrics

### Cache Occupancy (CO)
- Percentage of cache capacity used
- Formula: `(cached_items / cache_limit) * 100`

### cmBA (Centrality-based Multi-metric Balanced Assessment)
- Weighted combination of centrality measures
- Formula: `0.3 * degree + 0.4 * betweenness + 0.3 * closeness`

### Latency
- Network delay based on router position and load
- Formula: `base_latency * chr_factor * (2 - centrality_factor)`

### Cache Hit Ratio (CHR)
- Percentage of requests served from cache
- Formula: `(cache_hits / total_requests) * 100`

## Ensemble Learning

The AI recommender uses ensemble learning with:

1. **Random Forest Classifier**: For robust decision making
2. **Decision Tree Classifier**: For interpretable rules
3. **Logistic Regression**: For linear relationships
4. **Voting Mechanism**: Soft voting for final decisions
5. **Pruning**: To prevent overfitting

## Task Migration System

- **Dynamic Leader Assignment**: Based on AI recommendations
- **Computation Lead**: Router takes lead for future tasks
- **Migration Tracking**: Monitors leader changes over time
- **Performance Monitoring**: Tracks leader effectiveness

## Integration with Existing System

The system integrates seamlessly with the existing NDN simulation:

- **Router Class**: Enhanced with selection capabilities
- **Network Topology**: Automatic metric calculation
- **Content Requests**: Processed through both manual and AI methods
- **Data Persistence**: All tables saved automatically

## File Structure

```
Simulation_2_1_6_/
├── router_selection_system.py          # Core selection system
├── integrated_simulation_system.py     # Integrated simulation
├── demo_router_selection.py            # Demonstration script
├── ROUTER_SELECTION_README.md         # This documentation
├── Data_Tables/                        # Generated data tables
│   ├── Manual_Selection/               # Manual selection data
│   ├── AI_Recommendation/              # AI recommendation data
│   ├── Performance_Summary/            # Performance metrics
│   ├── Router_Performance/             # Per-iteration data
│   ├── Comparison_Reports/             # Manual vs AI comparison
│   └── Visualizations/                 # Performance plots
└── main.py                            # Original simulation system
```

## Running the System

### 1. Demonstration Mode
```bash
python demo_router_selection.py
```
This will:
- Show manual and AI processes
- Generate example data tables
- Demonstrate ensemble learning
- Create sample visualizations

### 2. Full Simulation Mode
```bash
python integrated_simulation_system.py
```
This will:
- Set up network topology
- Run integrated simulation
- Generate comprehensive reports
- Create performance visualizations

### 3. Custom Integration
```python
from router_selection_system import RouterSelectionSystem
from integrated_simulation_system import IntegratedSimulationSystem

# Initialize systems
selection_system = RouterSelectionSystem()
integrated_system = IntegratedSimulationSystem()

# Run custom simulation
results = integrated_system.run_integrated_simulation(
    routers, publishers, subscribers, iterations
)
```

## Output Examples

### Manual Selection Output
```
=== MANUAL ROUTER SELECTION PROCESS ===
Traced path for cat_image1.jpg: ['Router1', 'Router2', 'Router3']
Router Router1 - CO: 5.00%, cmBA: 0.3000, Latency: 0.0120s, CHR: 9.00%
Router Router2 - CO: 10.00%, cmBA: 0.5000, Latency: 0.0200s, CHR: 10.00%
Router Router3 - CO: 15.00%, cmBA: 0.8000, Latency: 0.0300s, CHR: 2.00%
Average cmBA for path: 0.5333
Manual selection: Router2
```

### AI Recommendation Output
```
=== AI RECOMMENDER PROCESS ===
AI Recommendation Result: Router3
  - Cache Occupancy: 15.0%
  - cmBA Score: 0.8
  - Latency: 0.0300s
  - Cache Hit Ratio: 2.0%
Current Task Migration Leader: Router3
```

## Benefits

1. **Automated Decision Making**: Both manual and AI processes
2. **Performance Optimization**: Based on multiple metrics
3. **Data Persistence**: All decisions and metrics saved
4. **Visualization**: Comprehensive performance analysis
5. **Scalability**: Handles multiple routers and requests
6. **Integration**: Works with existing NDN simulation

## Future Enhancements

- **Machine Learning Training**: Use historical data for model improvement
- **Real-time Adaptation**: Dynamic parameter adjustment
- **Advanced Metrics**: Additional performance indicators
- **Network Topology Optimization**: Automatic network structure improvement
- **Load Balancing**: Intelligent traffic distribution

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **File Permissions**: Check write permissions for Data_Tables directory
3. **Memory Issues**: Reduce iteration count for large networks
4. **Network Topology**: Verify router connections in FIB

### Dependencies

- pandas
- numpy
- networkx
- matplotlib
- scikit-learn
- csv
- datetime
- os
- sys

## Support

For issues or questions:
1. Check the generated log files in Data_Tables/
2. Verify network topology setup
3. Ensure all dependencies are installed
4. Review the demonstration output for examples

The system is designed to be robust and provide comprehensive logging for troubleshooting.
