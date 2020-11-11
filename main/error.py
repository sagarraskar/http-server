from jinja2 import Template
def getErrorPage(status_code, status_phrase, message):
    t = Template("""<!DOCTYPE html>
<html>
<head>
    <title>{{status_code}} {{status_phrase}}</title>
</head>
<body>
    <h1>{{status_phrase}}</h1>
    <p1>{{message}}</p>
</body>
</html>""")

    return t.render(status_code=status_code, status_phrase=status_phrase, message=message)

# print(getErrorPage(404, "Not Found", "Page Not Found"))