import os
import time
import json
import redis
from src.github_client import GithubClient
from src.LectorMetodos import extract_python_functions, extract_java_methods
from src.procesador import extract_words_from_name

def conectar_redis():
    """Establece la conexión con la cola de mensajes Redis."""
    # Lee las variables del .env, pero si no existen, usa valores por defecto
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    
    print(f"Conectando a la cola de mensajes Redis en {host}:{port}")
    # decode_responses=True hace que Redis nos devuelva strings normales y no bytes raros
    return redis.Redis(host=host, port=port, decode_responses=True)

def main():
    print("Iniciando Miner de GitHub")
    
    # 1. Inicializamos nuestras herramientas
    github = GithubClient()
    cola_redis = conectar_redis()
    
    # 2. Variables de control para el bucle continuo
    lenguajes = ["python", "java"]
    pagina_actual = 1
    
    # 3. EL BUCLE INFINITO (Requisito: proceso continuo)
    while True:
        for lenguaje in lenguajes:
            print(f"\n Buscando repositorios top de {lenguaje.upper()} (Página {pagina_actual})...")
            
            # Traemos 2 repositorios por página para no saturar la consola tan rápido
            repositorios = github.search_popular_repos(language=lenguaje, page=pagina_actual, per_page=2)
            
            if not repositorios:
                print("No hay más repositorios o se llego al límite de la API")
                time.sleep(60)
                continue
                
            for repo in repositorios:
                owner = repo["owner"]["login"]
                repo_name = repo["name"]
                branch = repo["default_branch"]
                
                print(f"\n Analizando Repositorio: {owner}/{repo_name}")
                
                extension = ".py" if lenguaje == "python" else ".java"
                archivos = github.get_files_from_repo(owner, repo_name, branch, (extension,))
                
                print(f" Encontrados {len(archivos)} archivos")
                
                # Limitamos a los primeros 5 archivos por repositorio para que sea dinámico
                for url_archivo in archivos[:5]: 
                    codigo = github.download_file_content(url_archivo)
                    if not codigo:
                        continue
                        
                    # Usamos el extractor adecuado
                    if lenguaje == "python":
                        metodos = extract_python_functions(codigo)
                    else:
                        metodos = extract_java_methods(codigo)
                        
                    # Procesamos cada método encontrado
                    for metodo in metodos:
                        palabras_limpias = extract_words_from_name(metodo)
                        
                        for palabra in palabras_limpias:
                            # 4. EMPAQUETADO DEL MENSAJE (Formato JSON)
                            mensaje = {
                                "word": palabra,
                                "language": lenguaje,
                                "repository": f"{owner}/{repo_name}"
                            }
                            
                            # 5. ENVÍO A REDIS (El Productor trabajando)
                            try:
                                # lpush empuja el mensaje a una lista llamada 'word_queue'
                                cola_redis.lpush("word_queue", json.dumps(mensaje))
                                print(f"Enviado a cola: {palabra}")
                            except redis.exceptions.ConnectionError:
                                print("\n Redis no está encendido o no es accesible")
                                return # Detenemos el script si no hay base de datos
                                
            # Pausa táctica entre repositorios
            time.sleep(2)
            
        # Avanzamos a la siguiente página de popularidad
        pagina_actual += 1

if __name__ == "__main__":
    # Capturamos el Ctrl+C para salir elegantemente sin mostrar errores feos
    try:
        main()
    except KeyboardInterrupt:
        print("\n Miner detenido por el usuario")