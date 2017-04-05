# -*- coding: utf-8 -*-

"""
This is the module for the survey data processing.
"""
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import config

SEPARATOR = ";"

ROLES_COLUMN = "What is your role in your current software development project(s)?"
DEFLATION_COLUMN = "Considering your current software project(s): How often is priority understated (or deflated) " \
                   "in bug reports?"
INFLATION_COLUMN = "Considering your current software project(s): How often is priority overstated (or inflated)" \
                   " in bug reports?"
IMPACT_COLUMN = "Is priority inflation/deflation affecting your work?"

DEVELOPER = "Developer"
TESTER = "Tester"
PROJECT_MANAGER = "Project Manager"
ARCHITECT = "Architect"
BUSINESS_ANALYST = "Business Analyst"

ROLES = [DEVELOPER, TESTER, PROJECT_MANAGER, ARCHITECT, BUSINESS_ANALYST]


def translate_roles(spanish_roles):
    role_translation_map = {"Desarrollador": "Developer",
                            "Analista de Calidad": "Tester",
                            "Jefe de Proyecto": "Project Manager",
                            "Arquitecto": "Architect",
                            "Analista Funcional": "Business Analyst",
                            "Líder técnico": "Technical Lead",
                            "Gobierno TI": "IT Governance",
                            "Tester": "Tester",
                            "Asegurador de Calidad": "Quality Assurance",
                            "Jefe de Desarrollo y Sistemas": "Development Manager",
                            "DBA": "DBA"}

    if type(spanish_roles) is str:
        english_roles = [role_translation_map[spanish_role] for spanish_role in spanish_roles.split(SEPARATOR)]
        return SEPARATOR.join(english_roles)

    return spanish_roles


def translate_responses(spanish_df):
    """
    Translate the relevant information to English
    :param spanish_df: Survey responses in spanish
    :return: Translated dataframe
    """
    roles_column_es = " ¿Qué roles cumples en el proyecto de desarrollo de Software en el que estás participando?"
    translated_roles = spanish_df[roles_column_es].apply(translate_roles).values

    frequency_translation = {"Frecuentemente": "Frequently",
                             "Ocasionalmente": "Occasionally",
                             "Nunca": "Never"}

    deflation_column_es = "En tu proyecto actual ¿Con qué frecuencia se subestima el valor del campo prioridad " \
                          "al reportar un defecto de software?"
    translated_deflations = spanish_df[deflation_column_es].map(frequency_translation).values

    inflation_column_es = "En tu proyecto actual ¿Con qué frecuencia se exagera el valor del campo prioridad" \
                          " al reportar un defecto de software?"
    translated_inflations = spanish_df[inflation_column_es].map(frequency_translation).values

    impact_translation = {"No tienen impacto alguno": "It has no impact",
                          "Tienen un impacto mínimo": "Its impact is minimum",
                          "Tienen un impacto significativo": "It has a significant impact"}
    impact_column_es = " ¿Qué impacto tienen estas prioridades exageradas o subestimadas en tu trabajo diario?"
    translated_impacts = spanish_df[impact_column_es].map(impact_translation).values

    return pd.DataFrame({ROLES_COLUMN: translated_roles,
                         DEFLATION_COLUMN: translated_deflations,
                         INFLATION_COLUMN: translated_inflations,
                         IMPACT_COLUMN: translated_impacts})


def contains_other(all_roles):
    """
    Returns True if the response contains a custom role.
    :param all_roles: 
    :return: 
    """
    if type(all_roles) is str:
        role_list = all_roles.split(SEPARATOR)
        difference = set(role_list) - set(ROLES)

        if len(difference) > 0:
            return True

    return False


def merge_columns(dataframe_list, column_name):
    """
    Merges the same column in several dataframes.
    :param dataframe_list: List of dataframe
    :param column_name: Name of the column
    :return: Merged series.
    """
    roles_series = None

    for dataframe in dataframe_list:
        if roles_series is None:
            roles_series = dataframe[column_name]
        else:
            roles_series = roles_series.append(dataframe[column_name])

    return roles_series


def get_role_information(roles_series):
    """
    Get the counts for the main roles
    :param dataframe_list: 
    :return: 
    """
    for role in ROLES:
        boolean_series = roles_series.apply(
            lambda all_roles: type(all_roles) is str and role in all_roles.split(SEPARATOR))

        print "Role: ", role, " Count: ", boolean_series.sum()

    print "Other: ", roles_series.apply(contains_other).sum()


def get_frequency_chart(frequency_series, file_name, figsize=(6, 6)):
    """
    Produces an image of the deflation chart.
    :param deflation_series: 
    :return: 
    """

    counts = frequency_series.value_counts(normalize=True)
    counts.name = ""
    print "Generating ", file_name, " from ", frequency_series.count(), " responses:\n", counts

    plt.figure()
    counts.plot.pie(autopct='%.2f%%', figsize=figsize)
    plt.savefig(file_name)


def main():
    apache_df = pd.read_csv(config.SURVEY_DIR + config.APACHE_FILE)
    print "Apache Responses: ", len(apache_df.index)

    english_df = pd.read_csv(config.SURVEY_DIR + config.ENGLISH_FILE)
    print "English Responses: ", len(english_df.index)

    spanish_df = pd.read_csv(config.SURVEY_DIR + config.SPANISH_FILE)
    print "Spanish Responses: ", len(spanish_df.index)

    all_responses = len(apache_df.index) + len(english_df.index) + len(spanish_df.index)
    print "Total responses: ", all_responses

    translated_df = translate_responses(spanish_df)

    all_dataframes = [apache_df, english_df, translated_df]

    get_role_information(merge_columns(all_dataframes, ROLES_COLUMN))

    matplotlib.style.use('ggplot')
    get_frequency_chart(merge_columns(all_dataframes, DEFLATION_COLUMN), "deflation_plot.png")
    get_frequency_chart(merge_columns(all_dataframes, INFLATION_COLUMN), "inflation_plot.png")
    get_frequency_chart(merge_columns(all_dataframes, IMPACT_COLUMN), "impact_plot.png", figsize=(8, 8))

    remedies_column_es = "Si las prioridades exageradas o subestimadas afectan tu trabajo diario, por favor detalla de " \
                         "qué manera y si se están tomando medidas para evitar que esto suceda."
    remedies_column_en = "If priority inflation/deflation is affecting your work, please detail how and what steps are " \
                         "being taken to address it."

    remedies_responses = spanish_df[remedies_column_es].count() + apache_df[remedies_column_en].count() + english_df[
        remedies_column_en].count()
    print "Number of responses containing remedies: ", remedies_responses


if __name__ == "__main__":
    main()
