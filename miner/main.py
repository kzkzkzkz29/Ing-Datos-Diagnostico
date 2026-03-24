import os
import time
import json
import redis
from src.github_client import GithubClient
from src.LectorMetodos import extract_python_functions, extract_java_methods
from src.procesador import extract_words_from_name

def conectar_redis():
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    
    print(f"Conectando a la cola de mensajes Redis en {host}:{port}")
    return redis.Redis(host=host, port=port, decode_responses=True)

def main():
    print("Iniciando Miner de GitHub")
    
    github = GithubClient()
    cola_redis = conectar_redis()
    
    lenguajes = ["python", "java"]
    pagina_actual = 1
    
    while True:
        for lenguaje in lenguajes:
            print(f"\n Buscando repositorios top de {lenguaje.upper()} (Página {pagina_actual})...")
            
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
                
                for url_archivo in archivos[:5]: 
                    codigo = github.download_file_content(url_archivo)
                    if not codigo:
                        continue
                        
                    if lenguaje == "python":
                        metodos = extract_python_functions(codigo)
                    else:
                        metodos = extract_java_methods(codigo)
                        
                    for metodo in metodos:
                        palabras_limpias = extract_words_from_name(metodo)
                        
                        for palabra in palabras_limpias:
                            mensaje = {
                                "word": palabra,
                                "language": lenguaje,
                                "repository": f"{owner}/{repo_name}"
                            }
                            
                            try:
                                cola_redis.lpush("word_queue", json.dumps(mensaje))
                                print(f"Enviado a cola: {palabra}")
                            except redis.exceptions.ConnectionError:
                                print("\n Redis no está encendido o no es accesible")
                                return 
                                
            time.sleep(2)
            
        pagina_actual += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n Miner detenido por el usuario")