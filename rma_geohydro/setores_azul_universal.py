# -*- coding: utf-8 -*-
"""RMA GeoHydro: setores preliminares entre transversais, SEM limites fixos de desenho.
Derivado da rotina de pre-visualizacao testada no console QGIS; resultados NÃO são bacias validadas.
Entrada aceita DXF ASCII com entidades LWPOLYLINE. Não altera os arquivos CAD.
"""
import os
import math
import unicodedata
from collections import Counter
from qgis.core import (QgsProject, QgsVectorLayer, QgsGeometry, QgsFeature, QgsField,
                       QgsPointXY, QgsCoordinateReferenceSystem, QgsWkbTypes,
                       QgsFillSymbol, QgsLineSymbol, QgsUnitTypes)
from qgis.PyQt.QtCore import QVariant
from .i18n import FileDialog as QFileDialog, InputDialog as QInputDialog, MessageBox as QMessageBox, tr, language
LIMIAR_GAP_CANAL_M = 20.0
LIMIAR_AFASTAMENTO_M = 10.0

def ler_lwpolylines_ascii_dxf(caminho):
    """Lê somente entidades LWPOLYLINE do ENTITIES do DXF ASCII (sem ezdxf)."""
    with open(caminho, 'r', encoding='latin-1', errors='replace') as f:
        linhas = f.read().splitlines()
    if len(linhas) % 2:
        linhas = linhas[:-1]
    pares = [(linhas[i].strip(), linhas[i + 1].strip())
             for i in range(0, len(linhas), 2)]
    entidades = []
    secao = None
    i = 0
    while i < len(pares):
        cod, val = pares[i]
        if cod == '0' and val == 'SECTION':
            if i + 1 < len(pares) and pares[i + 1][0] == '2':
                secao = pares[i + 1][1]
        elif cod == '0' and val == 'ENDSEC':
            secao = None
        elif secao == 'ENTITIES' and cod == '0' and val == 'LWPOLYLINE':
            j = i + 1
            dados = []
            while j < len(pares) and pares[j][0] != '0':
                dados.append(pares[j])
                j += 1
            layer, handle, pontos = '', '', []
            for code, value in dados:
                if code == '8':
                    layer = value
                elif code == '5':
                    handle = value
                elif code == '10':
                    pontos.append({'x': float(value), 'y': None, 'w0': 0.0, 'w1': 0.0})
                elif code == '20' and pontos:
                    pontos[-1]['y'] = float(value)
                elif code == '40' and pontos:
                    pontos[-1]['w0'] = float(value)
                elif code == '41' and pontos:
                    pontos[-1]['w1'] = float(value)
            pontos = [p for p in pontos if p['y'] is not None]
            if len(pontos) >= 2:
                entidades.append({'layer': layer.upper().strip(),
                                  'handle': handle, 'pts': pontos})
            i = j
            continue
        i += 1
    return entidades


def criar_memoria(nome, tipo, crs, campos):
    layer = QgsVectorLayer(tipo, nome, 'memory')
    if not layer.isValid():
        raise RuntimeError('Não foi possível criar a camada ' + nome)
    layer.setCrs(crs)
    layer.dataProvider().addAttributes(campos)
    layer.updateFields()
    return layer


def incluir(layer, geom, valores):
    feicao = QgsFeature(layer.fields())
    feicao.setGeometry(geom)
    feicao.setAttributes(valores)
    return layer.dataProvider().addFeatures([feicao])[0]


def qpt(p):
    return QgsPointXY(float(p[0]), float(p[1]))


def xy_pts(entidade):
    return [(p['x'], p['y']) for p in entidade['pts']]


def poligono_seta(ent):
    """Reconstrói largura CAD: corpo 3.07 m e cabeça triangular 9.27 m."""
    pts = xy_pts(ent)
    if len(pts) != 3:
        return None
    a, b, tip = pts
    v1 = (b[0] - a[0], b[1] - a[1])
    v2 = (tip[0] - b[0], tip[1] - b[1])
    l1, l2 = math.hypot(*v1), math.hypot(*v2)
    if l1 < 0.0001 or l2 < 0.0001:
        return None
    n1 = (-v1[1] / l1, v1[0] / l1)
    n2 = (-v2[1] / l2, v2[0] / l2)
    largura_corpo = ent['pts'][0]['w0'] or 1.0
    largura_cabeca = ent['pts'][1]['w0'] or 2.0
    ac = (a[0] + n1[0] * largura_corpo / 2, a[1] + n1[1] * largura_corpo / 2)
    bc = (b[0] + n2[0] * largura_cabeca / 2, b[1] + n2[1] * largura_cabeca / 2)
    bd = (b[0] - n2[0] * largura_cabeca / 2, b[1] - n2[1] * largura_cabeca / 2)
    ad = (a[0] - n1[0] * largura_corpo / 2, a[1] - n1[1] * largura_corpo / 2)
    ring = [ac, bc, tip, bd, ad, ac]
    geom = QgsGeometry.fromPolygonXY([[qpt(p) for p in ring]])
    return geom if not geom.isEmpty() else None


