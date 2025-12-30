import requests
from bs4 import BeautifulSoup, Tag

class SoupNavigator:
  @staticmethod
  def navigate(soup: BeautifulSoup | Tag, node: dict):
    return soup

  @staticmethod
  def find(soup: BeautifulSoup | Tag, kwargs: dict):
    return soup.find(**kwargs)
  
  def findAll(soup: BeautifulSoup | Tag, kwargs: dict):
    return soup.find_all(**kwargs)

testSite = 'https://webscraper.io/test-sites/tables'

testData = requests.get(testSite).text

soup = BeautifulSoup(testData, 'html.parser')

testNode = {}

print(SoupNavigator.navigate(testNode, soup))
