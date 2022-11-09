import requests
import lxml.html as html
import datetime
import os

SCRAPING_CONSTANTS = {
    "XPATH_LINK_TO_ARTICLE": "//text-fill[not(@class)]/a/@href",
    "XPATH_TITLE": '//div[@class="mb-auto"]/h2/span/text()',
    "XPATH_SUMMARY": '//div[@class="lead"]/p/text()',
    "XPATH_CONTENT": '//div[@class="html-content"]/p/descendant-or-self::*/text()',
    "XPATH_TARGET": 'https://www.larepublica.co'
}


def parse_home() -> html:
    '''Realiza una petición GET a XPATH_TARGET para recibir el HTML como string y lo convierte a un documento que pueda ser manipulado con XPATH.'''
    try:
        request_response = requests.get(SCRAPING_CONSTANTS["XPATH_TARGET"])
        if request_response.status_code == 200:
            home = request_response.content.decode('utf-8')
            # Contenido html en home => Documento especial para hacer xpath
            parsed = html.fromstring(home)
            return parsed
        else:
            # Codigo de respuesta de la peticion HTTP
            raise ValueError(f'Error: {request_response.status_code}')

    except ValueError as ve:
        print("ValueError en parse_home. Detalles: \n", ve)
    except Exception as e:
        print("Error en parse_home. Detalles: \n", e)


def parse_notice(link: str, today: str):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            news = response.content.decode('utf-8')
            parsed = html.fromstring(news)
            try:
                title = parsed.xpath(SCRAPING_CONSTANTS["XPATH_TITLE"])[0]
                title = title.replace('\"', '')  # Evitar titulos con comillas
                title = title.strip()
                title = title.replace('“', '')
                title = title.replace('?', '').replace(
                    '¿', '').replace('!', '').replace('¡', '')
                title = title.replace('%', '').replace('$', '').replace('#', '').replace('@', '').replace('&', '').replace('*', '').replace('+', '').replace('=', '').replace('-', '').replace(
                    '_', '').replace('/', '').replace('\\', '').replace('|', '').replace('<', '').replace('>', '').replace('"', '').replace('\'', '')  # remove the special characters from the title
                summary = parsed.xpath(SCRAPING_CONSTANTS["XPATH_SUMMARY"])[0]
                body = parsed.xpath(SCRAPING_CONSTANTS["XPATH_CONTENT"])
                
            except IndexError:  # Evitar problemas con noticias que no tengan resumen
                return

            with open(f'Scrap_outputs/{today}/{title}.txt', 'w', encoding='utf-8') as f:
                f.write(title)
                f.write('\n\n')
                f.write(summary)
                f.write('\n\n')
                for p in body:
                    f.write(p)
                    f.write('\n')
                f.write('\n\n\n')
                f.write(f'Link de la noticia: {link}')
        else:
            raise ValueError(f'Error: {response.status_code}')

    except ValueError as ve:
        print("ValueError en parse_notice. Detalles: \n", ve)
    except Exception as e:
        print("Error en parse_notice. Detalles: \n", e)


def xpath_flow(parsed: html):
    '''Función para llevar el flujo de XPATH, toma un documento HTML preparado para manipularlo con XPATH y se encarga de extraer los links de noticias de la pagina objetivo y llamar una función para el análisis de cada link'''
    try:
        today = datetime.date.today().strftime('%d-%m-%y')
        link_to_news = parsed.xpath(
            SCRAPING_CONSTANTS["XPATH_LINK_TO_ARTICLE"])
        if not os.path.isdir("Scrap_outputs/"+today):
            os.mkdir("Scrap_outputs/"+today)
        for link in link_to_news:
            parse_notice(link, today)
    except Exception as e:
        print("Error en xpath_flow. Detalles: \n", e)


def run_flow():
    parsed_document = parse_home()
    xpath_flow(parsed_document)


if __name__ == "__main__":
    run_flow()
