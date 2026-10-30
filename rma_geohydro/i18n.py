# -*- coding: utf-8 -*-
"""RMA GeoHydro user-facing language support (pt_BR / en_US).
Technical feature attributes, CAD layer names and geometry code are not translated.
"""
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox, QFileDialog

KEY = 'rma_geohydro/language'

def language():
    val = QSettings().value(KEY, 'pt_BR')
    return val if val in ('pt_BR', 'en_US') else 'pt_BR'

def set_language(value):
    QSettings().setValue(KEY, value if value in ('pt_BR', 'en_US') else 'pt_BR')

# Exact technical terms use the approved working glossary where applicable.
EN = {
    'Divisores topograficos': 'Topographic divides',
    'Reconhecimento automatico (PT/EN)': 'Automatic recognition (PT/EN)',
    'Correspondencia por nomes de camadas CAD em portugues e ingles. Confira os resultados antes do uso.': 'Matches CAD layer names in Portuguese and English. Review the results before use.',
    'Configuracoes avancadas': 'Advanced settings',
    'Ocultar configuracoes avancadas': 'Hide advanced settings',
    'Palavras-chave de reconhecimento CAD (editaveis)': 'CAD recognition keywords (editable)',
    'Canais': 'Channels', 'Descidas': 'Downchutes',
    'RMA GeoHydro — preparacao e diagnostico de drenagem via DXF': 'RMA GeoHydro — CAD/DXF drainage preparation and diagnostics',
    'Etapa inicial: classificar entidades CAD, verificar geometrias e gerar camadas.': 'First step: classify CAD entities, check geometries and create layers.',
    'Selecione um arquivo .dxf': 'Select a .dxf file',
    'Procurar...': 'Browse...', 'Arquivo DXF': 'DXF file',
    'Subcamada DXF': 'DXF sublayer', 'Campo do layer CAD': 'CAD layer field',
    'SRC do DXF (EPSG)': 'DXF CRS (EPSG)',
    'Sublayer OGR contendo as entidades do DXF.': 'OGR sublayer containing DXF entities.',
    'Campo que contem o layer CAD original.': 'Field containing the original CAD layer.',
    'Ex.: EPSG:31983 — necessario se o DXF nao tiver CRS': 'e.g. EPSG:31983 — required when DXF lacks a CRS',
    'Classificacao assistida por nomes de layers CAD': 'Assisted classification by CAD layer names',
    'Separe termos por virgula; correspondencia parcial sem diferenciar acentos.': 'Separate terms with commas; partial match, accent-insensitive.',
    'Ambas (longitudinal e transversal)': 'Both (longitudinal and transverse)',
    'Longitudinal': 'Longitudinal', 'Transversal': 'Transverse',
    'Escolha a configuração do projeto. A geometria segue o canal de referência e as transversais confirmadas, não o azimute norte/sul.': 'Choose project settings. Geometry follows the reference channel and confirmed transverse lines; it is not a north/south azimuth classification.',
    'Orientacao principal': 'Main orientation', 'Tolerancia de conexao': 'Connection tolerance',
    ' unidades do SRC': ' CRS units',
    'Tentar polygonizar limites FECHADOS (divisores + canais + descidas)': 'Try polygonizing CLOSED boundaries (divides + channels + downchutes)',
    'Formato de saida': 'Output format', 'Pasta...': 'Folder...', 'Pasta de saida': 'Output folder',
    'O diagnostico sera exibido aqui.': 'Diagnostics will appear here.',
    'GERAR ÁREAS DE DRENAGEM PRELIMINARES (assistido)': 'GENERATE PRELIMINARY DRAINAGE AREAS (assisted)',
    'Delimitação preliminar por canal, divisores/descidas e limite opcional. Não substitui validação hidrológica.': 'Preliminary delineation using channels, divides/downchutes and an optional boundary. Hydrological validation is still required.',
    'Classificar linhas e exportar': 'Classify lines and export', 'Fechar': 'Close',
    'Selecionar DXF': 'Select DXF', 'Selecionar pasta de saida': 'Select output folder',
    'SRC do desenho': 'Drawing CRS', 'Informe o EPSG original do DXF:': 'Enter the original DXF EPSG:',
    'Canal de referência': 'Reference channel', 'Divisores': 'Topographic divides',
    'Setas de fluxo (opcional)': 'Flow arrows (optional)',
    'Selecione a camada CAD correspondente (confira a sugestão):': 'Select the matching CAD layer (check the suggestion):',
    '(Nenhuma)': '(None)', '(não selecionada)': '(not selected)',
    'Selecionar arquivo DXF': 'Select DXF file',
    'SRC de origem': 'Source CRS', 'EPSG do DXF (por exemplo EPSG:32629):': 'DXF EPSG (e.g. EPSG:32629):',
    'RMA GeoHydro - confirmar elementos': 'RMA GeoHydro - confirm features',
    'Exportação de setores': 'Drainage area export',
    'RMA GeoHydro - setores preliminares': 'RMA GeoHydro - preliminary drainage areas',
    'Orientação informada:': 'Declared orientation:', 'Canal de referência:': 'Reference channel:',
    'Divisores:': 'Divides:', 'Descidas:': 'Downchutes:',
    'Total de transversais:': 'Total transverse lines:',
    'Os setores serão construídos entre transversais consecutivas em relação ao canal selecionado. Isso não classifica hidraulicamente a orientação. Continuar?': 'Preliminary drainage areas will be constructed between consecutive transverse lines along the selected channel. This does not determine hydraulic flow direction. Continue?',
    'Orientação escolhida:': 'Chosen orientation:', 'Transversais:': 'Transverse lines:',
    'Setas:': 'Arrows:', 'Setores preliminares:': 'Preliminary drainage areas:',
    'Rejeitados:': 'Rejected:', 'Lacunas de canal (m):': 'Channel gaps (m):',
    'ATENÇÃO: limites aproximados; NÃO usar para cálculos hidrológicos sem validação.': 'CAUTION: approximate boundaries; DO NOT use for hydrological calculations without validation.',
    'Selecione um arquivo DXF existente usando Procurar.': 'Select an existing DXF file using Browse.',
    'Nao foi encontrada subcamada DXF valida.': 'No valid DXF sublayer was found.',
    'Fonte de dados DXF invalida. Confira o caminho e o arquivo.': 'Invalid DXF data source. Check the path and file.',
    'Campo do layer CAD nao identificado. Escolha o campo correto.': 'CAD layer field not identified. Select the correct field.',
    'SRC invalido: use formato EPSG:31983, por exemplo.': 'Invalid CRS: use the EPSG:31983 format, for example.',
    'DXF sem SRC. Preencha o EPSG conforme o desenho original.': 'DXF has no CRS. Enter the EPSG of the original drawing.',
    'SRC em graus. Utilize um SRC projetado, preferencialmente UTM em metros.': 'CRS uses degrees. Use a projected CRS, preferably UTM in metres.',
    'SRC nao esta em metros. Reprojete o desenho antes de processar.': 'CRS units are not metres. Reproject the drawing before processing.',
    'Informe uma pasta de saida existente.': 'Select an existing output folder.',
    'Preencha palavras-chave para as tres categorias.': 'Provide keywords for all three categories.',
    'Processamento concluido. Confira o diagnostico e as camadas geradas.': 'Processing completed. Review the diagnostics and generated layers.',
    'O SRC informado precisa ser projetado e em metros.': 'The specified CRS must be projected and in metres.',
    'Nenhuma LWPOLYLINE encontrada. Verifique se o DXF está em formato ASCII com polilinhas compatíveis.': 'No LWPOLYLINE found. Verify the DXF is ASCII and contains compatible polylines.',
    'Operação cancelada pelo usuário.': 'Operation cancelled by user.',
    'A camada das descidas não pode ser a mesma do canal.': 'The downchute layer cannot be the same as the channel layer.',
    'A camada de setas deve ser distinta das camadas de drenagem.': 'The flow-arrow layer must differ from drainage layers.',
    'As camadas de canal e de transversais devem ser diferentes.': 'Channel and transverse-line layers must be different.',
    'São necessários um canal e no mínimo duas linhas transversais.': 'At least one channel and two transverse lines are required.',
    'Salvar os setores e camadas auxiliares como {} na pasta escolhida?': 'Save drainage areas and auxiliary layers as {} in the chosen folder?',
}

