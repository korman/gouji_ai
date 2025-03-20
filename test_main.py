import torch

# 创建测试张量并移至GPU
x = torch.rand(5, 3)
if torch.cuda.is_available():
    device = torch.device("cuda")
    x = x.to(device)
    print(f"使用GPU: {torch.cuda.get_device_name(0)}")
    print(f"张量在GPU上: {x.is_cuda}")
else:
    print("CUDA不可用")
