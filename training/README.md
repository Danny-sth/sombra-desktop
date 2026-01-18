# Training "Sombra" Wake Word

## Инструкция для Google Colab

### 1. Открой Colab
https://colab.research.google.com/github/dscripka/openWakeWord/blob/main/notebooks/automatic_model_training.ipynb

### 2. Выбери GPU Runtime
`Runtime` → `Change runtime type` → `T4 GPU`

### 3. Запусти ячейки "Environment Setup" и "Download Data"
Это займёт ~10-15 минут

### 4. Замени конфиг в ячейке "Define Training Configuration"

Найди ячейку с кодом:
```python
config["target_phrase"] = ["hey sebastian"]
```

Замени на:
```python
config["target_phrase"] = ["sombra", "hey sombra", "ok sombra"]
config["model_name"] = "sombra"
config["custom_negative_phrases"] = ["samba", "sombre", "zombie", "summer", "some", "sob"]
config["n_samples"] = 10000
config["n_samples_val"] = 2000
config["steps"] = 50000
```

### 5. Запусти обучение
Выполни ячейки:
- Step 1: Generate synthetic clips (~15 мин)
- Step 2: Augment clips (~5 мин)
- Step 3: Train model (~25 мин)

### 6. Скачай модель
После обучения файлы будут в `sombra_model/`:
- `sombra.onnx` - для Python
- `sombra.tflite` - для мобильных устройств

### 7. Установи модель в Sombra Desktop

```bash
# Скопируй модель
cp sombra.onnx ~/.local/share/sombra/models/

# Или положи в проект
cp sombra.onnx /home/danny/Documents/projects/sombra-desktop/models/
```

Затем обнови `wakeword_service.py`:
```python
self._model = OwwModel(wakeword_models=["path/to/sombra.onnx"])
```

## Примерное время: 45-60 минут
