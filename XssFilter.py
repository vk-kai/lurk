import bleach
from bleach.sanitizer import ALLOWED_TAGS
from bleach.css_sanitizer import CSSSanitizer
tags = list(ALLOWED_TAGS) + ['h',
                       'h1',
                       'h2',
                       'h3',
                       'h4',
                       'pre',
                       'br',
                       'hr',
                       'p',
                       'table',
                       'tbody',
                       'span',
                       'a',
                       'tr',
                       'td',
                       'img',
                       'figure',
                       'sup',
                       'sub',
                       'label',
                       'pr',
                       'mark'
                       'span',
                       'input',
                       'u',
                       'ul',
                       'li',
                       'em',
                       'mark',
                       'thead',
                       'th',
                       'font',
                       'strike'
                       'strong']
attrs = {
    '*': ['style', 'class', 'face', 'color', 'contenteditable'],
    'input': ['type', 'checked'],
    'img': ['src', 'data-original'],
    'a': ['href'],
    'br': ['data-cke-filler'],
    'pre': ['data-language'],
    'label':['class','contenteditable'],
    'ul': ['class'],

}
styles = [
    'color',
    'font-weight',
    'background-color',
    'Courier',
    'font-size',
    'text-align',
    'font-family',
    'width',
    'height',
]
css_sanitizer = CSSSanitizer(allowed_css_properties=styles)
def Xss_filter(content):

    content = bleach.clean(
        content,
        tags=tags,
        attributes=attrs,
        css_sanitizer=css_sanitizer,
    )
    return content
if __name__ == '__main__':
    print(Xss_filter('<script>alert(1)</script>'))
    print(Xss_filter('<p>111</p>'))