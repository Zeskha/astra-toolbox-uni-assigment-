import astra
import numpy as np
from functions import *
import json
import time
import cv2
import os

BASE_DIR = "D:\\Fotos de imagenes3"
rec_algorithm = 'CGLS3D_CUDA'
vol_size = [256, 512] 
degrees = [np.pi, 2*np.pi]
iterations = [10, 100, 1000, 2000]

def save_slice_video(volume, output_path, fps=30, duration=5):
    """
    Create a video from a 3D volume by showing slices.
    
    Args:
        volume (np.ndarray): 3D volume data
        output_path (str): Path to save the video
        fps (int): Frames per second
        duration (int): Video duration in seconds
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Calculate number of frames needed
    total_frames = fps * duration
    depth = volume.shape[0]
    
    # Calculate how many times we need to cycle through the volume
    cycles = total_frames // depth
    if cycles < 1:
        cycles = 1
        fps = depth // duration
    
    # Initialize video writer
    frame_size = (volume.shape[1], volume.shape[2])
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, frame_size, isColor=False)
    
    # Normalize volume to 0-255 range
    volume_norm = ((volume - volume.min()) * 255 / (volume.max() - volume.min())).astype(np.uint8)
    
    # Write frames
    for _ in range(cycles):
        for i in range(depth):
            frame = volume_norm[i]
            out.write(frame)
    
    out.release()

def save_comparison_video(phantom, reconstruction, output_path, fps=30, duration=5):
    """
    Create a video comparing phantom and reconstruction side by side.
    
    Args:
        phantom (np.ndarray): Original phantom volume
        reconstruction (np.ndarray): Reconstructed volume
        output_path (str): Path to save the video
        fps (int): Frames per second
        duration (int): Video duration in seconds
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Calculate number of frames needed
    total_frames = fps * duration
    depth = phantom.shape[0]
    
    # Calculate cycles
    cycles = total_frames // depth
    if cycles < 1:
        cycles = 1
        fps = depth // duration
    
    # Initialize video writer
    frame_height = phantom.shape[1]
    frame_width = phantom.shape[2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height * 2), isColor=False)
    
    # Normalize volumes
    phantom_norm = ((phantom - phantom.min()) * 255 / (phantom.max() - phantom.min())).astype(np.uint8)
    recon_norm = ((reconstruction - reconstruction.min()) * 255 / (reconstruction.max() - reconstruction.min())).astype(np.uint8)
    
    # Write frames
    for _ in range(cycles):
        for i in range(depth):
            # Stack phantom and reconstruction vertically
            combined_frame = np.vstack((phantom_norm[i], recon_norm[i]))
            out.write(combined_frame)
    
    out.release()

