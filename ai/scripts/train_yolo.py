from ultralytics import YOLO
import os

DATA_PATH = os.path.join("dataset", "data.yaml")

MODEL_NAME = "yolo11n.pt"

IMG_SIZE = 640

EPOCHS = 100

BATCH = 8 

DEVICE = "mps"

def main():
    print("\n🚀 Starting optimized YOLO11 training")
    print(f"Dataset: {DATA_PATH}")
    print(f"Base Model: {MODEL_NAME}")
    print(f"Image Size: {IMG_SIZE}")
    print(f"Epochs: {EPOCHS}")
    print(f"Batch Size: {BATCH}")
    print(f"Device: {DEVICE}\n")

    model = YOLO(MODEL_NAME)

    results = model.train(
        data=DATA_PATH,
        imgsz=IMG_SIZE,
        epochs=EPOCHS,
        batch=BATCH,
        device=DEVICE,
        lr0=0.005,           
        close_mosaic=20,     
        augment=True,

        project="runs/detect",
        name="train",
        exist_ok=True,
        verbose=True,
    )

    print("\n✅ Training complete!")
    print(f"📁 Results saved to: {results.save_dir}")
    print(f"🏆 Best model: {os.path.join(results.save_dir, 'weights', 'best.pt')}")

if __name__ == "__main__":
    main()
