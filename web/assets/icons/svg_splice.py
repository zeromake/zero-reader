from lxml import etree

if __name__ == "__main__":
    with open('icon.svg', 'r') as svg:
        root = etree.parse(svg).getroot()
        for child in root.iterchildren():
            if child.tag == 'symbol':
                svg_id = child.get("id")
                del child.attrib['id']
                svg_id = svg_id[5:]
                print(svg_id)
                child.tag = 'svg'

                etree.ElementTree(child).write(
                    'icons/' + svg_id + ".svg",
                    pretty_print=True,
                    encoding='utf-8'
                )