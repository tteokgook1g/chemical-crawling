import requests
import re
from bs4 import BeautifulSoup
import ghs_korean


def get_html(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        return html
    else:
        print(response.status_code)
        raise requests.HTTPError(response.status_code)


def get_soup(url: str) -> BeautifulSoup:
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_iupac_name(soup: BeautifulSoup) -> str:
    iupac_name = soup.select_one('#firstHeading > span').text
    return iupac_name


def get_property(soup: BeautifulSoup, property_name: str) -> str:
    tag = soup.select_one(f'tr a[title="{property_name}"]')
    while tag.name != 'tr':
        tag = tag.parent
    return tag.select_one('td:nth-child(2)').text.strip()


def to_tex_chemical_formula(text: str) -> str:
    return re.sub(r'(\d+)', r'_{\1}', text)


def get_pictograms(soup: BeautifulSoup) -> list[str]:
    pictograms = []
    tag = soup.select_one('a[title="GHS hazard pictograms"]')
    while tag.name != 'tr':
        tag = tag.parent
    pictograms = tag.select('td span a')
    return [ghs_korean.get_pictogram_korean(p['title']) for p in pictograms]


def get_ghs_signal_word(soup: BeautifulSoup) -> str:
    try:
        tags = soup.select(
            'tr a[title="Globally Harmonized System of Classification and Labelling of Chemicals"]')
        for tag in tags:
            while tag.name != 'tr':
                tag = tag.parent
            if tag.text.strip() == 'Signal word':
                break
        return tag.select_one('td:nth-child(2)').text.strip()
    except:
        return 'Not found'


def get_chemical_formula(soup: BeautifulSoup) -> str:
    text = get_property(soup, 'Chemical formula')
    return to_tex_chemical_formula(text)


def get_hazard_statements(soup: BeautifulSoup):
    tag = soup.select_one('tr a[title="GHS hazard statements"]')
    while tag.name != 'tr':
        tag = tag.parent
    hazard_statements = tag.select('td abbr')
    codes = [h.text for h in hazard_statements]
    return ghs_korean.get_hazard_statement_korean(codes)


def get_molar_mass(soup: BeautifulSoup) -> str:
    text = get_property(soup, "Molar mass")
    return re.findall(r'^([\d.]+)', text)[0]


def main():
    url = input('Enter url: ')
    kor_name = input('Enter Korean name: ')
    soup = get_soup(url)
    iupac_name = get_iupac_name(soup)
    chemical_formula = get_chemical_formula(soup)
    molar_mass = get_molar_mass(soup)
    with open(f'out/{iupac_name}.txt', 'w', encoding='utf-8') as file:
        file.write(
            f'{kor_name}({iupac_name}) {chemical_formula} {molar_mass} g/mol.')
        file.write(
            f'{", ".join(get_pictograms(soup))}. ')
        file.write(f'{get_ghs_signal_word(soup)}. ')
        df = get_hazard_statements(soup)
        df.columns = ['code', 'content']
        statements = df.to_csv(index=False).replace('\r', '')
        file.write(f'\n{statements}\n')
    print(f'Name: {iupac_name} successfully saved.')


if __name__ == '__main__':
    main()
