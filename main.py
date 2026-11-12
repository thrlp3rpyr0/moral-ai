import os
import speech_recognition as sr
import pyttsx3
import pywhatkit
import requests
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN DE VOZ (JARVIS VIBE) ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Intentamos configurar una voz en español si está disponible en el sistema
for voice in voices:
    if "spanish" in voice.name.lower() or "es" in voice.id.lower():
        engine.setProperty('voice', voice.id)
        break

engine.setProperty('rate', 170) # Velocidad de la voz

def hablar(texto):
    """Hace que Moral hable en voz alta y muestra el texto en consola"""
    print(f"Moral: {texto}")
    engine.say(texto)
    engine.runAndWait()

# --- FUNCIONES DE MORAL ---

def reproducir_musica_video(query):
    """Reproduce música o videos en YouTube usando pywhatkit"""
    hablar(f"Reproduciendo {query}")
    pywhatkit.playonyt(query)

def obtener_clima(ciudad="Ciudad de México"):
    """Obtiene el clima actual usando web scraping básico de Google"""
    try:
        url = f"https://www.google.com/search?q=clima+{ciudad}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        temperatura = soup.find('span', class_='BNeawe iBp4i AP7Wnd').text
        clima_estado = soup.find('span', class_='BNeawe tAd8D AP7Wnd').text
        
        resultado = f"El clima en {ciudad} es de {temperatura} con {clima_estado}."
        hablar(resultado)
    except Exception as e:
        hablar("No pude obtener el reporte del clima en este momento.")

def buscar_google(query):
    """Busca en Google y lee un resumen del resultado"""
    hablar(f"Buscando {query} en Google.")
    try:
        url = f"https://www.google.com/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Intentar extraer el párrafo de respuesta directa de Google
        extracto = soup.find('div', class_='BNeawe s3v9rd AP7Wnd').text
        hablar(f"Esto es lo que encontré: {extracto}")
    except Exception:
        # Si falla el scraping directo, abre la búsqueda en el navegador como respaldo
        pywhatkit.search(query)
        hablar("He abierto los resultados en tu navegador web.")

# --- BUCLE PRINCIPAL DE VOZ ---
def ejecutar_moral():
    hablar("Sistemas de voz activados. Inicializando Moral.")
    
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Calibrando micrófono contra el ruido ambiente... Guarda silencio un momento.")
        r.adjust_for_ambient_noise(source, duration=1.5)
        print("¡Listo! Moral está escuchando tus órdenes.")

    hablar("Sistema Moral listo. ¿En qué puedo ayudarte?")

    while True:
        try:
            with sr.Microphone() as source:
                print("\nEscuchando comandos...")
                # Timeout de 5s para reintentar si no hablas, límite de 8s por frase
                audio = r.listen(source, timeout=5, phrase_time_limit=8)
            
            # Reconocimiento de voz usando el servicio gratuito de Google en español (México)
            comando = r.recognize_google(audio, language='es-MX').lower()
            print(f"Tú dijiste: {comando}")
            
            # --- PROCESAMIENTO DE COMANDOS ---
            if 'reproduce' in comando or 'canción' in comando or 'video' in comando:
                item = comando.replace('reproduce', '').replace('canción', '').replace('video', '').strip()
                reproducir_musica_video(item)
                
            elif 'clima' in comando:
                obtener_clima()
                
            elif 'busca' in comando or 'investiga' in comando:
                tema = comando.replace('busca', '').replace('investiga', '').strip()
                buscar_google(tema)
                
            elif 'apagar' in comando or 'salir' in comando or 'apágate' in comando:
                hablar("Apagando los sistemas de Moral. Hasta luego.")
                break
            else:
                hablar("No reconozco esa orden. Intenta de nuevo.")

        except sr.WaitTimeoutError:
            # Si pasa el tiempo sin hablar, continúa el ciclo sin errores
            continue
        except sr.UnknownValueError:
            # No se entendió claramente lo que se dijo
            print("No se entendió el audio claramente.")
            continue
        except sr.RequestError:
            hablar("Error de conexión con el servicio de reconocimiento de voz.")
            break
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            continue

if __name__ == "__main__":
    ejecutar_moral()
