import os
from gtts import gTTS
from moviepy import AudioFileClip, ImageSequenceClip
from PIL import Image, ImageDraw
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Generador de Videos - ISSSTE C.M.F. Ermita",
    page_icon="🎬",
    layout="centered",
)

st.title("🎬 Generador Diario de Videos para Difusión con Audio")
st.write(
    "Sube tus imágenes laterales, tus fotos principales, escribe un texto descriptivo para cada una y genera tu video institucional con voz automatizada."
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

# 2. Sección para cargar las imágenes principales del día y sus textos descriptivos
st.subheader("🖼️ 2. Imágenes Principales y Textos para Audio")
uploaded_images = st.file_uploader(
    "Sube las fotos centrales del día (puedes seleccionar varias):",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key="principal",
)

# Diccionario o lista para almacenar los textos ingresados por el usuario
image_texts = {}

if uploaded_images:
  st.markdown(
      "--- \n ✍️ **Escribe el texto que se dirá en audio para cada imagen:**"
  )
  for idx, img_file in enumerate(uploaded_images):
    col_img, col_txt = st.columns([1, 2])
    with col_img:
      st.image(img_file, width=150, caption=f"Imagen {idx + 1}")
    with col_txt:
      image_texts[idx] = st.text_area(
          f"Texto para la imagen {idx + 1}:",
          placeholder="Ej. Hoy realizamos jornada de vacunación...",
          key=f"text_{idx}",
          height=100,
      )
  st.markdown("---")

# Configuración de duración por imagen por defecto (si no hay audio o por seguridad)
duracion_defecto = st.slider(
    "Duración mínima por imagen (segundos):",
    min_value=2,
    max_value=10,
    value=4,
)

if uploaded_images:
  # 3. Botón para crear el video con audio
  if st.button("🚀 Crear Video Institucional con Audio"):
    with st.spinner(
        "Generando audios, procesando plantillas y renderizando video..."
    ):
      temp_dir = "temp_multimedia"
      os.makedirs(temp_dir, exist_ok=True)

      image_paths = []
      audio_clips = []
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

      # Procesar cada imagen principal y su texto
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
                (0, canvas_height // 2 - 60),
                (canvas_width, canvas_height // 2 + 60),
            ],
            fill="#6B1426",
        )
        draw.rectangle(
            [
                (0, canvas_height // 2 - 20),
                (canvas_width, canvas_height // 2 + 20),
            ],
            fill="#D4AF37",
        )

        # 3. Procesar y pegar la Imagen Central Principal (Tamaño máximo)
        max_img_width = 1120
        max_img_height = 640
        img.thumbnail((max_img_width, max_img_height), Image.Resampling.LANCZOS)

        paste_x = (canvas_width - img.width) // 2
        paste_y = (canvas_height - img.height) // 2
        template.paste(img, (paste_x, paste_y))

        # 4. Insertar imagen lateral IZQUIERDA
        if lat_izq_img:
          target_w = 180
          target_h = int(
              lat_izq_img.height
              * (target_w / lat_izq_img.width)
          )
          lat_izq_resized = lat_izq_img.resize(
              (int(target_w), int(target_h)), Image.Resampling.LANCZOS
          )
          pos_izq_x = 25
          pos_izq_y = (canvas_height - lat_izq_resized.height) // 2
          template.paste(
              lat_izq_resized,
              (pos_izq_x, pos_izq_y),
              lat_izq_resized,
          )

        # 5. Insertar imagen lateral DERECHA
        if lat_der_img:
          target_w = 180
          target_h = int(
              lat_der_img.height
              * (target_w / lat_der_img.width)
          )
          lat_der_resized = lat_der_img.resize(
              (int(target_w), int(target_h)), Image.Resampling.LANCZOS
          )
          pos_der_x = canvas_width - lat_der_resized.width - 25
          pos_der_y = (canvas_height - lat_der_resized.height) // 2
          template.paste(
              lat_der_resized,
              (pos_der_x, pos_der_y),
              lat_der_resized,
          )

        # Guardar imagen procesada temporalmente
        img_path = os.path.join(temp_dir, f"img_{idx:03d}.jpg")
        template.save(img_path, "JPEG", quality=95)
        image_paths.append(img_path)

        # Generar audio correspondiente a partir del texto ingresado
        texto_actual = image_texts.get(idx, "").strip()
        if texto_actual:
          tts = gTTS(text=texto_actual, lang="es", slow=False)
          audio_path = os.path.join(temp_dir, f"audio_{idx:03d}.mp3")
          tts.save(audio_path)

          # Cargar clip de audio para medir su duración exacta
          from moviepy import AudioFileClip

          a_clip = AudioFileClip(audio_path)
          audio_clips.append(a_clip)
        else:
          # Si no hay texto, creamos un audio de silencio o usamos duración por defecto
          # Para simplificar con ImageSequenceClip asignamos duración por defecto si falta texto
          audio_clips.append(None)

      # Ruta del video resultante
      output_video_path = "video_difusion_con_audio.mp4"

      try:
        # Calcular duraciones individuales basadas en el audio si existen, o usar estándar
        duraciones = []
        final_audio_clips = []

        # Como moviepy requiere manejar concatenación de audios de forma precisa,
        # asignaremos duraciones y unificaremos el audio total.
        from moviepy import concatenate_audioclips, concatenate_videoclips

        clip_list = []
        for i, path in enumerate(image_paths):
          dur = duracion_defecto
          if i < len(audio_clips) and audio_clips[i] is not None:
            dur = max(audio_clips[i].duration + 0.5, duracion_defecto)

          # Crear clip individual de imagen con su duración específica
          from moviepy import ImageClip

          img_clip = ImageClip(path).with_duration(dur)

          if i < len(audio_clips) and audio_clips[i] is not None:
            # Sincronizar audio con el clip de imagen
            img_clip = img_clip.with_audio(audio_clips[i])

          clip_list.append(img_clip)

        # Unir todos los clips de video en secuencia
        final_video = concatenate_videoclips(clip_list, method="compose")

        # Exportar video final con audio integrado
        final_video.write_videofile(
            output_video_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
        )

        st.success(
            "¡Video institucional con locución en audio generado con éxito!"
        )

        # Reproductor y Botón de Descarga
        st.subheader("▶️ Vista previa del video con audio:")
        video_file = open(output_video_path, "rb")
        video_bytes = video_file.read()
        st.video(video_bytes)

        st.download_button(
            label="📥 Descargar Video con Audio",
            data=video_bytes,
            file_name="difusion_institucional_audio.mp4",
            mime="video/mp4",
        )

      except Exception as e:
        st.error(f"Ocurrió un error al generar el video con audio: {e}")

      finally:
        # Limpieza de archivos temporales
        for path in image_paths:
          if os.path.exists(path):
            os.remove(path)
        for i in range(len(uploaded_images)):
          a_path = os.path.join(temp_dir, f"audio_{i:03d}.mp3")
          if os.path.exists(a_path):
            os.remove(a_path)
        if os.path.exists(temp_dir):
          os.rmdir(temp_dir)