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
    "Sube tus imágenes del día, define la duración y genera tu video con plantilla institucional."
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
    with st.spinner("Generando video con texto masivo y de extremo a extremo..."):
      temp_dir = "temp_imagenes"
      os.makedirs(temp_dir, exist_ok=True)

      image_paths = []
      canvas_width, canvas_height = 1280, 720
      canvas_size = (canvas_width, canvas_height)

      # Fuente verdaderamente gigante (160 px para impacto total)
      try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(font_path, 160)
      except:
        font = ImageFont.load_default()

      # Procesar cada imagen con la plantilla institucional
      for idx, img_file in enumerate(uploaded_images):
        img = Image.open(img_file)

        if img.mode in ("RGBA", "P"):
          img = img.convert("RGB")

        # 1. Crear lienzo base en Blanco
        template = Image.new("RGB", canvas_size, "white")
        draw = ImageDraw.Draw(template)

        # 2. Ajustar la foto central dejando espacio para los textos masivos de los lados
        max_img_width = 820
        max_img_height = 460
        img.thumbnail((max_img_width, max_img_height), Image.Resampling.LANCZOS)

        # 3. Líneas centrales con gran grosor
        draw.rectangle(
            [
                (0, canvas_height // 2 - 30),
                (canvas_width, canvas_height // 2 + 30),
            ],
            fill="#6B1426",
        )
        draw.rectangle(
            [
                (0, canvas_height // 2 - 10),
                (canvas_width, canvas_height // 2 + 10),
            ],
            fill="#D4AF37",
        )

        # 4. Centrar la foto en el lienzo
        paste_x = (canvas_width - img.width) // 2
        paste_y = (canvas_height - img.height) // 2
        template.paste(img, (paste_x, paste_y))

        # 5. Motor corregido para letras gigantes sin restricciones de tamaño
        def crear_texto_masivo(texto):
          # Creamos una tira vertical del tamaño completo del alto del video (720px) y ancho de 200px
          txt_canvas = Image.new("RGBA", (canvas_height, 200), (255, 255, 255, 0))
          d = ImageDraw.Draw(txt_canvas)
          
          # Escribir el texto con la fuente gigante de 160px
          d.text((15, 10), texto, fill="#6B1426", font=font)
          
          # Rotar 90 grados para que corra verticalmente cubriendo todo el borde
          return txt_canvas.rotate(90, expand=True)

        # Texto izquierdo (ISSSTE)
        txt_izq = crear_texto_masivo("ISSSTE")
        template.paste(txt_izq, (-40, 0), txt_izq)

        # Texto derecho (C.M.F. ERMITA)
        txt_der = crear_texto_masivo("C.M.F. ERMITA")
        template.paste(txt_der, (canvas_width - txt_der.width + 40, 0), txt_der)

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

        st.success("¡Video generado con éxito! Tipografía masiva aplicada.")

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