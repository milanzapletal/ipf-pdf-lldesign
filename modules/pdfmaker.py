#!/usr/bin/python3
import json
from time import ctime, strftime
from fpdf import FPDF, HTMLMixin



class CreatePDF(FPDF, HTMLMixin):
    """Create PDF object."""

    def __str__(self):
        """Describe the object."""
        return 'To create PDF object.'

    def header(self):
        """Create page header."""
        # Position at 1.5 cm from top
        self.set_y(15)
        # Logo
        self.image('images/logoIPF.png', 2, 2, 33)
        # Picture
        self.image('images/headerIPF.png', 120, -15, 100)

    def footer(self):
        """Create page footer."""
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # helvetica italic 8
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(160, 160, 160)
        # Page number
        self.cell(45, 10, 'Page ' + str(self.page_no()), 0, 0, 'L')
        self.cell(100, 10, 'IP Fabric - Low Level Design', 0, 0, 'C')
        self.cell(45, 10, strftime("%c"), 0, 0, 'R')


class GeneratePDF:
    """Generate PDF report."""

    def __init__(self):
        self.author = 'author, XX'
        self.date_now = strftime("%c")
        self.main_font = 'helvetica'

    def create_pdf(self):
        """Create PDF objectasd."""
        pdf = CreatePDF(orientation="P", unit="mm", format="A4")
        pdf.set_author(self.author)
        pdf.set_font(self.main_font, '', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(1, 33, 74)
        pdf.set_draw_color(150, 150, 150)
        self.table_height = pdf.font_size * 1.4
        return pdf

    def lld_report(self, base_dataset, site_name, output_file_path):
        """Supply PDF object with data and output into a lld report file."""
        pdf = self.create_pdf()
        mgmt_data = base_dataset.mine_management()
        platform_data = base_dataset.mine_base_data()
        snapshot_data = base_dataset.mine_snap_data()

        fonts = {
            'bold': {'rgb': (0, 0, 0), 'style': 'B', 'size': 12},
            'default': {'rgb': (0, 0, 0), 'style': '', 'size': 12},
            'title1': {'rgb': (1, 33, 74), 'style': 'B', 'size': 18},
            'title2': {'rgb': (1, 33, 74), 'style': 'B', 'size': 16},
            'title3': {'rgb': (1, 33, 74), 'style': 'B', 'size': 14},
            'table_title': {'rgb': (230, 230, 230), 'style': 'B', 'size': 12},
        }

        def set_font(font):
            pdf.set_text_color(font['rgb'][0], font['rgb'][1], font['rgb'][2])
            pdf.set_font(self.main_font, font['style'], font['size'])

        def add_title(input_title, font):
            set_font(fonts[font])
            pdf.multi_cell(0, 8, input_title, 0, align='L')

        def add_title_link(input_title1, input_link1, font):
            set_font(fonts[font])
            pdf.cell(0, 8, input_title1, 0, align='L', ln=1, link=input_link1)

        def add_text(input_text):
            set_font(fonts['default'])
            pdf.multi_cell(0, 5, input_text, 0, align='J')

        def add_space():
            pdf.multi_cell(0, 5, '', 0, align='C')

        def add_link(link_name):
            pdf.set_link(link_name, y=pdf.get_y(), page=pdf.page_no())

        def add_mgmt_data(mgmt_input):
            for item in mgmt_input:
                set_font(fonts['table_title'])
                pdf.multi_cell(0, self.table_height, item, border=1, align="C", fill=True)
                set_font(fonts['default'])
                pdf.multi_cell(0, self.table_height, str(mgmt_input[item]), border=1, align="L")
                pdf.ln(self.table_height)

        def add_platform_data(platform_input):
            for idx, item in enumerate(platform_input):
                if idx != 0:
                    set_font(fonts['default'])
                    pdf.cell(70, self.table_height, item, border=1, align="C")
                    pdf.cell(116, self.table_height, str(platform_input[item]), border=1, align="C")
                else:
                    set_font(fonts['table_title'])
                    pdf.cell(70, self.table_height, item, border=1, align="C", fill=True)
                    pdf.cell(116, self.table_height, platform_input[item], border=1, align="C", fill=True)
                pdf.ln(self.table_height)

        def load_json(json_input):
            with open(json_input, 'r') as file:
                print('  -- Reading JSON file: ', json_input)
                json_object = json.load(file)
            return json_object

        txt_source = load_json('./srctext/lld-text.json')
        # Adding PART 0 - First page
        pdf.add_page()
        pdf.cell(0, 100, '', 0, ln=1, align='C')
        pdf.set_font_size(32)
        pdf.set_text_color(1, 33, 74)
        pdf.cell(0, 20, 'Low-Level Design - {}'.format(site_name), 0, ln=1, align='C')
        pdf.set_font_size(16)
        pdf.cell(0, 20, self.date_now, 0, ln=1, align='C')

        # Generating links for Table of Content
        link_1 = pdf.add_link()
        link_site_overview = pdf.add_link()
        link_mgmt_protocols = pdf.add_link()

        # Adding PART 1 - Table of content
        pdf.add_page()
        add_title('Table of content', 'title1')
        add_space()
        # add_title_link(txt_source['1-title'], link_1, 'title1')
        # add_title_link('      1.1 Network Overview', link_network_overview, 'title2')
        # add_title_link('      1.2 Management Protocols Summary', link_management_protocols, 'title2')
        for chapter in txt_source.keys():
            title = txt_source[chapter]['title']
            title_num = chapter.split('chapter')[1]
            title_num_len = len(title_num)
            text_pars = txt_source[chapter]['text']
            if title_num_len == 1:
                pdf.add_page()
            add_title(title_num + ' ' + title, 'title{}'.format(title_num_len))
            for par in text_pars:
                add_text(par)
                add_space()
            if chapter == 'chapter1':
                add_platform_data(platform_data)



        # add_link(link_1)
        # add_title(txt_source['1-title'], 'title1')
        # add_text(txt_source['1-text'].format(site_name, ctime(snapshot_data['tsStart'] / 1000), str(platform_data['Number of devices'])))
        add_space()

        # Adding platform summary data

        add_space()
        # add_link(link_network_overview)
        # add_title('1.1 Network Overview', 'title2')

        # add_space()
        # # Adding management protocols data
        # add_link(link_management_protocols)
        # add_title('1.3 Management protocols summary', 'title2')
        # add_text('Network management protocols are responsible for collecting and organizing information about managed devices on IP networks and changing device behavior. Due to their nature, they form a critical part for network infrastructure management and therefore is essential to understand how they are implemented and what management systems are used to operate the network.')
        # add_space()
        # add_text(
        #     'Following tables represents all detected management servers for supported management protocols.')
        # add_space()
        # add_mgmt_data(mgmt_data)

        try:
            print('  -- Creating PDF: ', output_file_path)
            pdf.output(output_file_path)
        except PermissionError as err:
            print('  -- Unable to create PDF due to: {}'.format(err))
        except FileNotFoundError as err:
            print('  -- Directory not found: {}'.format(err))
        except:
            print('Unable to create PDF file: {}, Unexpected error.'.format(
                output_file_path))
            raise
