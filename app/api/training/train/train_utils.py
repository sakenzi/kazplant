from torch.utils.data import DataLoader
from torchvision import transforms
from model import ImageClassificationDataset
from app.api.training.train.training import start_training

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def train_model_script(batch_size: int, num_epochs: int):
    train_dir = "C:/projects/FASTAPI/kazplant/kazplant/new_plant/New Plant Diseases Dataset(Augmented)/train"
    val_dir = "C:/projects/FASTAPI/kazplant/kazplant/new_plant/New Plant Diseases Dataset(Augmented)/valid"

    train_dataset = ImageClassificationDataset(train_dir, transform=transform)
    val_dataset = ImageClassificationDataset(val_dir, transform=transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    start_training(train_loader, val_loader, batch_size=batch_size, epochs=num_epochs)
