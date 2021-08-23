#!/usr/bin/python3
"""Generate a PDF based on data from IP Fabric."""

from time import strftime
from modules.pdfmaker import GeneratePDF
from modules.snapminer import MineSnapshot

API_KEY = '84ce433a3500e31b4169dfca95e62f0'
BASE_URL = 'https://demo4.ipfabric.io/'
SNAPSHOT_ID = '7d06ee21-edab-4582-972b-70a3dcd438ce'
# API_KEY = '36089ed76f47c3e81517878aedded3'  # test11
# BASE_URL = 'http://10.0.9.55'  # test11
# SNAPSHOT_ID = '4f59fa49-bef7-4076-808e-989e0de7a4b9'  # test11
SITE_NAME = 'L66'
SECURE_CONN = True  # If True HTTPS has to be operational
output_file_path = 'export/lld-{}-{}.pdf'.format(SITE_NAME, strftime('%Y%m%d'))


def main():
    """Generate a PDF Low-Level design report based on data from IP Fabric."""
    # Getting Data
    base_dataset = MineSnapshot(
        BASE_URL, SNAPSHOT_ID, SITE_NAME, API_KEY, SECURE_CONN)
    # Creating PDF object
    pdf_object = GeneratePDF()
    # Producing PDF file
    pdf_object.lld_report(base_dataset, SITE_NAME, output_file_path)


if __name__ == "__main__":
    print()
    main()