EN.update({
    'Exportação de áreas de drenagem': 'Drainage area export',
    'Salvar as áreas de drenagem e camadas auxiliares como {} na pasta escolhida?': 'Save drainage areas and auxiliary layers as {} in the selected folder?',
    'RMA GeoHydro - áreas de drenagem preliminares': 'RMA GeoHydro - preliminary drainage areas',
    'Áreas de drenagem preliminares:': 'Preliminary drainage areas:',
})

def tr(text):
    if language() != 'en_US':
        return str(text)
    s = str(text)
    if s in EN:
        return EN[s]
    # Only user-facing prompts, diagnostics or errors: do not change CAD names or field values.
    for pt, en in sorted(EN.items(), key=lambda x: -len(x[0])):
        if pt and pt in s:
            s = s.replace(pt, en)
    return s

class InputDialog:
    @staticmethod
    def getItem(parent, title, label, items, *args, **kwargs):
        # Translate the optional sentinel, but never rename real CAD layer values.
        labels = [tr(i) if i in ('(Nenhuma)', '(não possui)', 'Não sei') else i for i in items]
        selected, ok = QInputDialog.getItem(parent, tr(title), tr(label), labels, *args, **kwargs)
        if selected == '(None)': selected = '(Nenhuma)'
        return selected, ok
    @staticmethod
    def getText(parent, title, label, *args, **kwargs):
        return QInputDialog.getText(parent, tr(title), tr(label), *args, **kwargs)

class MessageBox:
    StandardButton = QMessageBox.StandardButton
    @staticmethod
    def question(parent, title, message, *args, **kwargs):
        return QMessageBox.question(parent, tr(title), tr(message), *args, **kwargs)
    @staticmethod
    def information(parent, title, message, *args, **kwargs):
        return QMessageBox.information(parent, tr(title), tr(message), *args, **kwargs)
    @staticmethod
    def warning(parent, title, message, *args, **kwargs):
        return QMessageBox.warning(parent, tr(title), tr(message), *args, **kwargs)
    @staticmethod
    def critical(parent, title, message, *args, **kwargs):
        return QMessageBox.critical(parent, tr(title), tr(message), *args, **kwargs)

class FileDialog:
    @staticmethod
    def getOpenFileName(parent, title, *args, **kwargs):
        return QFileDialog.getOpenFileName(parent, tr(title), *args, **kwargs)
    @staticmethod
    def getExistingDirectory(parent, title, *args, **kwargs):
        return QFileDialog.getExistingDirectory(parent, tr(title), *args, **kwargs)
