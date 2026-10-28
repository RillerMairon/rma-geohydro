# -*- coding: utf-8 -*-
"""
DELIMITAÇÃO PRELIMINAR DE SETORES DE DRENAGEM - QGIS 3.x
Módulo de delimitação assistida integrado ao RMA GeoHydro.
O arquivo DXF é escolhido pelo usuário; nenhuma camada original é editada.
Os resultados são TEMPORÁRIOS e exigem conferência hidráulica/topográfica.
"""
import math
import os
import unicodedata
from collections import Counter

from osgeo import ogr
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsGeometry, QgsFeature, QgsField,
    QgsPointXY, QgsCoordinateReferenceSystem, QgsUnitTypes,
    QgsFillSymbol, QgsLineSymbol
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QFileDialog, QInputDialog, QMessageBox

# Alerta para lacunas entre trechos e afastamento das seções (metros).
MAX_GAP_M = 20.0
MAX_AFASTAMENTO_M = 10.0


def avisar(texto, titulo="Delimitação de drenagem"):
    QMessageBox.information(None, titulo, texto)


def cancelar():
    raise RuntimeError("Operação cancelada. Nenhum arquivo original foi modificado.")


def sim_nao(pergunta):
    resposta = QMessageBox.question(
        None, "Verificação do DXF", pergunta,
        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
    )
    return resposta == QMessageBox.Yes


def escolher(titulo, pergunta, opcoes, obrigatorio=True):
    if not opcoes:
        if obrigatorio:
            raise RuntimeError("Não há opções para " + titulo)
        return None
    selecionado, ok = QInputDialog.getItem(
        None, titulo, pergunta, list(opcoes), 0, False
    )
    if not ok:
        cancelar()
    return selecionado


def nome_normalizado(txt):
    txt = unicodedata.normalize("NFKD", str(txt))
    return ''.join(ch for ch in txt if not unicodedata.combining(ch)).upper()


def sugerir_layer(camadas, palavras):
    # Sugestão apenas; o usuário confirma o nome da camada na janela.
    ranqueadas = sorted(
        camadas,
        key=lambda n: -sum(p in nome_normalizado(n) for p in palavras)
    )
    return ranqueadas


def linhas_geometria(geom):
    """Converte linhas do OGR em coordenadas XY sem exigir ezdxf."""
    if geom is None or geom.IsEmpty():
        return []
    nome = geom.GetGeometryName().upper()
    if nome in ("LINESTRING", "LINEARRING", "CIRCULARSTRING"):
        try:
            pts = [(float(p[0]), float(p[1])) for p in geom.GetPoints()]
        except Exception:
            return []
        # Remove vértices consecutivos repetidos.
        limpos = []
        for p in pts:
            if not limpos or math.hypot(p[0]-limpos[-1][0], p[1]-limpos[-1][1]) > 1e-9:
                limpos.append(p)
        return [limpos] if len(limpos) >= 2 else []
    if nome in ("POLYGON", "CURVEPOLYGON"):
        return linhas_geometria(geom.GetGeometryRef(0))
    if geom.GetGeometryCount():
        resultado = []
        for i in range(geom.GetGeometryCount()):
            resultado.extend(linhas_geometria(geom.GetGeometryRef(i)))
        return resultado
    return []


def ler_dxf(caminho):
    ds = ogr.Open(caminho, 0)
    if ds is None:
        raise RuntimeError("Não consegui ler esse DXF com o GDAL/OGR do QGIS.")
    itens = []
    for k in range(ds.GetLayerCount()):
        camada = ds.GetLayerByIndex(k)
        camada.ResetReading()
        for f in camada:
            cad_layer = f.GetField("Layer") if f.GetFieldIndex("Layer") >= 0 else camada.GetName()
            ident = (str(f.GetField("EntityHandle"))
                     if f.GetFieldIndex("EntityHandle") >= 0 and f.GetField("EntityHandle")
                     else str(f.GetFID()))
            for n, pts in enumerate(linhas_geometria(f.GetGeometryRef())):
                itens.append({"layer": str(cad_layer or "SEM_CAMADA"),
                              "id": ident + ":" + str(n), "pts": pts})
    ds = None
    if not itens:
        raise RuntimeError("Nenhuma linha/polilinha legível foi encontrada no DXF.")
    return itens


def ponto(xy):
    return QgsPointXY(float(xy[0]), float(xy[1]))


def distancia(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])


