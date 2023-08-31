import pandas as pd

df_pictogram = pd.read_csv('data/pictogram.csv')
df_hazard = pd.read_csv('data/hazard_statements_kor.csv')


def get_pictogram_korean(pictogram_code: str) -> str:
    try:
        return df_pictogram[df_pictogram['ghs'] == pictogram_code]['korean'].values[0]
    except:
        print(f'Pictogram Not found: {pictogram_code}')
        raise


def get_hazard_statement_korean(hazard_statement_codes: list[str]) -> pd.DataFrame:
    try:
        return df_hazard[df_hazard['code'].isin(hazard_statement_codes)]
    except:
        print(f'Hazard statement Not found: {hazard_statement_codes}')
        raise
