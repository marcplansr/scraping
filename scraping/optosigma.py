import requests
from bs4 import BeautifulSoup

from scraping import utilities
from pathlib import Path
import json


DEFAULT_URL = 'https://europe.optosigma.com/spherical-lens-bk7-plano-convex-uncoated.html'

# max number of results, <= 0 to return all results
NUMBER_RESULTS = 10 


def run_scrap(url=DEFAULT_URL):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')

    main_container = soup.find('div', attrs={'class': 'grouped-container'})
    lens_table = main_container.findAll('tr', attrs={'class': 'grouped-item'})

    lens_output_list = []

    for i in range(len(lens_table)):
        lens = lens_table[i]

        lens_dict = dict.fromkeys(utilities.DICT_KEYS)

        lens_dict['manufacturer'] = 'OptoSigma'

        id_scrap = lens.find('span', attrs={'class': 'sku-cell'}).text
        lens_dict['manufacturer_id'] = id_scrap

        description_scrap = lens.find('a', attrs={'class': 'link'}).text
        lens_dict['description'] = description_scrap

        diameter_scrap = lens.find('td', attrs={
            'class': 'grouped-item-cell grouped-item-cell-attribute first-attribute'}).text[1:-2]
        lens_dict['diameter_mm'] = diameter_scrap

        focal_length_scrap = lens.find(
            'td', attrs={'class': 'grouped-item-cell grouped-item-cell-attribute'}).text[:-2]
        lens_dict['focal_length_mm'] = focal_length_scrap

        price_scrap = lens.find('span', attrs={'class': 'price'}).text[1:]
        lens_dict['price_vat_ex_euro'] = price_scrap

        delivery_scrap = lens.contents[7].div['data-delivery']
        lens_dict['delivery'] = delivery_scrap

        specs_url = lens.a['href']
        specs_r = requests.get(specs_url)
        specs_soup = BeautifulSoup(specs_r.content, 'html5lib')
        specs_container = specs_soup.find(
            'table', attrs={'class': 'product-attributes product-attributes--simple'}).tbody

        specs_scrap_dict = {
            'material_scrap': 9,
            'coating_scrap': 11,
            'edge_thickness_scrap': 13,
            'center_thickness_scrap': 15,
            'back_focal_length_scrap': 17,
            'radius_curvature_scrap': 19,
            'centration_scrap': 21,
            'surface_quality_scrap': 23,
            'clear_aperture_scrap': 25
        }

        for scrap in specs_scrap_dict:
            scrap_value = specs_container.contents[(specs_scrap_dict.get(
                scrap))].find('td', attrs={'class': 'product-attribute-value'}).text
            scrap_value = scrap_value.lstrip('\n ').rstrip('\n ')
            specs_scrap_dict[scrap] = scrap_value

        lens_dict['material'] = specs_scrap_dict.get('material_scrap')
        lens_dict['wavelength_range_antireflection_coating'] = specs_scrap_dict.get(
            'coating_scrap')
        lens_dict['edge_thickness_mm'] = specs_scrap_dict.get('edge_thickness_scrap')[
            :-2]
        lens_dict['center_thickness_mm'] = specs_scrap_dict.get(
            'center_thickness_scrap')[:-2]
        lens_dict['back_focal_length_mm'] = specs_scrap_dict.get(
            'back_focal_length_scrap')[:-2]
        lens_dict['radius_curvature_mm'] = specs_scrap_dict.get(
            'radius_curvature_scrap')[:-2]
        
        # filter only digits prev to adding to dictionary
        centration_scrap_value = specs_scrap_dict.get('centration_scrap')
        centration_scrap_value = ''.join(
            filter(str.isdigit, centration_scrap_value))
        lens_dict['centration_arcmin'] = centration_scrap_value
        
        lens_dict['surface_quality_scratch_dig'] = specs_scrap_dict.get(
            'surface_quality_scrap')

        # filter only digits prev to adding to dictionary
        clear_aperture_scrap_value = specs_scrap_dict.get(
            'clear_aperture_scrap')
        clear_aperture_scrap_value = ''.join(
            filter(str.isdigit, clear_aperture_scrap_value))
        lens_dict['clear_aperture_percent'] = clear_aperture_scrap_value
        
        # console print current lens
        print(json.dumps(lens_dict, indent=4))
        
        # appends lens to result list
        lens_output_list.append(lens_dict)
        
        # break in case number of results reach limit
        if(NUMBER_RESULTS > 0 and len(lens_output_list) == NUMBER_RESULTS):
            break
        
    # write to json file
    file = open(str(Path(__file__).parent.parent) +
                '/resources/optosigma.json', 'w')
    file.write(json.dumps(lens_output_list, indent=4))
    file.close()


run_scrap()