def geom_linha(pts):
    return QgsGeometry.fromPolylineXY([ponto(p) for p in pts])


def geom_ponto(xy):
    return QgsGeometry.fromPointXY(ponto(xy))


def montar_eixo(entidades):
    """Ordena trechos por proximidade das extremidades, sem assumir norte/sul."""
    partes = [e["pts"][:] for e in entidades if len(e["pts"]) >= 2]
    if not partes:
        raise RuntimeError("Camada longitudinal sem linhas válidas.")
    def comp(pts):
        return sum(distancia(a,b) for a,b in zip(pts,pts[1:]))
    inicio = max(range(len(partes)), key=lambda i: comp(partes[i]))
    cadeia = [partes.pop(inicio)]
    while partes:
        opcoes = []
        for i, p in enumerate(partes):
            opcoes.extend([
                (distancia(cadeia[-1][-1], p[0]), i, "fim", False),
                (distancia(cadeia[-1][-1], p[-1]), i, "fim", True),
                (distancia(cadeia[0][0], p[-1]), i, "inicio", False),
                (distancia(cadeia[0][0], p[0]), i, "inicio", True),
            ])
        _, i, lado, inverter = min(opcoes, key=lambda x: x[0])
        p = partes.pop(i)
        if inverter:
            p.reverse()
        if lado == "fim":
            cadeia.append(p)
        else:
            cadeia.insert(0, p)

    caminho = list(cadeia[0])
    lacunas = []
    pos = sum(distancia(a,b) for a,b in zip(caminho,caminho[1:]))
    for parte in cadeia[1:]:
        gap = distancia(caminho[-1], parte[0])
        if gap > 1e-6:
            lacunas.append((pos, pos+gap, gap))
            caminho.append(parte[0])
            pos += gap
        for p in parte[1:]:
            pos += distancia(caminho[-1], p)
            caminho.append(p)
    return caminho, lacunas


def trecho_linha(geometria, coordenadas, pos_a, pos_b):
    """Segmento percorrido de A para B, mesmo com eixo invertido."""
    reverso = pos_a > pos_b
    a, b = sorted((pos_a, pos_b))
    if abs(b-a) < 1e-7:
        return []
    pa = geometria.interpolate(a).asPoint()
    saida = [(pa.x(), pa.y())]
    acum = 0.0
    for p, q in zip(coordenadas, coordenadas[1:]):
        acum += distancia(p, q)
        if a+1e-7 < acum < b-1e-7:
            saida.append(q)
    pb = geometria.interpolate(b).asPoint()
    saida.append((pb.x(), pb.y()))
    return saida[::-1] if reverso else saida


def camada_memoria(nome, tipo, crs, campos):
    camada = QgsVectorLayer(tipo, nome, "memory")
    if not camada.isValid():
        raise RuntimeError("Erro ao criar camada temporária: " + nome)
    camada.setCrs(crs)
    camada.dataProvider().addAttributes(campos)
    camada.updateFields()
    return camada


def inserir(camada, geometria, atributos):
    ft = QgsFeature(camada.fields())
    ft.setGeometry(geometria)
    ft.setAttributes(atributos)
    return camada.dataProvider().addFeatures([ft])[0]


def poligono_seta(pts):
    """Seta visual aproximada; pode não reproduzir largura/estilo do CAD."""
    # Setas CAD que já chegam como polígono: preservar a forma original.
    if len(pts) >= 4 and distancia(pts[0], pts[-1]) < 1e-7:
        g = QgsGeometry.fromPolygonXY([[ponto(p) for p in pts]])
        return g if not g.isEmpty() and g.isGeosValid() else None
    inicio, ponta = pts[0], pts[-1]
    length = distancia(inicio, ponta)
    if length < 1e-5:
        return None
    ux, uy = ((ponta[0]-inicio[0])/length, (ponta[1]-inicio[1])/length)
    nx, ny = -uy, ux
    largura = max(.2, min(3.0, length*.08))
    cabeca = max(.6, min(7.0, length*.26))
    recuo = min(length*.43, max(length*.2, cabeca))
    base = (ponta[0]-recuo*ux, ponta[1]-recuo*uy)
    anel = [
        (inicio[0]+nx*largura/2, inicio[1]+ny*largura/2),
        (base[0]+nx*largura/2, base[1]+ny*largura/2),
        (base[0]+nx*cabeca/2, base[1]+ny*cabeca/2),
        ponta,
        (base[0]-nx*cabeca/2, base[1]-ny*cabeca/2),
        (base[0]-nx*largura/2, base[1]-ny*largura/2),
        (inicio[0]-nx*largura/2, inicio[1]-ny*largura/2),
    ]
    anel.append(anel[0])
    return QgsGeometry.fromPolygonXY([[ponto(p) for p in anel]])


