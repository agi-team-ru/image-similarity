import logging
import os
from typing import Dict, List, Optional, Tuple, cast
import gradio as gr

from processors import find_similar
from core import make_public_uri
from constants import DATA_DIR, FAVICON_PATH, PUBLIC_ASSETS_DIR
from utils import read_dir_files, read_file
from PIL import Image

# Устанавливаем уровень логирования на основе переменной окружения LOG_LEVEL (по умолчанию "WARNING")
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING").upper())
logger = logging.getLogger(__name__)

# Заголовок приложения и подключение ресурсов интерфейса
app_title = "Image Filter by AGI Team"
css = read_file("./assets/style.css")
header_html = read_file("./assets/header.html").format(
    app_title=app_title,
    logo_url=make_public_uri(FAVICON_PATH),
)

# Порог схожести для фильтрации изображений
sim_thresholt = 0.7

# Задаем статические пути для файлов Gradio (например, ресурсы из PUBLIC_ASSETS_DIR)
gr.set_static_paths(paths=[PUBLIC_ASSETS_DIR])

# Определение интерфейса с использованием Gradio Blocks
with gr.Blocks(
    theme=gr.themes.Soft(), css=css, title=app_title, analytics_enabled=False
) as demo:
    gr.HTML(header_html)

    # Загружаем файлы изображений из директории базы данных
    db_files = [f"{DATA_DIR}/{file_name}" for file_name in read_dir_files(DATA_DIR)]

    db_size = len(db_files)

    gr.Markdown(value=f"В базе данных найдено изображений: **{db_size}**")

    image_input = gr.ImageEditor(
        # show_download_button=False,
        interactive=True,
        label="Изображение для проверки",
        # height=480,
        # canvas_size=(320,320),
        type="pil",
        # layers=False,
        # brush=False,
        # eraser=False,
    )

    submit_button = gr.Button("Запустить поиск по базе данных", variant="primary")
    gallery_output = gr.Gallery(
        interactive=False,
        label="Результаты поиска",
        allow_preview=False,
        object_fit="scale-down",
    )
    not_found_text = gr.Label("Совпадений не найдено", visible=False, show_label=False)

    # Обработчик нажатия кнопки для запуска поиска похожих изображений
    @submit_button.click(outputs=[gallery_output, not_found_text], inputs=[image_input])
    def on_submit(target_imgs: Dict[str, Image.Image]):
        if not target_imgs:
            raise Exception("Сначала необходимо загрузить изображение")

        # Выполняем поиск похожих изображений, используя функцию find_similar
        res = find_similar(
            target_imgs["composite"],
            lambda: cast(
                List[Image.Image], [Image.open(img_path) for img_path in db_files]
            ),
        )
        results: List[Tuple[str, str]] = []
        for i, sim_percent in res:
            if sim_percent > sim_thresholt:
                results.append((db_files[i], f"Совпадение на {sim_percent:.1%}"))

        # Отображаем результаты поиска или текст, если совпадений не найдено
        return [
            gr.Gallery(results),
            gr.Markdown(visible=len(results) == 0),
        ]


# Запуск веб-приложения с указанием порта и параметров сервера
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=8080,
        show_api=False,
        favicon_path=FAVICON_PATH,
    )
