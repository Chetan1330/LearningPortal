from pikepdf import Pdf, PdfImage

filename = '70-461.pdf'
example = Pdf.open(filename)

for i, page in enumerate(example.pages):
    for j, (name, raw_image) in enumerate(page.images.items()):
        image = PdfImage(raw_image)
        out = image.extract_to(fileprefix=f"{filename}-page{(i+1):03}-img{j:03}")