def linha2(a, b):
    return QgsGeometry.fromPolylineXY([qpt(a), qpt(b)])


def criar_canal_continuo(canais):
    """Concatena trechos ao longo do eixo dominante; liga lacunas apenas para previsualização."""
    partes = []
    todos = [p for e in canais for p in xy_pts(e)]
    eixo = 1 if (max(p[1] for p in todos)-min(p[1] for p in todos)) >= (max(p[0] for p in todos)-min(p[0] for p in todos)) else 0
    for e in canais:
        pts = xy_pts(e)
        if pts[0][eixo] < pts[-1][eixo]:
            pts.reverse()
        partes.append(pts)
    partes.sort(key=lambda p: p[0][eixo], reverse=True)
    path, intervalos_gap = [], []
    dist_acum = 0.0
    for parte in partes:
        if path:
            dx = parte[0][0] - path[-1][0]
            dy = parte[0][1] - path[-1][1]
            gap = math.hypot(dx, dy)
            if gap > 0.001:
                intervalos_gap.append((dist_acum, dist_acum + gap, gap))
                dist_acum += gap
                path.append(parte[0])
        else:
            path.append(parte[0])
        for p in parte[1:]:
            dist_acum += math.hypot(p[0] - path[-1][0], p[1] - path[-1][1])
            path.append(p)
    return path, intervalos_gap


def trecho_canal_entre(geom, coords, pos1, pos2):
    """Retorna pontos do canal no intervalo [pos1,pos2], incluindo vértices."""
    out = [(geom.interpolate(pos1).asPoint().x(),
            geom.interpolate(pos1).asPoint().y())]
    acumulado = 0.0
    for a, b in zip(coords[:-1], coords[1:]):
        acumulado += math.hypot(b[0] - a[0], b[1] - a[1])
        if pos1 + 1e-7 < acumulado < pos2 - 1e-7:
            out.append(b)
    p = geom.interpolate(pos2).asPoint()
    out.append((p.x(), p.y()))
    return out



def _normalizar(texto):
    s = unicodedata.normalize('NFKD', str(texto).upper())
    return ''.join(c for c in s if not unicodedata.combining(c))


def _selecionar(titulo, nomes, palavras, obrigatorio=True):
    """Sugerir camada CAD real (inclusive para opcionais); nunca escolher Nenhuma por padrão."""
    candidatos = sorted(nomes, key=lambda n: (-sum(p in _normalizar(n) for p in palavras), n))
    if not candidatos:
        if obrigatorio:
            raise ValueError('Nenhuma camada disponível para ' + titulo)
        return None
    # Mostra a correspondência mais forte em primeiro lugar e deixa (Nenhuma) por último.
    opcoes = candidatos + ([] if obrigatorio else ['(Nenhuma)'])
    escolha, ok = QInputDialog.getItem(None, 'RMA GeoHydro - ' + titulo,
        'Selecione a camada CAD correspondente (confira a sugestão):', opcoes, 0, False)
    if not ok:
        raise RuntimeError('Operação cancelada pelo usuário.')
    return None if escolha == '(Nenhuma)' else escolha


