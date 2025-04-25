import numpy as np
def euclidean_distance(phantom, reconstruction):
    return np.sqrt((np.sum((phantom - reconstruction) ** 2))/(np.sum((phantom - np.average(phantom))**2)))

def average_absolute_distance(phantom, reconstruction):
    return (np.sum(np.absolute(phantom - reconstruction)))/np.sum(np.absolute(phantom))

def calculate_neighborhood_average(image: np.ndarray, k: int, l: int) -> float:
    """
    Calculate the average of a 2x2 neighborhood at position (k,l).
    
    Args:
        image (np.ndarray): Input image
        k (int): Row index
        l (int): Column index
    
    Returns:
        float: Average value of the 2x2 neighborhood
    """
    return (image[2*k,2*l] + image[2*k+1,2*l] + 
            image[2*k,2*l+1] + image[2*k+1,2*l+1]) / 4

def maximum_distance_2d(image1: np.ndarray, image2: np.ndarray) -> float:
    """
    Calculate the maximum distance between two 2D images using 2x2 neighborhood averaging.
    
    Args:
        image1 (np.ndarray): First 2D image
        image2 (np.ndarray): Second 2D image
    
    Returns:
        float: Maximum distance between the neighborhood averages
    """
    if image1.shape != image2.shape:
        raise ValueError("Images must have the same dimensions")
    
    rows, cols = image1.shape
    max_distance = 0
    
    # Iterate over 2x2 neighborhoods
    for k in range(rows // 2):
        for l in range(cols // 2):
            # Calculate P_k,l (average of first image neighborhood)
            P_kl = calculate_neighborhood_average(image1, k, l)
            # Calculate R_k,l (average of second image neighborhood)
            R_kl = calculate_neighborhood_average(image2, k, l)
            # Update maximum distance
            distance = abs(P_kl - R_kl)
            max_distance = max(max_distance, distance)
    
    return max_distance
def maximum_distance_3d(image1: np.ndarray, image2: np.ndarray) -> float:
    """
    Calculate the maximum distance between two 3D images using 2x2 neighborhood averaging.
    
    Args:
        image1 (np.ndarray): First 3D image
        image2 (np.ndarray): Second 3D image
    
    Returns:
        float: Maximum distance between the neighborhood averages
    """
    if image1.shape != image2.shape:
        raise ValueError("Images must have the same dimensions")
    
    # For 3D images, we calculate the maximum distance for each channel
    # and return the maximum across all channels
    max_distance = 0
    for channel in range(image1.shape[2]):
        channel_distance = maximum_distance_2d(image1[:,:,channel], image2[:,:,channel])
        max_distance = max(max_distance, channel_distance)
    return max_distance