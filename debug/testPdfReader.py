from pdfrw import PdfReader
a = PdfReader('test.pdf').Info

if not a.Subject is None or not a.Author is None or not a.Keywords is None:
    print(a.Title[1:len(a.Title)-1])
