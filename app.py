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
    with st.spinner("Generando video con textos laterales gigantes y bien posicionados..."):
      temp_dir = "temp_imagenes"
      os.makedirs(temp_dir, exist_ok=True)

      image_paths = []
      canvas_width, canvas_height = 1280, 720
      canvas_size = (canvas_width, canvas_height)

      # Fuente grande y visible
      try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(font_path, 110)
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

        # 2. Ajustar la foto central
        max_img_width = 840
        max_img_height = 480
        img.thumbnail((max_img_width, max_img_height), Image.Resampling.LANCZOS)

        # 3. Líneas centrales con gran grosor
        draw.rectangle(
            [
                (0, canvas_height // 2 - 25),
                (canvas_width, canvas_height // 2 + 25),
            ],
            fill="#6B1426",
        )
        draw.rectangle(
            [
                (0, canvas_height // 2 - 8),
                (canvas_width, canvas_height // 2 + 8),
            ],
            fill="#D4AF37",
        )

        # 4. Centrar la foto en el lienzo
        paste_x = (canvas_width - img.width) // 2
        paste_y = (canvas_height - img.height) // 2
        template.paste(img, (paste_x, paste_y))

        # 5. Función corregida para centrar perfectamente el texto vertical de extremo a extremo
        def crear_texto_vertical_exacto(texto):
          # Creamos un bloque transparente que mide exactamente el alto del video (720px) x 150px de ancho
          txt_canvas = Image.new("RGBA", (150, canvas_height), (255, 255, 255, 0))
          d = ImageDraw.Draw(txt_canvas)
          
          # Como vamos a rotar 90 grados, dibujamos el texto horizontalmente primero dentro de este bloque,
          # pero girado de abajo hacia arriba o viceversa. Usamos rotate(90, expand=True) sobre un lienzo 
          # donde la dimensión horizontal sea el alto del canvas.
          pass

        # Método directo y seguro: creamos una tira horizontal del tamaño del alto del video (720x150)
        def generar_tira_rotada(texto):
          # Lienzo horizontal temporal de 720 de ancho por 150 de alto
          tira = Image.new("RGBA", (720, 150), (255, 255, 255, 0))
          d = ImageDraw.Draw(tira)
          
          # Escribir el texto centrado horizontalmente en la tira
          # Usamos textbbox para medir el texto y centrarlo a lo largo de los 720 píxeles
          bbox = d.textbbox((0, 0), texto, font=font)
          text_width = bbox[2] - bbox[0]
          text_height = bbox[3] - bbox[1]
          
          x_pos = (720 - text_width) // 2
          y_pos = (150 - text_height) // 2 - 10
          
          d.text((x_pos, y_pos), texto, fill="#6B1426", font=font)
          
          # Rotar 90 grados en sentido horario para que quede vertical de arriba a abajo
          return tira.rotate(90, expand=True)

        # Texto izquierdo (ISSSTE)
        txt_izq = generar_tira_rotada("ISSSTE")
        # Se pega exactamente pegado a la izquierda (X=5, Y=0)
        template.paste(txt_izq, (5, 0), txt_izq)

        # Texto derecho (C.M.F. ERMITA)
        txt_der = generar_tira_rotada("C.M.F. ERMITA")
        # Se pega exactamente pegado a la derecha
        template.paste(txt_der, (canvas_width - txt_der.width - 5, 0), txt_der)

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

        st.success("¡Video generado con éxito! Textos verticales alineados de extremo a extremo.")

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