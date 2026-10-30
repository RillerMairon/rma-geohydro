# -*- coding: utf-8 -*-
"""RMA GeoHydro - plugin QGIS 3.28+ (qgis.PyQt compatibility imports)."""
import os
import re
import math
import traceback
from collections import Counter
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (QAction, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog, QDoubleSpinBox,
    QCheckBox, QTextEdit, QFormLayout, QGroupBox)
from qgis.core import (QgsVectorLayer, QgsFeature, QgsGeometry, QgsField,
    QgsWkbTypes, QgsProject, QgsCoordinateReferenceSystem,
    QgsVectorFileWriter, QgsCoordinateTransformContext, QgsPointXY)
from qgis.PyQt.QtCore import QVariant
from .cad_keywords import default_aliases, normalize_cad_name, contains_alias
from .i18n import FileDialog as QFileDialog, InputDialog as QInputDialog, MessageBox as QMessageBox, tr, language, set_language

CATEGORY = {
    'divisores': 'Divisores topograficos',
    'canais': 'Canais',
    'descidas': 'Descidas',
}


def normalize(value):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', str(value or '').lower())
                   if unicodedata.category(c) != 'Mn')


def guess_column(names):
    for cand in ('Layer', 'LAYER', 'layer', 'LayerName', 'layername'):
        if cand in names:
            return cand
    for col in names:
        if 'layer' in col.lower() or 'camada' in col.lower():
            return col
    return None


def line_parts(geom):
    """Return LINESTRING parts from single/multi and geometry collections."""
    if not geom or geom.isEmpty():
        return []
    try:
        if geom.type() == QgsWkbTypes.GeometryType.LineGeometry:
            if geom.isMultipart():
                return [[QgsPointXY(p) for p in part] for part in geom.asMultiPolyline() if len(part) >= 2]
            part = geom.asPolyline()
            return [[QgsPointXY(p) for p in part]] if len(part) >= 2 else []
        if geom.isMultipart() and QgsWkbTypes.flatType(geom.wkbType()) == QgsWkbTypes.Type.GeometryCollection:
            out = []
            for part in geom.asGeometryCollection():
                out.extend(line_parts(part))
            return out
    except Exception:
        return []
    return []


def write_layer(layer, directory, basename, fmt, project):
    ext = '.gpkg' if fmt == 'GPKG' else '.shp'
    path = os.path.join(directory, basename + ext)
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = 'GPKG' if fmt == 'GPKG' else 'ESRI Shapefile'
    options.fileEncoding = 'UTF-8'
    options.layerName = basename
    if os.path.exists(path):
        if fmt == 'GPKG':
            options.actionOnExistingFile = QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile
        else:
            # Delete sidecars safely via provider (not by overwriting a locked loaded layer).
            old = QgsVectorLayer(path, basename, 'ogr')
            if old.isValid():
                QgsVectorFileWriter.deleteShapeFile(path)
    result = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer, path, project.transformContext(), options)
    if result[0] != QgsVectorFileWriter.WriterError.NoError:
        raise RuntimeError('Falha ao salvar {}: {}'.format(path, result[1]))
    output = QgsVectorLayer(path, basename, 'ogr')
    if not output.isValid():
        raise RuntimeError('Arquivo escrito, mas camada invalida: ' + path)
    project.addMapLayer(output)
    return path


