import os
from PIL import Image, ImageOps
from moviepy import ImageSequenceClip
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Generador de Videos para Difusión", page_icon="🎬", layout="centered"
)

st.title("🎬 Generador Diario de Videos para Difusión")
st.write(
    "Sube tus imágenes del día, define la duración de cada una y haz clic en 'Crear Video'."
)

# 1. Sección para cargar imágenes
uploaded_images = st.file_uploader(
    "Sube tus imágenes (puedes seleccionar varias a la vez):",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
)

# Configuración de duración por imagen
duracion_imagen = st.slider(
    "¿Cuántos segundos debe durar cada imagen en el video?",
    min_value=1,
    max_value=10,
    value=3,
)

if uploaded_images:
  st.subheader("🖼️ Imágenes seleccionadas:")
  cols = st.columns(min(len(uploaded_images), 4))
  for idx, img_file in enumerate(uploaded_images):
    with cols[idx % 4]:
      img = Image.open(img_file)
      st.image(img, caption=f"Imagen {idx+1}", use_container_width=True)

  # 2. Botón para crear el video
  if st.button("🚀 Crear Video"):
    with st.spinner(
        "Aplicando plantilla, centrando imágenes y generando el video..."
    ):
      temp_dir = "temp_imagenes"
      os.makedirs(temp_dir, exist_ok=True)

      image_paths = []
      
      # Definir el tamaño del lienzo de la "plantilla" (Formato Horizontal HD)
      canvas_size = (1280, 720)
      
      # Color de fondo para los espacios vacíos (puedes elegir "black" o "white")
      bg_color = "black" 

      # Procesar y ajustar cada imagen a la plantilla proporcionalmente
      for idx, img_file in enumerate(uploaded_images):
        img = Image.open(img_file)
        
        # Convertir a RGB si es necesario
        if img.mode in ("RGBA", "P"):
          img = img.convert("RGB")

        # Ajustar la imagen proporcionalmente para que quepa dentro de 1280x720 sin deformarse
        img.thumbnail(canvas_size, Image.Resampling.LANCZOS)

        # Crear un lienzo nuevo del tamaño exacto de la plantilla con el color de fondo
        template = Image.new("RGB", canvas_size, bg_color)

        # Calcular la posición exacta para centrar la imagen en el lienzo
        paste_x = (canvas_size[0] - img.width) // 2
        paste_y = (canvas_size[1] - img.height) // 2

        # Pegar la imagen centrada sobre la plantilla
        template.paste(img, (paste_x, paste_y))

        # Guardar la imagen procesada temporalmente
        path = os.path.join(temp_dir, f"img_{idx:03d}.jpg")
        template.save(path, "JPEG", quality=95)
        image_paths.append(path)

      # Definir la ruta del video de salida
      output_video_path = "video_difusion.mp4"

      try:
        # Crear el clip de video usando MoviePy
        clip = ImageSequenceClip(image_paths, fps=1 / duracion_imagen)
        clip.write_videofile(
            output_video_path, fps=24, codec="libx264", audio=False
        )

        st.success("¡El video se ha generado con éxito y sin deformaciones!")

        # 3. Reproductor y Botón de Descarga
        st.subheader("▶️ Vista previa del video:")
        video_file = open(output_video_path, "rb")
        video_bytes = video_file.read()
        st.video(video_bytes)

        st.download_button(
            label="📥 Descargar Video para Difusión",
            data=video_bytes,
            file_name="difusion_del_dia.mp4",
            mime="video/mp4",
        )

      except Exception as e:
        st.error(f"Ocurrió un error al generar el video: {e}")

      finally:
        # Limpieza de archivos temporales
        for path in image_paths:
          if os.path.exists(path):
            os.remove(path)
        if os.path.exists(temp_dir):
          os.rmdir(temp_dir)