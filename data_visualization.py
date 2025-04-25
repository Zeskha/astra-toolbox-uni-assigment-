import matplotlib.pyplot as plt
import numpy as np
from data_analysis import get_all_values_and_iterations, get_ordered_values


path_to_json1 = "path1"
path_to_json2 = "path2"

def graph_iterations_value(value, path_to_json1, path_to_json2):
    sirt_file = path_to_json1
    cgls_file = path_to_json2

    values10_sirt, values100_sirt, values1000_sirt, values2000_sirt = get_all_values_and_iterations(sirt_file, value)
    values10_cgls, values100_cgls, values1000_cgls, values2000_cgls = get_all_values_and_iterations(cgls_file, value)

    # Calculate averages
    avg_sirt = [
        np.mean(values10_sirt),
        np.mean(values100_sirt),
        np.mean(values1000_sirt),
        np.mean(values2000_sirt)
    ]
    
    avg_cgls = [
        np.mean(values10_cgls),
        np.mean(values100_cgls),
        np.mean(values1000_cgls),
        np.mean(values2000_cgls)
    ]

    # Set up the bar graph
    iterations = ['10', '100', '1000', '2000']
    x = np.arange(len(iterations))
    width = 0.35  # Width of the bars

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, avg_sirt, width, label='SIRT')
    rects2 = ax.bar(x + width/2, avg_cgls, width, label='CGLS')

    # Add labels and title
    title_value = value.replace('_', ' ').title()
    ax.set_ylabel(title_value)
    ax.set_xlabel('Iterations')
    ax.set_title(f'{title_value} by Algorithm and Iterations')
    ax.set_xticks(x)
    ax.set_xticklabels(iterations)
    ax.legend()

    # Add value labels on top of each bar
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.3f}',
                        xy=(rect.get_x() + rect.get_width()/2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', rotation=90)

    autolabel(rects1)
    autolabel(rects2)

    plt.tight_layout()
    plt.show()

def plot_ordered_values(json_file, value_key, title=None):
    """
    Create a line plot of ordered values from a JSON file.
    
    Args:
        json_file (str): Path to the JSON file
        value_key (str): Key to extract values (e.g., 'euclidean_distance')
        title (str, optional): Title for the plot
    """
    # Get ordered values and their configurations
    values, infos = get_ordered_values(json_file, value_key)
    
    # Create positions for x-axis
    positions = np.arange(len(values))
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(positions, values, 'b-', label=value_key)
    plt.scatter(positions, values, color='red', s=30)
    
    # Customize the plot
    plt.xlabel('Position in ordered sequence')
    plt.ylabel(value_key.replace('_', ' ').title())
    if title:
        plt.title(title)
    else:
        plt.title(f'Ordered {value_key.replace("_", " ").title()} Values')
    
    # Add grid for better readability
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    plt.legend()
    
    # Show every nth label to avoid overcrowding
    n = max(len(positions) // 10, 1)  # Show about 10 labels
    plt.xticks(positions[::n])
    
    # Add tooltips for hovering (using annotations)
    annot = plt.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def hover(event):
        if event.inaxes:
            cont, ind = sc.contains(event)
            if cont:
                pos = ind["ind"][0]
                annot.xy = (positions[pos], values[pos])
                text = f"{value_key}: {values[pos]:.6f}\n{infos[pos]}"
                annot.set_text(text)
                annot.set_visible(True)
            else:
                annot.set_visible(False)
            plt.draw()

    # Create scatter plot for hover functionality
    sc = plt.scatter(positions, values, color='none')
    plt.gcf().canvas.mpl_connect("motion_notify_event", hover)
    
    plt.tight_layout()
    plt.show()

def plot_algorithms_comparison(value_key, path_to_json1, path_to_json2):
    """Create a comparative plot of SIRT and CGLS values"""
    # Get data for both algorithms
    sirt_values, sirt_infos = get_ordered_values(path_to_json1, value_key)
    cgls_values, cgls_infos = get_ordered_values(path_to_json2, value_key)

    # Create figure
    plt.figure(figsize=(12, 6))
    
    # Plot both algorithms
    plt.plot(range(len(sirt_values)), sirt_values, 'b-', label='SIRT', linewidth=2)
    plt.plot(range(len(cgls_values)), cgls_values, 'r-', label='CGLS', linewidth=2)
    
    # Add scatter points for better visibility
    plt.scatter(range(len(sirt_values)), sirt_values, color='blue', s=30, alpha=0.5)
    plt.scatter(range(len(cgls_values)), cgls_values, color='red', s=30, alpha=0.5)
    
    # Customize the plot
    plt.xlabel('Configuration Index')
    plt.ylabel(value_key.replace('_', ' ').title())
    plt.title(f'Comparison of {value_key.replace("_", " ").title()} between SIRT and CGLS')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Add tooltips
    annot = plt.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def hover(event):
        if event.inaxes:
            for line in plt.gca().lines:
                cont, ind = line.contains(event)
                if cont:
                    pos = ind["ind"][0]
                    annot.xy = (pos, line.get_ydata()[pos])
                    if line.get_label() == 'SIRT':
                        text = f"SIRT\n{value_key}: {sirt_values[pos]:.6f}\n{sirt_infos[pos]}"
                    else:
                        text = f"CGLS\n{value_key}: {cgls_values[pos]:.6f}\n{cgls_infos[pos]}"
                    annot.set_text(text)
                    annot.set_visible(True)
                    break
            else:
                annot.set_visible(False)
            plt.draw()

    plt.gcf().canvas.mpl_connect("motion_notify_event", hover)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    graph_iterations_value('execution_time_seconds') #Compare both json for each iteration number
    graph_iterations_value('euclidean_distance')
    graph_iterations_value('average_absolute_distance')
    graph_iterations_value('maximum_distance')

    # Example usage

    # Create plots for different metrics
    metrics = [
        'euclidean_distance',
        'average_absolute_distance',
        'maximum_distance',
        'execution_time_seconds'
    ]
    
    for metric in metrics:
        plot_algorithms_comparison(metric) #Compare both json

    plot_ordered_values(path_to_json1, 'euclidean_distance') # Plot only one json