class DrainageDialog(QDialog):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle('RMA GeoHydro | Áreas de drenagem preliminares (v0.3.3)')
        self.resize(750, 680)
        layout = QVBoxLayout(self)
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel('Idioma / Language:'))
        self.language_select = QComboBox()
        self.language_select.addItem('Português (Brasil)', 'pt_BR')
        self.language_select.addItem('English (US)', 'en_US')
        self.language_select.setCurrentIndex(1 if language() == 'en_US' else 0)
        lang_row.addWidget(self.language_select)
        lang_row.addStretch()
        layout.addLayout(lang_row)
        self.language_select.currentIndexChanged.connect(self.change_language)
        headline = QLabel('RMA GeoHydro — preparacao e diagnostico de drenagem via DXF')
        headline.setStyleSheet('font-size: 15px; font-weight: bold;')
        layout.addWidget(headline)
        layout.addWidget(QLabel('Etapa inicial: classificar entidades CAD, verificar geometrias e gerar camadas.'))

        form = QFormLayout()
        source_row = QHBoxLayout()
        self.path = QLineEdit()
        self.path.setPlaceholderText('Selecione um arquivo .dxf')
        source_row.addWidget(self.path)
        browse = QPushButton('Procurar...')
        browse.clicked.connect(self.browse_input)
        source_row.addWidget(browse)
        form.addRow('Arquivo DXF', source_row)

        self.source_name = QComboBox()
        self.source_name.setToolTip('Sublayer OGR contendo as entidades do DXF.')
        form.addRow('Subcamada DXF', self.source_name)
        self.field = QComboBox()
        self.field.setToolTip('Campo que contem o layer CAD original.')
        form.addRow('Campo do layer CAD', self.field)
        self.crs = QLineEdit()
        self.crs.setPlaceholderText('Ex.: EPSG:31983 — necessario se o DXF nao tiver CRS')
        form.addRow('SRC do DXF (EPSG)', self.crs)
        layout.addLayout(form)

        group = QGroupBox('Classificacao assistida por nomes de layers CAD')
        group_layout = QVBoxLayout(group)
        # A compact summary is always displayed. Full matching aliases are hidden
        # by default; QLineEdit values remain the single source of truth for processing.
        summary = QFormLayout()
        self.summary_labels = {}
        for key in CATEGORY:
            label = QLabel('Reconhecimento automatico (PT/EN)')
            label.setToolTip('Correspondencia por nomes de camadas CAD em portugues e ingles. Confira os resultados antes do uso.')
            summary.addRow(CATEGORY[key], label)
            self.summary_labels[key] = label
        group_layout.addLayout(summary)
        self.advanced_toggle = QPushButton('Configuracoes avancadas')
        self.advanced_toggle.setCheckable(True)
        self.advanced_toggle.setChecked(False)
        group_layout.addWidget(self.advanced_toggle)
        self.advanced_group = QGroupBox('Palavras-chave de reconhecimento CAD (editaveis)')
        self.advanced_group.setVisible(False)
        advanced_form = QFormLayout(self.advanced_group)
        self.kw = {}
        self._default_keywords = {}
        for key in CATEGORY:
            value = default_aliases(key, language())
            edit = QLineEdit(value)
            edit.setToolTip('Separe termos por virgula; correspondencia parcial sem diferenciar acentos.')
            self.kw[key] = edit
            self._default_keywords[key] = value
            advanced_form.addRow(CATEGORY[key], edit)
        group_layout.addWidget(self.advanced_group)
        self.advanced_toggle.toggled.connect(self._toggle_advanced)
        layout.addWidget(group)

        options = QFormLayout()
        self.orientation = QComboBox()
        self.orientation.addItems(['Ambas (longitudinal e transversal)', 'Longitudinal', 'Transversal'])
        self.orientation.setToolTip('Escolha a configuração do projeto. A geometria segue o canal de referência e as transversais confirmadas, não o azimute norte/sul.')
        options.addRow('Orientacao principal', self.orientation)
        self.tolerance = QDoubleSpinBox()
        self.tolerance.setRange(0.001, 100000)
        self.tolerance.setDecimals(3)
        self.tolerance.setValue(0.50)
        self.tolerance.setSuffix(' unidades do SRC')
        options.addRow('Tolerancia de conexao', self.tolerance)
        self.make_polygons = QCheckBox('Tentar polygonizar limites FECHADOS (divisores + canais + descidas)')
        self.make_polygons.setChecked(False)
        options.addRow('', self.make_polygons)
        self.output_format = QComboBox()
        self.output_format.addItems(['GeoPackage (.gpkg)', 'Shapefile (.shp)'])
        options.addRow('Formato de saida', self.output_format)
        out_row = QHBoxLayout()
        self.output_dir = QLineEdit()
        out_row.addWidget(self.output_dir)
        pick = QPushButton('Pasta...')
        pick.clicked.connect(self.browse_output)
        out_row.addWidget(pick)
        options.addRow('Pasta de saida', out_row)
        layout.addLayout(options)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText('O diagnostico sera exibido aqui.')
        layout.addWidget(self.log, 1)
        row = QHBoxLayout()
        sectors = QPushButton('GERAR ÁREAS DE DRENAGEM PRELIMINARES (assistido)')
        sectors.setToolTip('Delimitação preliminar por canal, divisores/descidas e limite opcional. Não substitui validação hidrológica.')
        sectors.clicked.connect(self.execute_sectors)
        row.addWidget(sectors)
        run = QPushButton('Classificar linhas e exportar')
        run.clicked.connect(self.execute)
        row.addWidget(run)
        close = QPushButton('Fechar')
        close.clicked.connect(self.reject)
        row.addWidget(close)
        layout.addLayout(row)
        self.source_name.currentIndexChanged.connect(self.update_fields)
        self.localize_ui()

    def _toggle_advanced(self, enabled):
        self.advanced_group.setVisible(enabled)
        if enabled:
            self.advanced_toggle.setText(tr('Ocultar configuracoes avancadas'))
        else:
            self.advanced_toggle.setText(tr('Configuracoes avancadas'))
        self.adjustSize()

    def change_language(self, *_):
        set_language(self.language_select.currentData())
        # Reopen the form to refresh labels; preserve the entered file path and settings
        # in the current session rather than clearing them unexpectedly.
        self.localize_ui()

    def localize_ui(self):
        # Preserve originals to support switching languages in either direction.
        from qgis.PyQt.QtWidgets import QLabel, QPushButton, QGroupBox, QCheckBox
        if not hasattr(self, '_original_ui'):
            self._original_ui = []
            for widget in (self.findChildren(QLabel) + self.findChildren(QPushButton) + self.findChildren(QGroupBox) + self.findChildren(QCheckBox)):
                self._original_ui.append((widget, widget.text() if hasattr(widget, 'text') else widget.title(),
                    widget.toolTip()))
            self._original_forms = []
            for form in self.findChildren(QFormLayout):
                for i in range(form.rowCount()):
                    item = form.itemAt(i, QFormLayout.LabelRole)
                    if item and item.widget() and isinstance(item.widget(), QLabel):
                        label = item.widget()
                        if not any(w is label for w, _, _ in self._original_ui):
                            self._original_ui.append((label, label.text(), label.toolTip()))
            self._original_placeholders = [(w,w.placeholderText()) for w in
                [self.path, self.crs, self.log]]
            self._original_orientation = [self.orientation.itemText(i) for i in range(self.orientation.count())]
            self._original_suffix = self.tolerance.suffix()
        for widget, original, original_tip in self._original_ui:
            if isinstance(widget, QGroupBox): widget.setTitle(tr(original))
            elif hasattr(widget, 'setText'): widget.setText(tr(original))
            widget.setToolTip(tr(original_tip))
        for widget, original in self._original_placeholders:
            widget.setPlaceholderText(tr(original))
        selected = self.orientation.currentIndex()
        for i, original in enumerate(self._original_orientation):
            self.orientation.setItemText(i, tr(original))
        self.orientation.setCurrentIndex(selected)
        self.tolerance.setSuffix(tr(self._original_suffix))
        # Display aliases in the selected language order without removing
        # international matches or overwriting user-customized keywords.
        for key, widget in self.kw.items():
            old_default = self._default_keywords[key]
            if widget.text() == old_default:
                new_default = default_aliases(key, language())
                widget.setText(new_default)
                self._default_keywords[key] = new_default
        self._toggle_advanced(self.advanced_toggle.isChecked())
        self.setWindowTitle('RMA GeoHydro | ' + ('Preliminary drainage areas' if language() == 'en_US' else 'Áreas de drenagem preliminares') + ' (v0.3.3)')

    def msg(self, message):
        self.log.append(tr(str(message)))

    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Selecionar DXF', '', 'DXF (*.dxf)')
        if path:
            self.path.setText(path)
            self.discover_sources()

    def browse_output(self):
        directory = QFileDialog.getExistingDirectory(self, 'Selecionar pasta de saida')
        if directory:
            self.output_dir.setText(directory)

    def discover_sources(self):
        self.source_name.clear()
        file_path = self.path.text().strip()
        if not os.path.isfile(file_path):
            return
        # Auto-detect common OGR DXF entity sublayers, independently of layer labels.
        candidates = [('entities', file_path + '|layername=entities'),
                      ('entities (padrao OGR)', file_path),
                      ('Entities', file_path + '|layername=Entities')]
        for label, uri in candidates:
            layer = QgsVectorLayer(uri, label, 'ogr')
            if layer.isValid() and layer.featureCount() > 0 and layer.geometryType() == QgsWkbTypes.GeometryType.LineGeometry:
                self.source_name.addItem(label, uri)
        if self.source_name.count() == 0:
            # DXF providers may report Unknown/Collection for mixed CAD entities.
            for label, uri in candidates:
                layer = QgsVectorLayer(uri, label, 'ogr')
                if layer.isValid() and layer.featureCount() > 0:
                    self.source_name.addItem(label, uri)
        if self.source_name.count() == 0:
            self.msg('ERRO: nenhum conjunto de entidades DXF legivel foi localizado.')
        self.update_fields()

    def update_fields(self, *_):
        self.field.clear()
        uri = self.source_name.currentData()
        if not uri:
            return
        layer = QgsVectorLayer(uri, 'temporario_dxf', 'ogr')
        if layer.isValid():
            names = [f.name() for f in layer.fields()]
            self.field.addItems(names)
            suggested = guess_column(names)
            if suggested:
                self.field.setCurrentText(suggested)

    def _orientation_value(self):
        return ('Ambas', 'Longitudinal', 'Transversal')[self.orientation.currentIndex()]

    def execute_sectors(self):
        """Executa fluxo universal dos setores usando a lógica original validada visualmente."""
        try:
            from .setores_azul_universal import executar
            caminho = self.path.text().strip()
            epsg = self.crs.text().strip().upper()
            if not caminho or not os.path.isfile(caminho):
                self.browse_input()
                caminho = self.path.text().strip()
            if not epsg:
                epsg, ok = QInputDialog.getText(self, 'SRC do desenho',
                    'Informe o EPSG original do DXF:', text=QgsProject.instance().crs().authid())
                if not ok: return
            formato = 'SHP' if self.output_format.currentIndex() == 1 else 'GPKG'
            quantidade = executar(caminho=caminho, epsg=epsg,
                diretorio=self.output_dir.text().strip(), formato=formato,
                orientacao=self._orientation_value())
            if quantidade is not None:
                self.msg('Áreas de drenagem preliminares geradas: {}'.format(quantidade))
        except Exception as exc:
            self.msg('Erro na delimitação dos setores: {}'.format(exc))
            QMessageBox.warning(self, 'RMA GeoHydro', str(exc))

    def execute(self):
        self.log.clear()
        try:
            self.run_pipeline()
        except Exception as exc:
            self.msg('ERRO: {}'.format(exc))
            self.msg(traceback.format_exc())
            QMessageBox.critical(self, 'RMA GeoHydro', 'Falha durante processamento:\n{}'.format(exc))

    def run_pipeline(self):
        path = self.path.text().strip()
        if not os.path.isfile(path) or not path.lower().endswith('.dxf'):
            raise ValueError('Selecione um arquivo DXF existente usando Procurar.')
        if not self.source_name.count():
            self.discover_sources()
        uri = self.source_name.currentData()
        if not uri:
            raise ValueError('Nao foi encontrada subcamada DXF valida.')
        layer = QgsVectorLayer(uri, 'RMA_DXF', 'ogr')
        if not layer.isValid():
            raise ValueError('Fonte de dados DXF invalida. Confira o caminho e o arquivo.')
        field = self.field.currentText()
        if field not in [f.name() for f in layer.fields()]:
            raise ValueError('Campo do layer CAD nao identificado. Escolha o campo correto.')
        src_text = self.crs.text().strip().upper()
        if src_text:
            source_crs = QgsCoordinateReferenceSystem(src_text)
            if not source_crs.isValid():
                raise ValueError('SRC invalido: use formato EPSG:31983, por exemplo.')
        else:
            source_crs = layer.crs()
        if not source_crs.isValid():
            raise ValueError('DXF sem SRC. Preencha o EPSG conforme o desenho original.')
        if source_crs.isGeographic():
            raise ValueError('SRC em graus. Utilize um SRC projetado, preferencialmente UTM em metros.')
        # Units must be meters for meaningful network-tolerance reporting.
        if source_crs.mapUnits() != 0:  # Metric map units are required for distance-based operations.
            from qgis.core import QgsUnitTypes
            if source_crs.mapUnits() != QgsUnitTypes.DistanceUnit.DistanceMeters:
                raise ValueError('SRC nao esta em metros. Reprojete o desenho antes de processar.')
        directory = self.output_dir.text().strip()
        if not directory or not os.path.isdir(directory):
            raise ValueError('Informe uma pasta de saida existente.')
        fmt = 'GPKG' if self.output_format.currentIndex() == 0 else 'SHP'
        terms = {k: [normalize(t.strip()) for t in inp.text().split(',') if t.strip()]
                 for k, inp in self.kw.items()}
        if any(not v for v in terms.values()):
            raise ValueError('Preencha palavras-chave para as tres categorias.')
        mem = {}
        for key in CATEGORY:
            out = QgsVectorLayer('LineString?crs=' + source_crs.authid(), 'RMA_' + key, 'memory')
            out.dataProvider().addAttributes([QgsField('cad_layer', QVariant.String),
                                               QgsField('classe', QVariant.String),
                                               QgsField('source_id', QVariant.LongLong)])
            out.updateFields()
            mem[key] = out
        counts = Counter()
        unmatched = Counter()
        endpoints = {k: [] for k in CATEGORY}
        polygon_lines = []
        skipped = 0
        for feature in layer.getFeatures():
            cad_layer = str(feature[field] or '')
            v = normalize(cad_layer)
            matches = [k for k, keywords in terms.items() if contains_alias(v, keywords)]
            if not matches:
                unmatched[cad_layer] += 1
                continue
            if len(matches) > 1:
                counts['ambiguo'] += 1
                unmatched[cad_layer] += 1
                continue
            key = matches[0]
            parts = line_parts(feature.geometry())
            if not parts:
                skipped += 1
                continue
            feats = []
            for part in parts:
                if len(part) < 2:
                    continue
                new_feature = QgsFeature(mem[key].fields())
                new_feature.setGeometry(QgsGeometry.fromPolylineXY(part))
                new_feature.setAttributes([cad_layer, key, int(feature.id())])
                feats.append(new_feature)
                endpoints[key].extend((part[0], part[-1]))
                polygon_lines.append(QgsGeometry.fromPolylineXY(part))
            mem[key].dataProvider().addFeatures(feats)
            counts[key] += len(feats)
        for out in mem.values():
            out.updateExtents()
        self.msg('Fonte: {}'.format(path))
        self.msg('SRC: {} | Orientacao declarada: {}'.format(source_crs.authid(), self._orientation_value()))
        self.msg('IMPORTANTE: orientacao e um metadado operacional; esta versao NAO altera automaticamente a geometria pelo sentido do canal.')
        self.msg('Entidades lineares classificadas: {}'.format(sum(counts[k] for k in CATEGORY)))
        for key in CATEGORY:
            self.msg('  {}: {}'.format(CATEGORY[key], counts[key]))
        self.msg('Ambiguas: {} | Geometrias nao lineares/invalidas ignoradas: {}'.format(counts['ambiguo'], skipped))
        if unmatched:
            self.msg('Layers CAD sem classificacao (ou ambiguos): ' + '; '.join('{} ({})'.format(k, n) for k,n in unmatched.most_common(20)))
        if not sum(counts[k] for k in CATEGORY):
            raise ValueError('Nenhuma linha classificada. Revise campo Layer e palavras-chave antes de exportar.')

        tol = self.tolerance.value()
        # Endpoint proximity diagnostic; endpoints within tolerance count as candidates,
        # not as guaranteed topology or hydraulic connectivity.
        nodes = []
        for cat, pts in endpoints.items():
            for point in pts:
                nodes.append((cat, point))
        near = 0
        isolated = 0
        # Spatial hash: avoid O(n^2) on large drawings.
        buckets = {}
        for i, (_, point) in enumerate(nodes):
            cell = (math.floor(point.x()/tol), math.floor(point.y()/tol))
            buckets.setdefault(cell, []).append(i)
        for i, (_, p) in enumerate(nodes):
            cx, cy = math.floor(p.x()/tol), math.floor(p.y()/tol)
            found = False
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    for j in buckets.get((cx+a, cy+b), []):
                        if j != i and p.distance(nodes[j][1]) <= tol:
                            found = True
                            break
                    if found: break
                if found: break
            if found: near += 1
            else: isolated += 1
        self.msg('Extremidades: {} | com vizinho ate {:.3f} m: {} | sem vizinho: {}'.format(len(nodes), tol, near, isolated))
        self.msg('AVISO: conexoes nos meios das linhas, cruzamentos e declividade nao sao validados nesta versao.')

        project = QgsProject.instance()
        saved = []
        for key, out in mem.items():
            if out.featureCount():
                saved.append(write_layer(out, directory, 'RMA_' + key, fmt, project))

        if self.make_polygons.isChecked():
            self.msg('Polygonizacao solicitada: apenas anéis fechados existentes podem gerar areas.')
            try:
                # QgsGeometry.polygonize returns a geometry collection / multipolygon.
                poly = QgsGeometry.polygonize(polygon_lines)
                polygons = []
                if poly and not poly.isEmpty():
                    if poly.type() == QgsWkbTypes.GeometryType.PolygonGeometry:
                        if poly.isMultipart():
                            polygons = [QgsGeometry.fromPolygonXY(p) for p in poly.asMultiPolygon()]
                        else:
                            polygons = [QgsGeometry.fromPolygonXY(poly.asPolygon())]
                    else:
                        for g in poly.asGeometryCollection():
                            if g.type() == QgsWkbTypes.GeometryType.PolygonGeometry:
                                polygons.extend([QgsGeometry.fromPolygonXY(p) for p in g.asMultiPolygon()] if g.isMultipart() else [g])
                if polygons:
                    out_poly = QgsVectorLayer('Polygon?crs=' + source_crs.authid(), 'RMA_areas_fechadas', 'memory')
                    out_poly.dataProvider().addAttributes([QgsField('id_area', QVariant.Int)])
                    out_poly.updateFields()
                    to_add = []
                    for j, geom in enumerate(polygons, 1):
                        f = QgsFeature(out_poly.fields())
                        f.setGeometry(geom)
                        f.setAttributes([j])
                        to_add.append(f)
                    out_poly.dataProvider().addFeatures(to_add)
                    out_poly.updateExtents()
                    saved.append(write_layer(out_poly, directory, 'RMA_areas_fechadas', fmt, project))
                    self.msg('Areas fechadas geradas: {}'.format(len(to_add)))
                else:
                    self.msg('Nenhuma area fechada encontrada. Nao foram inventados limites.')
            except Exception as exc:
                self.msg('Polygonizacao nao concluida: {}'.format(exc))
        report = os.path.join(directory, 'RMA_diagnostico.txt')
        with open(report, 'w', encoding='utf-8') as fh:
            fh.write(self.log.toPlainText() + '\n')
        self.msg('Arquivos salvos: ' + ', '.join(saved))
        self.msg('Diagnostico: ' + report)
        QMessageBox.information(self, 'RMA GeoHydro', 'Processamento concluido. Confira o diagnostico e as camadas geradas.')


class RMAGeoHydroPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        icon = QIcon(os.path.join(os.path.dirname(__file__), 'icon.svg'))
        self.action = QAction(icon, 'RMA GeoHydro', self.iface.mainWindow())
        self.action.triggered.connect(self.open_dialog)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu('&RMA GeoHydro', self.action)

    def open_dialog(self):
        self.dialog = DrainageDialog(self.iface, self.iface.mainWindow())
        self.dialog.exec()

    def unload(self):
        if self.action:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu('&RMA GeoHydro', self.action)
