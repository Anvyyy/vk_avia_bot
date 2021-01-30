import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageColor


class AirplaneTickets:

    def __init__(self, full_name, from_where, where_to, date, template=None, font_path=None):
        self.full_name = full_name
        self.from_where = from_where
        self.where_to = where_to
        self.date = date
        self.data_ticket = {235: self.full_name, 165: self.from_where, 100: self.where_to}
        self.template = os.path.join('drawing', 'images', 'ticket_template.png') if template is None else template
        self.font_path = os.path.join('drawing', 'fonts', 'airborne.ttf') if font_path is None else font_path

    def make_ticket(self):
        im = Image.open(self.template)
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype(self.font_path, size=15)

        for write_ticket in self.data_ticket.items():
            y = im.size[1] - write_ticket[0] - (5 + font.size) * 2
            message = write_ticket[1]
            draw.text((55, y), message, font=font, fill=ImageColor.colormap['black'])

        y = im.size[1] - 100 - (5 + font.size) * 2
        message = self.date
        draw.text((280, y), message, font=font, fill=ImageColor.colormap['black'])

        temp_file = BytesIO()
        im.save(temp_file, 'png')
        temp_file.seek(0)

        return temp_file


# if __name__ == '__main__':
# maker = AirplaneTickets(full_name='Попов Дмитрий Срегеевич',
#                         from_where='Москва',
#                         where_to='Рим',
#                         date='04.05.2020',
#                         font_path='drawing/fonts/roadradio.ttf')
# maker.make_ticket()
