"""Baby-lungs mascot: one flat-colour SVG per result level (works in the web page and, via svglib, in the PDF).
Web animation uses the classes lg-L / lg-R (breathing), lg-blink, lg-float, lg-spark, lg-drop (see style.css)."""
PAL = {  # body, shade, cheek, mouth path, brow tilt
    "Lower":        dict(b="#FF9AA9", s="#F2778C", c="#FF6F91", bg="#E6F7EE"),
    "Intermediate": dict(b="#FFC27A", s="#F29D4B", c="#F58A5B", bg="#FFF3DC"),
    "Higher":       dict(b="#F58C95", s="#D9606F", c="#E5484D", bg="#FFE6E3"),
}
MOUTH = {"Lower": '<path d="M90 128 Q100 140 110 128" fill="none" stroke="#7A2E3C" stroke-width="3.5" stroke-linecap="round"/>',
         "Intermediate": '<path d="M91 132 Q100 130 109 132" fill="none" stroke="#7A2E3C" stroke-width="3.5" stroke-linecap="round"/>',
         "Higher": '<path d="M90 135 Q100 125 110 135" fill="none" stroke="#7A2E3C" stroke-width="3.5" stroke-linecap="round"/>'}
EXTRA = {
 "Lower": '<g class="lg-spark"><path d="M30 40 l3 8 8 3 -8 3 -3 8 -3 -8 -8 -3 8 -3z" fill="#FFD166"/><path d="M168 52 l2 6 6 2 -6 2 -2 6 -2 -6 -6 -2 6 -2z" fill="#FFD166"/></g>',
 "Intermediate": '<g class="lg-drop"><path d="M150 62 q8 12 0 18 q-8 -6 0 -18z" fill="#7CC4F2"/></g>',
 "Higher": '<g class="lg-drop"><path d="M152 60 q9 14 0 21 q-9 -7 0 -21z" fill="#7CC4F2"/></g><path d="M42 72 l12 6 M158 108 l12 -4" stroke="#D9606F" stroke-width="3" stroke-linecap="round"/>'}


def eyes(level):
    if level == "Higher":  # wide, worried
        return ('<g class="lg-blink"><ellipse cx="85" cy="108" rx="7" ry="8.5" fill="#fff"/><ellipse cx="115" cy="108" rx="7" ry="8.5" fill="#fff"/>'
                '<circle cx="86" cy="110" r="4.2" fill="#3B2A2F"/><circle cx="114" cy="110" r="4.2" fill="#3B2A2F"/></g>'
                '<path d="M76 94 L92 98 M124 94 L108 98" stroke="#7A2E3C" stroke-width="3" stroke-linecap="round"/>')
    if level == "Intermediate":
        return ('<g class="lg-blink"><ellipse cx="85" cy="108" rx="6.5" ry="8" fill="#fff"/><ellipse cx="115" cy="108" rx="6.5" ry="8" fill="#fff"/>'
                '<circle cx="86" cy="109" r="4" fill="#3B2A2F"/><circle cx="114" cy="109" r="4" fill="#3B2A2F"/></g>'
                '<path d="M77 97 L92 95 M123 97 L108 95" stroke="#7A2E3C" stroke-width="3" stroke-linecap="round"/>')
    return ('<g class="lg-blink"><ellipse cx="85" cy="108" rx="6.5" ry="8" fill="#fff"/><ellipse cx="115" cy="108" rx="6.5" ry="8" fill="#fff"/>'
            '<circle cx="85" cy="109" r="4.3" fill="#3B2A2F"/><circle cx="115" cy="109" r="4.3" fill="#3B2A2F"/>'
            '<circle cx="86.5" cy="107" r="1.4" fill="#fff"/><circle cx="116.5" cy="107" r="1.4" fill="#fff"/></g>')


def svg(level="Lower", size=200, bg=True):
    p = PAL.get(level, PAL["Lower"]); lv = level if level in PAL else "Lower"
    bgc = f'<circle cx="100" cy="100" r="96" fill="{p["bg"]}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="{size}" height="{size}" role="img" aria-label="{lv}" class="lungs lungs-{lv}">'
            f'{bgc}<g class="lg-float">'
            f'<rect x="94" y="30" width="12" height="46" rx="6" fill="{p["s"]}"/>'
            f'<path d="M100 70 Q84 74 76 88 M100 70 Q116 74 124 88" fill="none" stroke="{p["s"]}" stroke-width="9" stroke-linecap="round"/>'
            f'<g class="lg-L"><path d="M98 96 C98 80 84 70 68 76 C46 84 36 120 40 150 C42 166 56 172 72 168 C88 164 98 152 98 136 Z" fill="{p["b"]}"/>'
            f'<path d="M52 110 q-4 22 2 40" fill="none" stroke="{p["s"]}" stroke-width="4" stroke-linecap="round" opacity=".7"/></g>'
            f'<g class="lg-R"><path d="M102 96 C102 80 116 70 132 76 C154 84 164 120 160 150 C158 166 144 172 128 168 C112 164 102 152 102 136 Z" fill="{p["b"]}"/>'
            f'<path d="M148 110 q4 22 -2 40" fill="none" stroke="{p["s"]}" stroke-width="4" stroke-linecap="round" opacity=".7"/></g>'
            f'<ellipse cx="72" cy="128" rx="9" ry="6" fill="{p["c"]}" opacity=".45"/><ellipse cx="128" cy="128" rx="9" ry="6" fill="{p["c"]}" opacity=".45"/>'
            f'{eyes(lv)}{MOUTH[lv]}</g>{EXTRA[lv]}</svg>')
