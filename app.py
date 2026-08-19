import os
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageSequenceClip
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Generador de Videos - ISSSTE C.M.F. Ermita",
    page_icon="🎬",
    layout="centered",
)

st.title("🎬 Generador Diario de Videos para Difusión")
st.write(
    "Sube tu imagen principal en gran tamaño, tus dos imágenes laterales y genera tu video institucional limpio."
)

# 1. Cargar imágenes laterales institucionales (izquierda y derecha)
st.subheader("📌 1. Imágenes Laterales (Izquierda y Derecha)")
col_l, col_r = st.columns(2)

with col_l:
  img_lat_izq_file = st.file_uploader(
      "Imagen lateral IZQUIERDA:",
      type=["png", "jpg", "jpeg"],
      key="lat_izq",
  )

with col_r:
  img_lat_der_file = st.file_uploader(
      "Imagen lateral DERECHA:",
      type=["png", "jpg", "jpeg"],
      key="lat_der",
  )

# 2. Sección para cargar las imágenes principales del día
st.subheader("🖼️ 2. Imágenes Principales del Día")
uploaded_images = st.file_uploader(
    "Sube las fotos centrales del día (puedes seleccionar varias):",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key="principal",
)

# Configuración de duración por imagen
duracion_imagen = st.slider(
    "¿Cuántos segundos debe durar cada imagen en el video?",
    min_value=1,
    max_value=10,
    value=3,
)

if uploaded_images:
  # 3. Botón para crear el video
  if st.button("🚀 Crear Video Institucional"):
    with st.spinner("Generando plantilla limpia con imagen central ampliada..."):
      temp_dir = "temp_imagenes"
      os.makedirs(temp_dir, exist_ok=True)

      image_paths = []
      canvas_width, canvas_height = 1280, 720
      canvas_size = (canvas_width, canvas_height)

      # Preparar imagen lateral izquierda
      lat_izq_img = None
      if img_lat_izq_file:
        lat_izq_img = Image.open(img_lat_izq_file).convert("RGBA")

      # Preparar imagen lateral derecha
      lat_der_img = None
      if img_lat_der_file:
        lat_der_img = Image.open(img_lat_der_file).convert("RGBA")

      # Procesar cada imagen principal
      for idx, img_file in enumerate(uploaded_images):
        img = Image.open(img_file)
        if img.mode in ("RGBA", "P"):
          img = img.convert("RGB")

        # 1. Lienzo base en Blanco
        template = Image.new("RGB", canvas_size, "white")
        draw = ImageDraw.Draw(template)

        # 2. Dibujar las líneas guinda y dorada al centro (por detrás)
        draw.rectangle(
            [
                (0, canvas_height // 2 - 50),
                (canvas_width, canvas_height // 2 + 50),
            ],
            fill="#6B1426",
        )
        draw.rectangle(
            [
                (0, canvas_height // 2 - 18),
                (canvas_width, canvas_height // 2 + 18),
            ],
            fill="#D4AF37",
        )

        # 3. Procesar y pegar la Imagen Central Principal (Ampliación máxima sin deformar)
        max_img_width = 980
        max_img_height = 580
        img.thumbnail((max_img_width, max_img_height), Image.Resampling.LANCZOS)

        paste_x = (canvas_width - img.width) // 2
        paste_y = (canvas_height - img.height) // 2
        template.paste(img, (paste_x, paste_y))

        # 4. Insertar imagen lateral IZQUIERDA (Proporcional)
        if lat_izq_img:
          target_w = img.width // 4.5
          target_h = int(
              lat_izq_img.height
              * (target_w / lat_izq_img.width)
          )
          lat_izq_resized = lat_izq_img.resize(
              (int(target_w), int(target_h)), Image.Resampling.LANCZOS
          )
          pos_izq_x = 35
          pos_izq_y = (canvas_height - lat_izq_resized.height) // 2
          template.paste(
              lat_izq_resized,
              (pos_izq_x, pos_izq_y),
              lat_izq_resized,
          )

        # 5. Insertar imagen lateral DERECHA
        if lat_der_img:
          target_w = img.width // 4.5
          target_h = int(
              lat_der_img.height
              * (target_w / lat_der_img.width)
          )
          lat_der_resized = lat_der_img.resize(
              (int(target_w), int(target_h)), Image.Resampling.LANCZOS
          )
          pos_der_x = canvas_width - lat_der_resized.width - 35
          pos_der_y = (canvas_height - lat_der_resized.height) // 2
          template.paste(
              lat_der_resized,
              (pos_der_x, pos_der_y),
              lat_der_resized,
          )

        # Guardar imagen procesada temporalmente
        path = os.path.join(temp_dir, f"img_{idx:03d}.jpg")
        template.save(path, "JPEG", quality=95)
        image_paths.append(path)

      # Ruta del video resultante
      output_video_path = "video_difusion.mp4"

      try:
        clip = ImageSequenceClip(image_paths, fps=1 / duracion_imagen)
        clip.write_videofile(
            output_video_path, fps=24, codec="libx264", audio=False
        )

        st.success(
            "¡Video institucional generado con éxito (limpio de textos y con imagen central ampliada)!"
        )

        # Reproductor y Botón de Descarga
        st.subheader("▶️ Vista previa del video:")
        video_file = open(output_video_path, "rb")
        video_bytes = video_file.read()
        st.video(video_bytes)

        st.download_button(
            label="📥 Descargar Video de Difusión",
            data=video_bytes,
            file_name="difusion_institucional.mp4",
            mime="video/mp4",
        )

      except Exception as e:
        st.error(f"Ocurrió un error al generar el video: {e}")

      finally:
        for path in image_paths:
          if os.path.exists(path):
            os.remove(path)
        if os.path.exists(temp_dir):
          os.rmdir(temp_dir)