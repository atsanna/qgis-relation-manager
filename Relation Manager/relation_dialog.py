# relation_dialog.py
import os
import json
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                 QPushButton, QTableWidget, QTableWidgetItem,
                                 QLabel, QMessageBox, QFileDialog, QHeaderView,
                                 QDialogButtonBox, QSpacerItem, QSizePolicy,
                                 QTextEdit, QCheckBox, QComboBox, QFormLayout,
                                 QGroupBox)
from qgis.core import QgsProject, QgsRelation, QgsVectorLayer, QgsRelationManager


class RelationDialog(QDialog):
    def __init__(self, parent=None):
        super(RelationDialog, self).__init__(parent)
        self.setupUi()

        # Connetti i pulsanti
        self.exportButton.clicked.connect(self.export_relations)
        self.importButton.clicked.connect(self.import_relations)
        self.refreshButton.clicked.connect(self.refresh_relations)

        # Carica le relazioni attuali
        self.refresh_relations()

    def setupUi(self):
        """Crea l'interfaccia utente programmaticamente"""
        self.setWindowTitle("Gestione Relazioni")
        self.setGeometry(100, 100, 900, 700)

        # Layout principale
        layout = QVBoxLayout()

        # Titolo
        title_label = QLabel("Gestione Relazioni del Progetto")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Layout pulsanti
        button_layout = QHBoxLayout()

        self.exportButton = QPushButton("Esporta Relazioni")
        self.importButton = QPushButton("Importa Relazioni")
        self.refreshButton = QPushButton("Aggiorna")

        button_layout.addWidget(self.exportButton)
        button_layout.addWidget(self.importButton)
        button_layout.addWidget(self.refreshButton)

        # Spacer per allineare i pulsanti a sinistra
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)

        layout.addLayout(button_layout)

        # Label informativo per quando non ci sono relazioni
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: gray; font-style: italic; margin: 20px;")
        layout.addWidget(self.info_label)

        # Tabella relazioni
        self.relationsTable = QTableWidget()
        self.relationsTable.setAlternatingRowColors(True)
        self.relationsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.relationsTable.setSortingEnabled(True)
        layout.addWidget(self.relationsTable)

        # Area di debug/log
        debug_group = QGroupBox("Log Importazione")
        debug_layout = QVBoxLayout()
        self.debugText = QTextEdit()
        self.debugText.setMaximumHeight(150)
        self.debugText.setReadOnly(True)
        debug_layout.addWidget(self.debugText)
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)

        # Pulsanti di chiusura
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def log_message(self, message):
        """Aggiunge un messaggio al log di debug"""
        self.debugText.append(message)

    def refresh_relations(self):
        """Aggiorna la tabella con le relazioni attuali"""
        project = QgsProject.instance()
        relation_manager = project.relationManager()
        relations = relation_manager.relations()

        if not relations:
            # Nessuna relazione trovata
            self.relationsTable.setRowCount(0)
            self.relationsTable.setColumnCount(4)
            self.relationsTable.setHorizontalHeaderLabels([
                'ID', 'Nome', 'Layer Figlio', 'Layer Padre'
            ])
            self.info_label.setText(
                "Nessuna relazione trovata nel progetto corrente.\nUtilizza 'Importa Relazioni' per caricare relazioni da un file JSON.")
            self.info_label.show()
            self.exportButton.setEnabled(False)
        else:
            # Ci sono relazioni da mostrare
            self.info_label.hide()
            self.exportButton.setEnabled(True)

            self.relationsTable.setRowCount(len(relations))
            self.relationsTable.setColumnCount(4)
            self.relationsTable.setHorizontalHeaderLabels([
                'ID', 'Nome', 'Layer Figlio', 'Layer Padre'
            ])

            for row, (rel_id, relation) in enumerate(relations.items()):
                self.relationsTable.setItem(row, 0, QTableWidgetItem(rel_id))
                self.relationsTable.setItem(row, 1, QTableWidgetItem(relation.name()))

                # Layer padre (referencing layer)
                parent_layer = relation.referencingLayer()
                parent_name = parent_layer.name() if parent_layer else "N/A"
                self.relationsTable.setItem(row, 2, QTableWidgetItem(parent_name))

                # Layer figlio (referenced layer)
                child_layer = relation.referencedLayer()
                child_name = child_layer.name() if child_layer else "N/A"
                self.relationsTable.setItem(row, 3, QTableWidgetItem(child_name))

        # Ridimensiona le colonne
        header = self.relationsTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

    def export_relations(self):
        """Esporta le relazioni in un file JSON"""
        project = QgsProject.instance()
        relation_manager = project.relationManager()
        relations = relation_manager.relations()

        if not relations:
            QMessageBox.information(self, "Informazione",
                                    "Nessuna relazione trovata nel progetto corrente.")
            return

        # Seleziona il file di destinazione
        filename, _ = QFileDialog.getSaveFileName(
            self, "Esporta Relazioni", "", "JSON Files (*.json)")

        if not filename:
            return

        try:
            relations_data = self.serialize_relations(relations)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(relations_data, f, indent=2, ensure_ascii=False)

            QMessageBox.information(self, "Successo",
                                    f"Relazioni esportate con successo in {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Errore",
                                 f"Errore durante l'esportazione: {str(e)}")

    def import_relations(self):
        """Importa le relazioni da un file JSON"""
        # Pulisce il log
        self.debugText.clear()

        # Seleziona il file da importare
        filename, _ = QFileDialog.getOpenFileName(
            self, "Importa Relazioni", "", "JSON Files (*.json)")

        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                relations_data = json.load(f)

            self.log_message("=== INIZIO IMPORTAZIONE ===")
            self.log_message(f"File: {filename}")

            # Mostra i layer disponibili nel progetto
            self.log_message("\n--- Layer disponibili nel progetto ---")
            project = QgsProject.instance()
            for layer_id, layer in project.mapLayers().items():
                self.log_message(f"ID: {layer_id}, Nome: {layer.name()}")

            imported_count = self.deserialize_relations(relations_data)

            if imported_count > 0:
                self.refresh_relations()
                QMessageBox.information(self, "Successo",
                                        f"{imported_count} relazioni importate con successo.")
                self.log_message(f"\n=== IMPORTAZIONE COMPLETATA: {imported_count} relazioni ===")
            else:
                QMessageBox.warning(self, "Attenzione",
                                    "Nessuna relazione è stata importata. Controlla il log per i dettagli.")
                self.log_message("\n=== NESSUNA RELAZIONE IMPORTATA ===")

        except Exception as e:
            error_msg = f"Errore durante l'importazione: {str(e)}"
            QMessageBox.critical(self, "Errore", error_msg)
            self.log_message(f"\nERRORE: {error_msg}")

    def serialize_relations(self, relations):
        """Serializza le relazioni in un formato JSON"""
        relations_data = {
            "version": "1.0",
            "export_date": QgsProject.instance().fileName(),
            "relations": []
        }

        for rel_id, relation in relations.items():
            try:
                relation_data = {
                    "id": rel_id,
                    "name": relation.name(),
                    "strength": str(relation.strength()),
                    "parent_layer": {
                        "id": relation.referencingLayer().id() if relation.referencingLayer() else None,
                        "name": relation.referencingLayer().name() if relation.referencingLayer() else None,
                        "source": relation.referencingLayer().source() if relation.referencingLayer() else None
                    },
                    "child_layer": {
                        "id": relation.referencedLayer().id() if relation.referencedLayer() else None,
                        "name": relation.referencedLayer().name() if relation.referencedLayer() else None,
                        "source": relation.referencedLayer().source() if relation.referencedLayer() else None
                    },
                    "field_pairs": []
                }

                # Metodo corretto per ottenere le coppie di campi
                referencing_fields = relation.referencingFields()
                referenced_fields = relation.referencedFields()

                # Crea le coppie di campi con i nomi dei campi
                for i in range(len(referencing_fields)):
                    if i < len(referenced_fields):
                        field_pair = {
                            "referencing_field": referencing_fields[i],
                            "referenced_field": referenced_fields[i]
                        }
                        relation_data["field_pairs"].append(field_pair)

                relations_data["relations"].append(relation_data)

            except Exception as e:
                print(f"Errore nella serializzazione della relazione {rel_id}: {str(e)}")
                continue

        return relations_data

    def deserialize_relations(self, relations_data):
        """Deserializza le relazioni da un formato JSON"""
        if "relations" not in relations_data:
            raise ValueError("Formato file non valido: manca la sezione 'relations'")

        project = QgsProject.instance()
        relation_manager = project.relationManager()
        imported_count = 0

        self.log_message(f"\nTentativo di importare {len(relations_data['relations'])} relazioni...")

        for i, relation_data in enumerate(relations_data["relations"]):
            try:
                self.log_message(f"\n--- Relazione {i + 1}: {relation_data['name']} ---")

                # Trova i layer nel progetto corrente
                parent_layer = self.find_layer_by_name_or_source(
                    relation_data["parent_layer"]["name"],
                    relation_data["parent_layer"]["source"]
                )
                child_layer = self.find_layer_by_name_or_source(
                    relation_data["child_layer"]["name"],
                    relation_data["child_layer"]["source"]
                )

                if not parent_layer:
                    self.log_message(f"❌ Parent layer non trovato: {relation_data['parent_layer']['name']}")
                    continue

                if not child_layer:
                    self.log_message(f"❌ Child layer non trovato: {relation_data['child_layer']['name']}")
                    continue

                self.log_message(f"✅ Parent layer trovato: {parent_layer.name()} (ID: {parent_layer.id()})")
                self.log_message(f"✅ Child layer trovato: {child_layer.name()} (ID: {child_layer.id()})")

                # Controlla se la relazione esiste già
                existing_relation = relation_manager.relation(relation_data["id"])
                if existing_relation.isValid():
                    self.log_message(f"⚠️ Relazione già esistente, saltata")
                    continue

                # Crea la nuova relazione
                relation = QgsRelation()
                relation.setId(relation_data["id"])
                relation.setName(relation_data["name"])
                relation.setReferencingLayer(parent_layer.id())
                relation.setReferencedLayer(child_layer.id())

                # Aggiungi le coppie di campi
                field_pairs_added = 0
                for field_pair in relation_data["field_pairs"]:
                    ref_field = str(field_pair["referencing_field"])
                    refd_field = str(field_pair["referenced_field"])

                    # Verifica che i campi esistano nei layer
                    parent_fields = [field.name() for field in parent_layer.fields()]
                    child_fields = [field.name() for field in child_layer.fields()]

                    # Se il campo è un numero, prova a convertirlo in nome campo
                    if ref_field.isdigit():
                        field_index = int(ref_field)
                        if field_index < len(parent_fields):
                            ref_field = parent_fields[field_index]
                        else:
                            self.log_message(f"⚠️ Indice campo parent non valido: {field_index}")
                            continue

                    if refd_field.isdigit():
                        field_index = int(refd_field)
                        if field_index < len(child_fields):
                            refd_field = child_fields[field_index]
                        else:
                            self.log_message(f"⚠️ Indice campo child non valido: {field_index}")
                            continue

                    # Verifica che i campi esistano
                    if ref_field not in parent_fields:
                        self.log_message(f"⚠️ Campo '{ref_field}' non trovato nel parent layer")
                        continue

                    if refd_field not in child_fields:
                        self.log_message(f"⚠️ Campo '{refd_field}' non trovato nel child layer")
                        continue

                    relation.addFieldPair(ref_field, refd_field)
                    field_pairs_added += 1
                    self.log_message(f"✅ Campo aggiunto: {ref_field} -> {refd_field}")

                if field_pairs_added == 0:
                    self.log_message(f"❌ Nessuna coppia di campi valida trovata")
                    continue

                # Controlla se la relazione è valida
                if relation.isValid():
                    relation_manager.addRelation(relation)
                    imported_count += 1
                    self.log_message(f"✅ Relazione importata con successo!")
                else:
                    self.log_message(f"❌ Relazione non valida dopo la creazione")

            except Exception as e:
                error_msg = f"Errore nell'importazione della relazione '{relation_data.get('name', 'sconosciuta')}': {str(e)}"
                self.log_message(f"❌ {error_msg}")

        return imported_count

    def find_layer_by_name_or_source(self, name, source):
        """Trova un layer per nome o sorgente con ricerca fuzzy"""
        project = QgsProject.instance()

        # Prima prova per nome esatto
        if name:
            layers = project.mapLayersByName(name)
            if layers:
                return layers[0]

            # Prova con nome simile (rimuovi caratteri speciali)
            name_clean = name.replace("-", "_").replace(" ", "_")
            for layer in project.mapLayers().values():
                layer_name_clean = layer.name().replace("-", "_").replace(" ", "_")
                if layer_name_clean.lower() == name_clean.lower():
                    return layer

            # Prova ricerca parziale
            for layer in project.mapLayers().values():
                if name.lower() in layer.name().lower() or layer.name().lower() in name.lower():
                    return layer

        # Poi prova per sorgente (solo se accessibile)
        if source:
            for layer in project.mapLayers().values():
                if hasattr(layer, 'source'):
                    try:
                        # Confronta solo la parte del nome della tabella
                        if 'table=' in source and 'table=' in layer.source():
                            source_table = source.split('table=')[1].split()[0].strip('"')
                            layer_table = layer.source().split('table=')[1].split()[0].strip('"')
                            if source_table == layer_table:
                                return layer
                    except:
                        continue

        return None
