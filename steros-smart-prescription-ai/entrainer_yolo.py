from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO("yolo26n.pt")

    resultats = model.train(
        data="data_v4.yaml",
        epochs=100,
        imgsz=640,
        batch=8,
        patience=20,
        device=0,
        project="runs_entrainement",
        name="zones_ordonnances_v4",
    )

# epoch:msh yara data 100 mara , 640 yaml resize lel les img kol ,batch : yarahm lots de 8 ala fois , patience kn f 20 epoch lasrtsh amelioration ikos