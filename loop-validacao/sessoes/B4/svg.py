def scatter_panel(pts, x0, y0, w, h, xr, yr, titulo, xl, yl, cor, rotulos=(), vline=None, hline=0):
    """pts: list (x,y,label)"""
    sx=lambda x: x0+ (x-xr[0])/(xr[1]-xr[0])*w
    sy=lambda y: y0+h-(y-yr[0])/(yr[1]-yr[0])*h
    s=[f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="#999"/>',
       f'<text x="{x0+w/2}" y="{y0-10}" font-size="13" text-anchor="middle" font-weight="bold">{titulo}</text>',
       f'<text x="{x0+w/2}" y="{y0+h+34}" font-size="11" text-anchor="middle">{xl}</text>',
       f'<text x="{x0-40}" y="{y0+h/2}" font-size="11" text-anchor="middle" transform="rotate(-90 {x0-40} {y0+h/2})">{yl}</text>']
    import numpy as np
    for t in np.linspace(xr[0],xr[1],5):
        s.append(f'<text x="{sx(t)}" y="{y0+h+15}" font-size="10" text-anchor="middle">{t:.0f}</text>')
    for t in np.linspace(yr[0],yr[1],5):
        s.append(f'<text x="{x0-5}" y="{sy(t)+3}" font-size="10" text-anchor="end">{t:.0f}</text>')
    if hline is not None: s.append(f'<line x1="{x0}" x2="{x0+w}" y1="{sy(hline)}" y2="{sy(hline)}" stroke="#bbb"/>')
    if vline is not None: s.append(f'<line x1="{sx(vline)}" x2="{sx(vline)}" y1="{y0}" y2="{y0+h}" stroke="#888" stroke-dasharray="4 3"/>')
    for x,y,lab in pts:
        s.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4" fill="{cor}" fill-opacity="0.8"/>')
        if lab in rotulos: s.append(f'<text x="{sx(x)+5:.1f}" y="{sy(y)-4:.1f}" font-size="9">{lab}</text>')
    return '\n'.join(s)
def svg(conteudo, W, H, rodape=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif">'
            f'<rect width="100%" height="100%" fill="white"/>{conteudo}'
            f'<text x="10" y="{H-8}" font-size="9" fill="#555">{rodape}</text></svg>')
