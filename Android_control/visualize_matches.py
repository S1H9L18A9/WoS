import os
import cv2
import numpy as np
from pathlib import Path

def find_images_in_screenshot(seed_folder, screenshot_paths, threshold = 0.8, filter = False, 
                              min_distance = 20):
    """
    Find all occurrences of seed images in the given screenshots.
    
    Args:
        seed_folder (str): Path to folder containing seed images and subfolders
        screenshot_paths (list): List of paths to screenshot images to search in
        threshold (float): Minimum match probability (0.0 to 1.0)
        
    Returns:
        dict: Results organized by screenshot with matches for each seed image
    """
    # Get all image files recursively from the seed folder
    seed_images = []
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    for root, _, files in os.walk(seed_folder):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_extensions:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, seed_folder)
                seed_images.append((relative_path, file_path))
    
    print(f"Found {len(seed_images)} seed images")
    
    # Initialize results dictionary
    results = {}
    
    # Check each screenshot
    for screenshot_path in screenshot_paths:
        screenshot = cv2.imread(screenshot_path)
        if screenshot is None:
            print(f"Error: Could not load screenshot at {screenshot_path}")
            continue
            
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Initialize results for this screenshot
        screenshot_results = []
        
        # Search for each seed image
        for relative_path, seed_path in seed_images:
            seed_img = cv2.imread(seed_path)
            if seed_img is None:
                print(f"Error: Could not load seed image at {seed_path}")
                continue
                
            seed_gray = cv2.cvtColor(seed_img, cv2.COLOR_BGR2GRAY)
            
            # Use template matching to find the seed image in the screenshot
            result = cv2.matchTemplate(screenshot_gray, seed_gray, cv2.TM_CCOEFF_NORMED)
            
            # Find all locations where the match exceeds the threshold
            locations = np.where(result >= threshold)
            
            # Process all matches
            matches = []
            for y, x in zip(*locations):
                # Get the match probability
                prob = result[y, x]
                
                # Record this match
                match = {
                    'seed_path': relative_path,
                    'probability': float(prob),
                    'position': (int(x), int(y)),
                    'size': seed_img.shape[:2][::-1]  # (width, height)
                }
                matches.append(match)
            
            # If we found matches, add to results
            if matches:
                if filter:
                    matches = filter_list_of(matches, min_distance)
                screenshot_results.extend(matches)
        
        # Sort results by probability (highest first)
        screenshot_results.sort(key=lambda x: x['probability'], reverse=True)
        
        # Add to overall results
        results[screenshot_path] = screenshot_results
        print(f"Found {len(screenshot_results)} matches in {screenshot_path}")
    return results


def filter_list_of(matches, min_distance,):
        # Apply non-maximum suppression
    filtered_matches = []
    
    while matches:
        # Take the match with highest probability
        best_match = matches.pop(0)
        filtered_matches.append(best_match)
        
        # Filter out all matches that are too close to this one
        remaining_matches = []
        for match in matches:
            # Skip if it's the same seed image and too close to the best match
            if match['seed_path'] == best_match['seed_path']:
                x1, y1 = best_match['position']
                x2, y2 = match['position']
                distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                if distance < min_distance:
                    continue
            
            remaining_matches.append(match)
        
        matches = remaining_matches
    
    return filtered_matches


def visualize_matches(screenshot_path, matches, output_path=None):
    """
    Visualize matches on a copy of the screenshot.
    
    Args:
        screenshot_path (str): Path to the screenshot
        matches (list): List of match dictionaries
        output_path (str, optional): Path to save the visualization
        
    Returns:
        numpy.ndarray: Screenshot with matches highlighted
    """
    # Load the screenshot
    screenshot = cv2.imread(screenshot_path)
    if screenshot is None:
        print(f"Error: Could not load screenshot at {screenshot_path}")
        return None
        
    # Make a copy to draw on
    visual = screenshot.copy()
    
    # Draw all matches
    for match in matches:
        x, y = match['position']
        w, h = match['size']
        prob = match['probability']
        if 'seed_path' in match.keys():
            seed_path = match['seed_path']
        else:
            seed_path = ''
        
        # Draw rectangle
        cv2.rectangle(visual, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Add text with probability and seed path
        text = f"{seed_path}-{prob:.2f}"
        cv2.putText(visual, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Save if requested
    if output_path:
        cv2.imwrite(output_path, visual)
        print(f"Visualization saved to {output_path}")
    
    return visual

def main():
    # Configuration
    # seed_folder = r"C:\Users\sahilr\Downloads\Whiteout Survival\Whiteout Survival\image\ocr"
    seed_folder = "..\\test_images"
    screenshots = ["..\\screen_intel.png", "..\\screen_heal_click.png"]
    threshold = 0.9
    
    # Find matches
    results = find_images_in_screenshot(seed_folder, screenshots, threshold, filter= True)
    
    # Generate visualizations
    for screenshot_path, matches in results.items():
        if matches:
            output_path = f"{os.path.splitext(screenshot_path)[0]}_matched.png"
            visualize_matches(screenshot_path, matches, output_path)
            
            # Print detailed results
            print(f"\nMatches found in {screenshot_path}:")
            for i, match in enumerate(matches, 1):
                print(f"  {i}. {match['seed_path']} - Probability: {match['probability']:.4f}, Position: {match['position']}")
        else:
            print(f"\nNo matches found in {screenshot_path}")
    print(results)

if __name__ == "__main__":
    main()