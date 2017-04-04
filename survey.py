# -*- coding: utf-8 -*-

"""
This is the module for the survey data processing.
"""

import pandas as pd
import config

SEPARATOR = ";"

ROLES_COLUMN = "What is your role in your current software development project(s)?"

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

    return pd.DataFrame({ROLES_COLUMN: translated_roles})


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


def get_role_information(dataframe_list):
    """
    Get the counts for the main roles
    :param dataframe_list: 
    :return: 
    """
    roles_series = None

    for dataframe in dataframe_list:
        if roles_series is None:
            roles_series = dataframe[ROLES_COLUMN]
        else:
            roles_series = roles_series.append(dataframe[ROLES_COLUMN])

    for role in ROLES:
        boolean_series = roles_series.apply(
            lambda all_roles: type(all_roles) is str and role in all_roles.split(SEPARATOR))

        print "Role: ", role, " Count: ", boolean_series.sum()

    print "Other: ", roles_series.apply(contains_other).sum()


def main():
    apache_df = pd.read_csv(config.SURVEY_DIR + config.APACHE_FILE)
    print "Apache Responses: ", len(apache_df.index)

    english_df = pd.read_csv(config.SURVEY_DIR + config.ENGLISH_FILE)
    print "English Responses: ", len(english_df.index)

    spanish_df = pd.read_csv(config.SURVEY_DIR + config.SPANISH_FILE)
    print "Spanish Responses: ", len(spanish_df.index)

    all_responses = len(apache_df.index) + len(english_df.index) + len(spanish_df.index)
    print "Total responses: ", all_responses

    spanish_df = translate_responses(spanish_df)

    get_role_information([apache_df, english_df, spanish_df])


if __name__ == "__main__":
    main()
