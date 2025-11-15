import torch

# Check if CUDA is available
if torch.cuda.is_available():
    print("CUDA is available. GPUs detected.")
    
    # Get the number of available GPUs
    num_gpus = torch.cuda.device_count()
    print(f"Number of GPUs: {num_gpus}")
    
    # Iterate through each GPU and print its name
    for i in range(num_gpus):
        gpu_name = torch.cuda.get_device_name(i)
        print(f"GPU {i}: {gpu_name}")
        
    # Get the current default GPU
    current_gpu_index = torch.cuda.current_device()
    current_gpu_name = torch.cuda.get_device_name(current_gpu_index)
    print(f"Current default GPU: {current_gpu_name} (Index: {current_gpu_index})")
else:
    print("CUDA is not available. No GPUs detected or configured for PyTorch.")