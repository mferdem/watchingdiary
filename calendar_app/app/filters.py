from flask import Flask

def color_for_name(name):
    colors = [
        'crimson', 'darkblue', 'darkgreen', 'indigo', 'orangered',
        'teal', 'hotpink', 'olive', 'tomato', 'goldenrod',
        'slateblue', 'darkorange', 'deeppink', 'mediumvioletred', 'mediumseagreen'
    ]
    index = sum(ord(c) for c in name.lower()) % len(colors)
    return colors[index]

