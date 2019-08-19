import requests
from bs4 import BeautifulSoup

from scraping import utilities
from pathlib import Path
import json


DEFAULT_URL = 'https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=112'


def get_common_dict(soup):
    common_dict = dict.fromkeys(utilities.DICT_KEYS)
    common_dict['manufacturer'] = 'Thorlabs'

    common_table = soup.find(
        'div', attrs={'class': 'tableFloatRight'}).contents[1].contents[3]

    material_scrap = common_table.contents[3].contents[3].contents[0].text
    common_dict['material'] = material_scrap

    coating_scrap = common_table.contents[5].contents[3].text
    common_dict['wavelength_range_antireflection_coating'] = coating_scrap

    surface_quality_scrap = common_table.contents[15].contents[3].text[:-12]
    common_dict['surface_quality_scratch_dig'] = surface_quality_scrap

    centration_scrap = common_table.contents[25].contents[3].text
    centration_scrap = "".join(filter(str.isdigit, centration_scrap))
    common_dict['centration_arcmin'] = centration_scrap

    clear_aperture_scrap = common_table.contents[27].contents[3].text
    clear_aperture_scrap = "".join(filter(str.isdigit, clear_aperture_scrap))
    common_dict['clear_aperture_percent'] = clear_aperture_scrap

    return common_dict


def run_scrap(url=DEFAULT_URL):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')

    main_container = soup.find('div', attrs={'id': 'sgContainer'})

    lens_output_list = []

    for i in range(len(main_container)):
        group = main_container.contents[i]

        top_table_body = group.find(
            'table', attrs={'class': 'SpecTable'}).tbody
        bottom_table_body = group.find(
            'div', attrs={'class': 'partnumbers'}).contents[1].contents[0].contents[1]

        for j in range(0, len(bottom_table_body) - 1):
            # second index k for top_table
            k = 2 * j + 1

            lens_dict = get_common_dict(soup)

            lens_bottom_row = bottom_table_body.contents[j]
            lens_top_row = top_table_body.contents[k]

            id_scrap = lens_top_row.contents[1].text
            lens_dict['manufacturer_id'] = id_scrap

            description_scrap = lens_bottom_row.find(
                'td', attrs={'class': 'prodDesc'}).text
            lens_dict['description'] = description_scrap

            price_scrap = lens_bottom_row.contents[4].text[:-2]
            price_scrap = price_scrap.replace(',', '.')
            lens_dict['price_vat_ex_euro'] = price_scrap
            
            delivery_scrap = lens_bottom_row.contents[5].text
            lens_dict['delivery'] = delivery_scrap
            
            diameter_scrap = lens_top_row.contents[3].text
            lens_dict['diameter_mm'] = diameter_scrap
            
            focal_length_scrap = lens_top_row.contents[5].text
            lens_dict['focal_length_mm'] = focal_length_scrap
            
            radius_curvature_scrap = lens_top_row.contents[9].text
            lens_dict['radius_curvature_mm'] = radius_curvature_scrap
            
            center_thickness_scrap = lens_top_row.contents[11].text
            lens_dict['center_thickness_mm'] = center_thickness_scrap
            
            edge_thickness_scrap = lens_top_row.contents[13].text
            lens_dict['edge_thickness_mm'] = edge_thickness_scrap
            
            back_focal_length_scrap = lens_top_row.contents[15].text
            lens_dict['back_focal_length_mm'] = back_focal_length_scrap
            
            # console print current lens
            print(json.dumps(lens_dict, indent=4))
            
            # appends lens to result list
            lens_output_list.append(lens_dict)

    # write to json file
    file = open(str(Path(__file__).parent.parent) +
        '/resources/thorlab.json', 'w')
    file.write(json.dumps(lens_output_list, indent=4))
    file.close()


run_scrap()

