import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from torch.utils.data import DataLoader
from tqdm import tqdm
from model.model import TrainingSession, TrainingEpoch
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=10, batch_size=32, db=None, name_model="resnet50"):
    logger.info(f"Starting training model {name_model} with {num_epochs} epochs and batch size {batch_size}")
    training_session = TrainingSession(
        model_name=name_model,  
        epochs=num_epochs,
        batch_size=batch_size,
        best_val_accuracy=0.0
    )
    db.add(training_session)
    db.commit()
    logger.info(f"Training session saved with ID: {training_session.id}")

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for inputs, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}"):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels)
            total_train += labels.size(0)

        epoch_loss = running_loss / len(train_loader.dataset)
        epoch_accuracy = correct_train.double() / total_train

        model.eval()
        correct_val = 0
        total_val = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                correct_val += torch.sum(preds == labels)
                total_val += labels.size(0)

        val_accuracy = correct_val.double() / total_val

        training_epoch = TrainingEpoch(
            epoch_num=epoch + 1,
            train_loss=epoch_loss,
            train_accuracy=epoch_accuracy.item(),
            val_accuracy=val_accuracy.item(),
            training_session_id=training_session.id
        )
        db.add(training_epoch)
        db.commit()
        logger.info(f"Epoch {epoch+1} saved: Loss={epoch_loss:.4f}, TrainAcc={epoch_accuracy:.4f}, ValAcc={val_accuracy:.4f}")

        if val_accuracy > training_session.best_val_accuracy:
            training_session.best_val_accuracy = val_accuracy.item()
            db.commit()
            torch.save(model.state_dict(), f'best_model_{name_model}.pth')
            logger.info(f"Model saved with validation accuracy {val_accuracy:.4f}")

        print(f"Loss: {epoch_loss:.4f} | Train Accuracy: {epoch_accuracy:.4f} | Val Accuracy: {val_accuracy:.4f}")

    logger.info("Training completed")
    print("Training completed")

def start_training(train_loader, val_loader, batch_size: int, epochs: int, db, name_model: str):
    model_map = {
        "resnet50": models.resnet50,
        "resnet18": models.resnet18,
        "vgg16": models.vgg16
    }
    
    if name_model not in model_map:
        logger.error(f"Unsupported model: {name_model}")
        raise ValueError(f"Unsupported model: {name_model}. Supported models: {list(model_map.keys())}")

    model_fn = model_map[name_model]
    model = model_fn(weights="IMAGENET1K_V2")  
    num_classes = len(train_loader.dataset.classes)
    
    if "resnet" in name_model:
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif name_model == "vgg16":
        model.classifier[6] = nn.Linear(model.classifier[6].in_features, num_classes)
    
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=epochs, batch_size=batch_size, db=db, name_model=name_model)