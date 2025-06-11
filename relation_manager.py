# relation_manager.py
import os
from qgis.PyQt.QtCore import QTranslator, QCoreApplication, QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from .relation_dialog import RelationDialog


class RelationManager:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # Inizializza locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RelationManager_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr('&Relation Manager')
        self.dlg = None  # Inizializza come None

    def tr(self, message):
        return QCoreApplication.translate('RelationManager', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True,
                   add_to_menu=True, add_to_toolbar=True, status_tip=None,
                   whats_this=None, parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        """Crea le voci di menu e i pulsanti della toolbar"""
        icon_path = os.path.join(self.plugin_dir, 'icon.png')

        # Se non esiste l'icona, usa un'icona vuota
        if not os.path.exists(icon_path):
            icon_path = ':/images/themes/default/mActionAddGroup.svg'

        self.add_action(
            icon_path,
            text=self.tr('Gestisci Relazioni'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Rimuove le voci di menu e i pulsanti della toolbar"""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr('&Relation Manager'), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Esegue il plugin"""
        # Crea sempre una nuova istanza del dialog
        self.dlg = RelationDialog()

        # Mostra il dialog
        self.dlg.show()

        # Esegue il dialog e aspetta la risposta
        result = self.dlg.exec_()