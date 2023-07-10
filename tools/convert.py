import markdown
import codecs

input_file = codecs.open("helper.md", mode="r", encoding="utf-8")
text = input_file.read()
html = markdown.markdown(text)

output_file = codecs.open("helper.html", mode="w", encoding="utf-8", errors="xmlcharrefreplace")
output_file.write(html)