def executar(caminho=None, epsg=None, diretorio=None, formato='SHP', orientacao='Ambas'):
    """Gerar setores TEMPORÁRIOS e exportar quando solicitado; nunca modifica o CAD."""
    if not caminho or not os.path.isfile(caminho):
        caminho, _ = QFileDialog.getOpenFileName(None, 'Selecionar arquivo DXF', '', 'DXF (*.dxf)')
    if not caminho:
        return None
    projeto = QgsProject.instance()
    if not epsg:
        epsg, ok = QInputDialog.getText(None, 'SRC de origem', 'EPSG do DXF (por exemplo EPSG:32629):', text=projeto.crs().authid())
        if not ok: return None
    crs = QgsCoordinateReferenceSystem(epsg)
    if not crs.isValid() or crs.isGeographic() or crs.mapUnits() != QgsUnitTypes.DistanceUnit.DistanceMeters:
        raise ValueError('O SRC informado precisa ser projetado e em metros.')
    entidades = ler_lwpolylines_ascii_dxf(caminho)
    if not entidades:
        raise RuntimeError('Nenhuma LWPOLYLINE encontrada. Verifique se o DXF está em formato ASCII com polilinhas compatíveis.')
    nomes = sorted(set(e['layer'] for e in entidades))
    nome_canal = _selecionar('Canal de referência', nomes, ['CANAL', 'CHANNEL', 'DREN'])
    nome_divisor = _selecionar('Divisores', nomes, ['DIVISOR', 'CRISTA', 'RIDGE'])
    nome_descida = _selecionar('Descidas', [n for n in nomes if n != nome_divisor], ['DESCIDA', 'DOWNCHUTE'], False)
    nome_seta = _selecionar('Setas de fluxo (opcional)', [n for n in nomes if n not in (nome_canal, nome_divisor, nome_descida)], ['SENTIDO', 'FLUXO', 'ARROW'], False)
    if nome_descida == nome_canal:
        raise ValueError('A camada das descidas não pode ser a mesma do canal.')
    if nome_seta in (nome_canal, nome_divisor, nome_descida):
        raise ValueError('A camada de setas deve ser distinta das camadas de drenagem.')
    if nome_canal == nome_divisor or nome_canal == nome_descida:
        raise ValueError('As camadas de canal e de transversais devem ser diferentes.')
    canais = [e for e in entidades if e['layer'] == nome_canal]
    barras = [e for e in entidades if e['layer'] in set([nome_divisor, nome_descida])]
    setas = [e for e in entidades if e['layer'] == nome_seta] if nome_seta else []
    n_divisores = sum(1 for e in entidades if e['layer'] == nome_divisor)
    n_descidas = sum(1 for e in entidades if nome_descida and e['layer'] == nome_descida)
    aviso = ('Orientação informada: {}\nCanal de referência: {} ({} trechos)\n'
             'Divisores: {} ({} linhas)\nDescidas: {} ({} linhas)\n'
             'Total de transversais: {}').format(orientacao, nome_canal, len(canais),
             nome_divisor, n_divisores, nome_descida or '(não selecionada)',
             n_descidas, len(barras))
    print('RMA GeoHydro - conferência\n' + aviso)
    if QMessageBox.question(None, 'RMA GeoHydro - confirmar elementos',
            aviso + '\n\nOs setores serão construídos entre transversais consecutivas em relação ao canal selecionado. '
            'Isso não classifica hidraulicamente a orientação. Continuar?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes) != QMessageBox.StandardButton.Yes:
        return None
    if len(barras) < 2 or not canais:
        raise ValueError('São necessários um canal e no mínimo duas linhas transversais.')
    # Output names follow the selected UI language. Geometry and attribute schema stay unchanged.
    output_names = (
        {
            'arrows': 'RMA_01_flow_arrows',
            'divides': 'RMA_02_divides_downchutes',
            'channels': 'RMA_03_channels',
            'areas': 'RMA_04_PRELIMINARY_DRAINAGE_AREAS_REVIEW',
            'export_areas': 'RMA_preliminary_drainage_areas',
            'export_channels': 'RMA_channels',
            'export_divides': 'RMA_divides_downchutes',
            'export_arrows': 'RMA_flow_arrows',
            'diagnostic': 'RMA_drainage_areas_diagnostic.txt',
        } if language() == 'en_US' else {
            'arrows': 'RMA_01_setas_fluxo',
            'divides': 'RMA_02_divisores_descidas',
            'channels': 'RMA_03_canais',
            'areas': 'RMA_04_AREAS_DRENAGEM_PRELIMINARES_REVISAR',
            'export_areas': 'RMA_areas_drenagem_preliminares',
            'export_channels': 'RMA_canais',
            'export_divides': 'RMA_divisores_descidas',
            'export_arrows': 'RMA_setas',
            'diagnostic': 'RMA_diagnostico_areas_drenagem.txt',
        }
    )
    # Camadas temporárias independentes; setores são apenas aproximações geométricas.
    layer_setas = criar_memoria(output_names['arrows'], 'Polygon', crs, [QgsField('cad_id', QVariant.String)])
    for ent in setas:
        g = poligono_seta(ent)
        if g and g.isGeosValid(): incluir(layer_setas, g, [ent['handle']])
    layer_setas.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'38,112,203,255', 'outline_style':'no'}))
    layer_barras = criar_memoria(output_names['divides'], 'LineString', crs, [QgsField('cad_id', QVariant.String), QgsField('tipo', QVariant.String)])
    for ent in barras:
        pts=xy_pts(ent)
        incluir(layer_barras, linha2(pts[0], pts[-1]), [ent['handle'], ent['layer']])
    layer_barras.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':'32,82,197,255', 'line_width':'0.65'}))
    layer_canais = criar_memoria(output_names['channels'], 'LineString', crs, [QgsField('cad_id', QVariant.String)])
    for ent in canais:
        incluir(layer_canais, QgsGeometry.fromPolylineXY([qpt(p) for p in xy_pts(ent)]), [ent['handle']])
    layer_canais.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':'0,170,215,255', 'line_width':'0.9'}))
    coords_canal, gaps = criar_canal_continuo(canais)
    geom_canal = QgsGeometry.fromPolylineXY([qpt(p) for p in coords_canal])
    transectos = []
    for ent in barras:
        pts = xy_pts(ent)
        a,b=pts[0],pts[-1]
        da=geom_canal.distance(QgsGeometry.fromPointXY(qpt(a)))
        db=geom_canal.distance(QgsGeometry.fromPointXY(qpt(b)))
        interior, exterior, dist=(a,b,da) if da<=db else (b,a,db)
        pos=geom_canal.lineLocatePoint(QgsGeometry.fromPointXY(qpt(interior)))
        if pos>=0: transectos.append((pos,interior,exterior,dist,ent))
    transectos.sort(key=lambda t:t[0])
    campos=[QgsField('setor',QVariant.Int), QgsField('inicio',QVariant.String),
            QgsField('fim',QVariant.String), QgsField('status',QVariant.String),
            QgsField('afast_m',QVariant.Double), QgsField('gap_m',QVariant.Double),
            QgsField('area_m2',QVariant.Double), QgsField('alerta_geom',QVariant.Int)]
    layer_areas = criar_memoria(output_names['areas'],'Polygon',crs,campos)
    rejeitados=[]
    for i,(t1,t2) in enumerate(zip(transectos[:-1],transectos[1:]),1):
        s1,_,fora1,d1,e1=t1
        s2,_,fora2,d2,e2=t2
        if s2-s1 <= 0.000001:
            rejeitados.append('Setor {}: transversais na mesma posição do canal'.format(i));continue
        trecho=trecho_canal_entre(geom_canal, coords_canal,s1,s2)
        anel=[fora1,fora2]+list(reversed(trecho))+[fora1]
        g=QgsGeometry.fromPolygonXY([[qpt(p) for p in anel]])
        maior_gap=max((comp for x,y,comp in gaps if x<s2 and y>s1),default=0.0)
        maior_erro=max(d1,d2)
        if not g.isGeosValid() or g.area()<=0:
            rejeitados.append('Setor {}: polígono inválido (CAD/interseções)'.format(i));continue
        motivos=[]
        if maior_gap>LIMIAR_GAP_CANAL_M: motivos.append('GAP_CANAL')
        if maior_erro>LIMIAR_AFASTAMENTO_M: motivos.append('AFASTAMENTO')
        situacao='+'.join(motivos) if motivos else 'PRELIMINAR'
        incluir(layer_areas,g,[i,e1['handle'],e2['handle'],situacao,maior_erro,maior_gap,g.area(), 0 if situacao == 'PRELIMINAR' else 1])
    layer_areas.renderer().setSymbol(QgsFillSymbol.createSimple({
        'color':'255,184,35,60','outline_color':'255,116,0,255','outline_width':'0.45'}))
    for lyr in (layer_areas,layer_canais,layer_barras,layer_setas):
        lyr.updateExtents()
        if lyr.featureCount(): projeto.addMapLayer(lyr)
    resumo = ('DXF: {}\nCanal: {} ({} trechos)\nTransversais: {}\nSetas: {}\n'
        'Orientação escolhida: {}\nDivisores: {} | Descidas: {}\nÁreas de drenagem preliminares: {}\nRejeitados: {}\nLacunas de canal (m): {}\n{}\n'
        'ATENÇÃO: limites aproximados; NÃO usar para cálculos hidrológicos sem validação.').format(
        os.path.basename(caminho),nome_canal,len(canais),len(transectos),len(setas),
        orientacao,n_divisores,n_descidas,layer_areas.featureCount(),len(rejeitados),[round(x[2],2) for x in gaps], '\n'.join(rejeitados))
    print('RMA GeoHydro\n'+resumo)
    if diretorio and os.path.isdir(diretorio) and layer_areas.featureCount():
        resp=QMessageBox.question(None,'Exportação de áreas de drenagem',
            'Salvar as áreas de drenagem e camadas auxiliares como {} na pasta escolhida?'.format(formato),
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if resp==QMessageBox.StandardButton.Yes:
            from .plugin import write_layer
            for lyr,nome in ((layer_areas,output_names['export_areas']),
                             (layer_canais,output_names['export_channels']),(layer_barras,output_names['export_divides']),
                             (layer_setas,output_names['export_arrows'])):
                if lyr.featureCount(): write_layer(lyr,diretorio,nome,formato,projeto)
            with open(os.path.join(diretorio,output_names['diagnostic']),'w',encoding='utf-8') as f:
                f.write(resumo)
    QMessageBox.information(None,'RMA GeoHydro - áreas de drenagem preliminares',resumo)
    return layer_areas.featureCount()
