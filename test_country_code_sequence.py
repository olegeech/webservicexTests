# Before run test please install:
# pip install pytest
# pip install zeep
# pip install pytest-allure-adaptor
from enum import Enum
import pytest
from zeep import Client
import xml.etree.ElementTree as xml_tree
import allure

WSDL = 'http://www.webservicex.net/country.asmx?WSDL'


class Tags(Enum):
    NAME = 'name'
    CURRENCY = 'Currency'
    CURRENCY_CODE = 'CurrencyCode'


def get_tag_value_dicts(xml_string):
    tables = []
    xml = xml_tree.fromstring(xml_string)
    for table in xml.getiterator('Table'):
        for child in table:
            tables.append({child.tag: child.text})
    return tables


def get_values(dicts, tag_name):
    currency_codes = []
    for currency_code_dict in dicts:
        if tag_name in currency_code_dict:
            currency_codes.append(currency_code_dict[tag_name])
    return currency_codes


@pytest.yield_fixture
def get_soap_client_service():
    yield Client(WSDL).service


# TODO: BUG or FEATURE that tables are duplicated is considered :)
@pytest.mark.parametrize("country_code,country,currency,currency_code",
                         [
                             ("qa", "Qatar", "Rial", "QAR"),
                             ("om", "Oman", "Rial", "OMR")
                         ])
def test_country_code_sequence(country_code, country, currency, currency_code, get_soap_client_service):
    with allure.step('Get country by country code'):
        country_data1 = get_soap_client_service.GetCountryByCountryCode(country_code)
        country_dicts1 = get_tag_value_dicts(country_data1)
        countries1 = get_values(country_dicts1, Tags.NAME.value)
        assert country in countries1
    with allure.step('Get currency by country'):
        currency_data2 = get_soap_client_service.GetCurrencyByCountry(countries1[0])
        currency_dicts2 = get_tag_value_dicts(currency_data2)
        currencies2 = get_values(currency_dicts2, Tags.CURRENCY.value)
        currency_codes2 = get_values(currency_dicts2, Tags.CURRENCY_CODE.value)
        assert currency in currencies2
        assert currency_code in currency_codes2
    with allure.step('Get country by currency code'):
        country_data3 = get_soap_client_service.GetCountryByCurrencyCode(currency_codes2[0])
        currency_dicts3 = get_tag_value_dicts(country_data3)
        currencies3 = get_values(currency_dicts3, Tags.CURRENCY.value)
        currency_codes3 = get_values(currency_dicts3, Tags.CURRENCY_CODE.value)
        assert currencies3 == currencies2
        assert currency_codes3 == currency_codes2
    with allure.step('Get currency code by currency name'):
        currency_data4 = get_soap_client_service.GetCurrencyCodeByCurrencyName(currencies3[0])
        currency_code_dicts = get_tag_value_dicts(currency_data4)
        assert currency_code in get_values(currency_code_dicts, Tags.CURRENCY_CODE.value)