def save_sinogram_image(sinogram, output_path):
    """
    Save a representative slice of the sinogram as an image.
    
    Args:
        sinogram (np.ndarray): 3D sinogram data
        output_path (str): Path to save the image
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Take a middle slice of the sinogram
    middle_slice = sinogram[sinogram.shape[0]//2]
    
    # Normalize to 0-255 range
    sino_norm = ((middle_slice - middle_slice.min()) * 255 / (middle_slice.max() - middle_slice.min())).astype(np.uint8)
    
    # Save the image
    cv2.imwrite(output_path, sino_norm)

def create_storing_folders(storing_dir, algorithm_name):
    # Create base output directory and subdirectories with algorithm name
    os.makedirs(os.path.join(storing_dir, f'reconstructions_{algorithm_name}'), exist_ok=True)
    os.makedirs(os.path.join(storing_dir, f'phantoms_{algorithm_name}'), exist_ok=True)
    os.makedirs(os.path.join(storing_dir, f'comparisons_{algorithm_name}'), exist_ok=True)
    os.makedirs(os.path.join(storing_dir, f'sinograms_{algorithm_name}'), exist_ok=True)

def projection_process(vol_id, sino_id, algorithm='FP3D_CUDA'):
    # Forward projection
    cfg_fp = astra.astra_dict(algorithm) 
    cfg_fp['VolumeDataId'] = vol_id
    cfg_fp['ProjectionDataId'] = sino_id

    alg_id = astra.algorithm.create(cfg_fp)
    astra.algorithm.run(alg_id)
    astra.algorithm.delete(alg_id)

    return astra.data3d.get(sino_id)

def reconstruction_process(vol_geom, sino_id, rec_algorithm):
    rec_id = astra.data3d.create('-vol', vol_geom)
    
    cfg_ra = astra.astra_dict(rec_algorithm)  
    cfg_ra['ProjectionDataId'] = sino_id
    cfg_ra['ReconstructionDataId'] = rec_id

    alg_id = astra.algorithm.create(cfg_ra)
    astra.algorithm.run(alg_id, e)
    reconstruction = astra.data3d.get(rec_id)
    astra.data3d.delete(rec_id)

    return reconstruction

def save_videos(reconstruction, phantom_3d, sinogram, config_id):
    # Save reconstruction video with new base path including algorithm name
    recon_video_path = os.path.join(BASE_DIR, f'reconstructions_{rec_algorithm}', f'{config_id}_reconstruction.mp4')
    save_slice_video(reconstruction, recon_video_path)
    
    # Save phantom video with new base path including algorithm name
    phantom_video_path = os.path.join(BASE_DIR, f'phantoms_{rec_algorithm}', f'{config_id}_phantom.mp4')
    save_slice_video(phantom_3d, phantom_video_path)
    
    # Save comparison video with new base path including algorithm name
    comparison_video_path = os.path.join(BASE_DIR, f'comparisons_{rec_algorithm}', f'{config_id}_comparison.mp4')
    save_comparison_video(phantom_3d, reconstruction, comparison_video_path)
    
    # Save sinogram image with new base path including algorithm name
    sinogram_path = os.path.join(BASE_DIR, f'sinograms_{rec_algorithm}', f'{config_id}_sinogram.png')
    save_sinogram_image(sinogram, sinogram_path)

def print_end_status(config_id, execution_time):
    print(f"Completed: {config_id}")
    print(f"Time: {execution_time:.2f}s")
    print(f"Saved files in {BASE_DIR}")

def main():
    create_storing_folders(BASE_DIR, rec_algorithm)
    # Create a dictionary to store all results
    results = {}
    # Define volume size
    for a in vol_size:
        results[f'vol_size_{a}'] = {}
        for w in range(1, 3):
            b = a * w
            results[f'vol_size_{a}'][f'pixels_{b}'] = {
                'spacing_180': {},
                'spacing_360': {},
                'spacing_720': {}
            }  
            for c in range(1,3):
                for d in degrees:
                    # Create a key for the current degrees configuration
                    degree_key = 'pi' if d == np.pi else '2pi'
                    results[f'vol_size_{a}'][f'pixels_{b}'][f'spacing_{int(np.rad2deg(d)*c)}'][f'degrees_{degree_key}'] = {}
                    
                    for e in iterations:
                        start_time = time.time()
                        angles = np.linspace(0, d, int(np.rad2deg(d)*c), endpoint=False)
                        vol_geom = astra.create_vol_geom(a, a, a)
                        proj_geom = astra.create_proj_geom('parallel3d', 1, 1, b, b, angles)

                        phantom_id, phantom_3d = astra.data3d.shepp_logan(vol_geom, modified=True)
                        astra.data3d.delete(phantom_id)

                        vol_id = astra.data3d.create('-vol', vol_geom, data=phantom_3d)
                        sino_id = astra.data3d.create('-proj3d', proj_geom)
                        
                        sinogram = projection_process(vol_id, sino_id)
                        
                        # Reconstruction
                        reconstruction = reconstruction_process(vol_geom, sino_id, rec_algorithm)

                        end_time = time.time()
                        execution_time = end_time - start_time

                        # Clean up ASTRA objects
                        astra.data3d.delete(vol_id)
                        astra.data3d.delete(sino_id)

                        # Generate unique identifier for this configuration
                        config_id = f'vol{a}_pix{b}_sp{int(np.rad2deg(d)*c)}_deg{degree_key}_iter{e}'
                        
                        save_videos(config_id, reconstruction, phantom_3d, sinogram, )
                        
                        # Calculate metrics
                        eucl_dist = float(euclidean_distance(phantom_3d, reconstruction))
                        avg_abs_dist = float(average_absolute_distance(phantom_3d, reconstruction))
                        max_dist = float(maximum_distance_3d(phantom_3d, reconstruction))
                        
                        
                        # Store results
                        results[f'vol_size_{a}'][f'pixels_{b}'][f'spacing_{int(np.rad2deg(d)*c)}'][f'degrees_{degree_key}'][f'iterations_{e}'] = {
                            'euclidean_distance': eucl_dist,
                            'average_absolute_distance': avg_abs_dist,
                            'maximum_distance': max_dist,
                            'execution_time_seconds': execution_time,
                            'info': config_id
                        }
                        # Save results after each iteration to the new base path with algorithm name
                        json_path = os.path.join(BASE_DIR, f'reconstruction_results_{rec_algorithm}.json')
                        with open(json_path, 'w') as f:
                            json.dump(results, f, indent=4)
                            
                        print_end_status(config_id, execution_time)
                        

if __name__ == '__main__':
    main()
    