def executar():
    avisar("MODO SETORES: construção preliminar entre transversais e canal.\n"
           "Os setores precisam de revisão técnica.\n"
           "Selecione o arquivo DXF de drenagem.\n"
           "O nome do arquivo e os nomes das camadas CAD podem ser diferentes dos exemplos.",
           "1/7 - Escolher DXF")
    dxf, _ = QFileDialog.getOpenFileName(
        None, "Selecione o arquivo DXF de drenagem", "", "AutoCAD DXF (*.dxf)")
    if not dxf:
        cancelar()

    itens = ler_dxf(dxf)
    todas = sorted(set(e["layer"] for e in itens), key=str.casefold)
    resumo = Counter(e["layer"] for e in itens)
    print("\nDXF:", os.path.basename(dxf))
    print("Camadas CAD (quantidade de geometrias):", dict(resumo))

    nome_canal = escolher(
        "2/7 - Eixo de referência",
        "Qual camada CAD contém a linha longitudinal do CANAL de referência?",
        sugerir_layer(todas, ["CANAL", "DREN", "PERIF", "EIXO"]))
    tem_descidas = sim_nao("O DXF contém DESCIDAS DE ÁGUA em linhas/polilinhas?")
    tem_fluxo = sim_nao("O DXF contém SETAS / INDICAÇÕES DO SENTIDO DO FLUXO?")

    nome_div = escolher(
        "3/7 - Divisores",
        "Qual camada CAD contém os DIVISORES transversais?\n"
        "Se não houver, selecione '(não possui)'.",
        ["(não possui)"] + sugerir_layer(todas, ["DIVIS", "SEPAR", "LIMITE"]),
        obrigatorio=False)
    if nome_div == "(não possui)":
        nome_div = None

    nome_desc = None
    if tem_descidas:
        nome_desc = escolher("4/7 - Descidas de água",
                            "Selecione a camada CAD das DESCIDAS:",
                            sugerir_layer(todas, ["DESC", "QUEDA", "DOWN", "DREN"]))

    nome_fluxo = None
    direcao = "não informada"
    if tem_fluxo:
        nome_fluxo = escolher("5/7 - Sentido do fluxo",
                             "Selecione a camada CAD das SETAS DE FLUXO:",
                             sugerir_layer(todas, ["SENTIDO", "FLUXO", "SETA", "FLOW"]))
        direcao = escolher("5/7 - Direção de escoamento",
                          "Em relação à TELA do QGIS, para onde aponta o escoamento?\n"
                          "(Isso é registrado para conferência; não substitui análise de relevo.)",
                          ["Para a esquerda", "Para a direita", "Ambos os lados / varia", "Não sei"])

    # Linha de limite adicional permite usar a 3ª linha, quando estiver em layer próprio.
    tem_limite = sim_nao(
        "Existe no DXF uma LINHA LONGITUDINAL específica que deve limitar\n"
        "a largura dos setores (por exemplo, a 3ª linha), em uma camada CAD?\n\n"
        "SIM: usar essa linha como limite externo.\n"
        "NÃO: usar as extremidades das divisões transversais.")
    nome_limite = None
    if tem_limite:
        nome_limite = escolher("6/7 - Limite externo",
                              "Selecione a camada CAD que contém o LIMITE correto:",
                              sugerir_layer(todas, ["LIMITE", "BORDA", "CRISTA", "OFFSET", "MARGEM"]))

    epsg_padrao = QgsProject.instance().crs().authid() or "EPSG:31983"
    epsg, ok = QInputDialog.getText(
        None, "7/7 - Sistema de coordenadas",
        "SRC real das coordenadas do DXF (exemplo EPSG:31983):",
        text=epsg_padrao)
    if not ok:
        cancelar()
    crs = QgsCoordinateReferenceSystem(epsg.strip())
    if not crs.isValid() or crs.mapUnits() != QgsUnitTypes.DistanceMeters:
        raise RuntimeError("Escolha um SRC válido com unidades em metros. Nada foi alterado.")

    def filtrar(layer):
        return [e for e in itens if e["layer"] == layer] if layer else []
    canais = filtrar(nome_canal)
    transversais = filtrar(nome_div) + filtrar(nome_desc)
    # Quando o usuario seleciona a mesma camada para duas categorias,
    # evita criar a mesma transversal duas vezes.
    transversais = list({(e["layer"], e["id"]): e
                         for e in transversais}.values())
    setas = filtrar(nome_fluxo)
    limites = filtrar(nome_limite)
    if len(transversais) < 2 or not canais:
        raise RuntimeError("São necessários um canal e ao menos duas linhas transversais.")

    canal_pts, gaps = montar_eixo(canais)
    canal_geom = geom_linha(canal_pts)
    borda_pts = None
    borda_geom = None
    if limites:
        borda_pts, gaps_borda = montar_eixo(limites)
        borda_geom = geom_linha(borda_pts)
    else:
        gaps_borda = []

    # Apenas para visualização: canais e divisores do DXF.
    campo_id = QgsField("cad_id", QVariant.String)
    c_canal = camada_memoria("DREN_01_CANAIS", "LineString", crs, [campo_id])
    for e in canais:
        inserir(c_canal, geom_linha(e["pts"]), [e["id"]])
    c_canal.renderer().setSymbol(QgsLineSymbol.createSimple({
        "line_color": "0,154,230,255", "line_width": "0.7"}))

    c_trans = camada_memoria("DREN_02_DIVISORES_DESCIDAS", "LineString", crs,
                             [campo_id, QgsField("tipo", QVariant.String)])
    for e in transversais:
        tipo = "DESCIDA" if nome_desc and e["layer"] == nome_desc else "DIVISOR"
        inserir(c_trans, geom_linha(e["pts"]), [e["id"], tipo])
    c_trans.renderer().setSymbol(QgsLineSymbol.createSimple({
        "line_color": "37,92,195,255", "line_width": "0.6"}))

    c_setas = None
    if setas:
        c_setas = camada_memoria("DREN_03_SETAS_APROXIMADAS", "Polygon", crs,
                                 [campo_id, QgsField("direcao", QVariant.String)])
        for e in setas:
            pg = poligono_seta(e["pts"])
            if pg and not pg.isEmpty() and pg.isGeosValid():
                inserir(c_setas, pg, [e["id"], direcao])
        c_setas.renderer().setSymbol(QgsFillSymbol.createSimple({
            "color": "20,110,212,220", "outline_style": "no"}))

    c_limite = None
    if borda_pts:
        c_limite = camada_memoria("DREN_04_LIMITE_LONGITUDINAL", "LineString", crs, [campo_id])
        for e in limites:
            inserir(c_limite, geom_linha(e["pts"]), [e["id"]])
        c_limite.renderer().setSymbol(QgsLineSymbol.createSimple({
            "line_color": "222,50,50,255", "line_width": "0.65"}))

    # Projeta as extremidades das transversais no canal e na borda externa.
    secoes = []
    for e in transversais:
        a, b = e["pts"][0], e["pts"][-1]
        da = canal_geom.distance(geom_ponto(a))
        db = canal_geom.distance(geom_ponto(b))
        junto, fora, afast = (a,b,da) if da <= db else (b,a,db)
        s = canal_geom.lineLocatePoint(geom_ponto(junto))
        if s < 0:
            continue
        pp = canal_geom.interpolate(s).asPoint()
        canal_xy = (pp.x(), pp.y())
        pos_borda = None
        dist_borda = 0.0
        if borda_geom is not None:
            pos_borda = borda_geom.lineLocatePoint(geom_ponto(fora))
            if pos_borda < 0:
                continue
            qq = borda_geom.interpolate(pos_borda).asPoint()
            fora_xy = (qq.x(), qq.y())
            dist_borda = distancia(fora, fora_xy)
        else:
            fora_xy = fora
        secoes.append({"s":s, "canal":canal_xy, "fora":fora_xy,
                       "t":pos_borda, "afast":afast,
                       "dist_borda":dist_borda, "id":e["id"]})
    secoes.sort(key=lambda x:x["s"])

    c_areas = camada_memoria("DREN_05_SETORES_PRELIMINARES", "Polygon", crs,
        [QgsField("setor", QVariant.Int), QgsField("origem", QVariant.String),
         QgsField("destino", QVariant.String), QgsField("situacao", QVariant.String),
         QgsField("gap_m", QVariant.Double), QgsField("afast_m", QVariant.Double),
         QgsField("area_m2", QVariant.Double)])
    for idx, (a,b) in enumerate(zip(secoes, secoes[1:]), 1):
        faixa_canal = trecho_linha(canal_geom, canal_pts, a["s"], b["s"])
        if not faixa_canal:
            continue
        if borda_geom is not None:
            faixa_borda = trecho_linha(borda_geom, borda_pts, a["t"], b["t"])
        else:
            faixa_borda = [a["fora"], b["fora"]]
        if not faixa_borda:
            continue
        anel = faixa_borda + list(reversed(faixa_canal))
        if distancia(anel[0], anel[-1]) > 1e-8:
            anel.append(anel[0])
        if len(anel) < 4:
            continue
        geom = QgsGeometry.fromPolygonXY([[ponto(p) for p in anel]])
        if geom.isEmpty() or geom.area() <= 0 or not geom.isGeosValid():
            print("Setor", idx, "inválido, não gerado.")
            continue
        gap = max((g for ini,fim,g in gaps if ini < b["s"] and fim > a["s"]),default=0)
        if borda_geom is not None:
            lo, hi = sorted((a["t"], b["t"]))
            gap = max(gap, max((g for ini,fim,g in gaps_borda
                                if ini < hi and fim > lo), default=0))
        afast = max(a["afast"], b["afast"], a["dist_borda"], b["dist_borda"])
        avisos = []
        if gap > MAX_GAP_M:
            avisos.append("LACUNA")
        if afast > MAX_AFASTAMENTO_M:
            avisos.append("AFASTADO")
        status = "+".join(avisos) if avisos else "PRELIMINAR"
        inserir(c_areas, geom, [idx, a["id"], b["id"], status,
                                float(gap), float(afast), geom.area()])
    c_areas.renderer().setSymbol(QgsFillSymbol.createSimple({
        "color": "250,182,35,90", "outline_color": "220,118,8,255",
        "outline_width": "0.5"}))

    projeto = QgsProject.instance()
    criadas = [c_areas, c_canal, c_trans, c_setas, c_limite]
    for lyr in criadas:
        if lyr is not None:
            lyr.updateExtents()
            projeto.addMapLayer(lyr)
    print("\n== PROCESSAMENTO FINALIZADO ==")
    print("Arquivo:", os.path.basename(dxf))
    print("Divisores/descidas:", len(transversais))
    print("Setas (aproximadas):", c_setas.featureCount() if c_setas else 0)
    print("Direção declarada:", direcao)
    print("Setores preliminares:", c_areas.featureCount())
    print("Lacunas canal (m):", [round(x[2],2) for x in gaps])
    print("ORIGINAIS PRESERVADOS. Confira os polígonos antes de uso hidrológico.")
    # Exportação opcional; nunca sobrescrever arquivos existentes.
    if c_areas.featureCount() > 0 and sim_nao(
            "Deseja salvar agora as camadas geradas como SHP em uma pasta?\n"
            "NÃO: manter apenas as camadas temporárias no projeto QGIS."):
        pasta = QFileDialog.getExistingDirectory(None, "Escolha a pasta de saída (SHP)")
        if pasta:
            from qgis.core import QgsVectorFileWriter
            import datetime
            sufixo = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            for lyr in criadas:
                if lyr is None or not lyr.isValid() or not lyr.featureCount():
                    continue
                caminho_saida = os.path.join(pasta, lyr.name() + "_" + sufixo + ".shp")
                opts = QgsVectorFileWriter.SaveVectorOptions()
                opts.driverName = "ESRI Shapefile"
                opts.fileEncoding = "UTF-8"
                resp = QgsVectorFileWriter.writeAsVectorFormatV3(
                    lyr, caminho_saida, projeto.transformContext(), opts)
                if resp[0] != QgsVectorFileWriter.NoError:
                    print("ERRO AO SALVAR", caminho_saida, resp)
                else:
                    print("SHP salvo:", caminho_saida)
        else:
            print("Exportação cancelada: camadas temporárias permanecem no QGIS.")
    avisar("Processo concluído!\n"
           "Setores preliminares: {}\n"
           "Camadas originais preservadas.\n\n"
           "ATENÇÃO: confira limites, cotas e fluxo. Salve as camadas temporárias\n"
           "em GeoPackage antes de fechar o QGIS.".format(c_areas.featureCount()),
           "Resultado")

