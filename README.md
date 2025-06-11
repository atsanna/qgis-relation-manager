# QGIS Relation Manager Plugin

Un plugin per QGIS che permette di esportare e importare le relazioni tra layer da un progetto all'altro, facilitando la gestione e il riutilizzo delle configurazioni delle relazioni.

## Caratteristiche

- **Visualizzazione relazioni**: Mostra tutte le relazioni presenti nel progetto corrente in una tabella organizzata
- **Esportazione**: Salva le relazioni in formato JSON con tutti i dettagli (layer, campi, configurazioni)
- **Importazione**: Carica relazioni da file JSON in altri progetti QGIS
- **Log dettagliato**: Sistema di logging che mostra il processo di importazione passo per passo
- **Ricerca intelligente**: Trova automaticamente i layer corrispondenti anche con nomi leggermente diversi
- **Gestione errori**: Feedback chiaro sui problemi riscontrati durante l'importazione

## Installazione

1. Scarica il plugin e decomprimilo nella cartella dei plugin di QGIS:
   - **Windows**: `C:\Users\[username]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

2. Riavvia QGIS

3. Attiva il plugin da: **Plugin → Gestisci e installa plugin → Installati**

## Utilizzo

### Apertura del Plugin

Il plugin può essere avviato tramite:
- Menu: **Plugin → Relation Manager → Gestisci Relazioni**
- Barra degli strumenti: Icona del plugin (se aggiunta)

### Esportazione delle Relazioni

1. Apri un progetto QGIS con relazioni configurate
2. Avvia il plugin
3. Clicca su **"Esporta Relazioni"**
4. Scegli nome e posizione del file JSON
5. Le relazioni verranno salvate con tutti i dettagli

### Importazione delle Relazioni

1. Apri il progetto di destinazione (deve contenere i layer coinvolti nelle relazioni)
2. Avvia il plugin
3. Clicca su **"Importa Relazioni"**
4. Seleziona il file JSON precedentemente esportato
5. Controlla il log per verificare l'esito dell'importazione
6. Clicca **"Aggiorna"** per vedere le nuove relazioni

## Formato File JSON

Il plugin salva le relazioni in un formato JSON strutturato che include:
```json
json
{
  "version": "1.0",
  "export_date": "percorso/del/progetto.qgz",
  "relations": [
    {
      "id": "id_relazione",
      "name": "Nome della relazione",
      "strength": "0",
      "parent_layer": {
        "id": "id_layer_padre",
        "name": "nome_layer_padre",
        "source": "sorgente_dati"
      },
      "child_layer": {
        "id": "id_layer_figlio",
        "name": "nome_layer_figlio",
        "source": "sorgente_dati"
      },
      "field_pairs": [
        {
          "referencing_field": "campo_padre",
          "referenced_field": "campo_figlio"
        }
      ]
    }
  ]
}
```
## Risoluzione Problemi

### Le relazioni non vengono importate

**Possibili cause e soluzioni:**

1. **Layer non trovati**:
   - Verifica che i layer esistano nel progetto di destinazione
   - Controlla i nomi dei layer nel log
   - I nomi possono essere leggermente diversi (es. "layer-name" vs "layer_name")

2. **Campi non trovati**:
   - Assicurati che i campi delle relazioni esistano nei layer
   - Verifica i nomi dei campi nel log di importazione
   - I campi devono avere lo stesso nome o indice

3. **Relazioni già esistenti**:
   - Le relazioni con lo stesso ID vengono saltate
   - Rimuovi le relazioni esistenti se vuoi sostituirle

### Il plugin non si avvia

1. Verifica che il plugin sia attivato in **Plugin → Gestisci e installa plugin**
2. Controlla la console Python di QGIS per errori
3. Riavvia QGIS

### Errori durante l'esportazione

1. Assicurati che il progetto contenga relazioni valide
2. Verifica i permessi di scrittura nella cartella di destinazione
3. Controlla che non ci siano caratteri speciali nel percorso del file

## Consigli per l'Uso

### Best Practices

1. **Backup**: Fai sempre un backup del progetto prima di importare relazioni
2. **Nomi consistenti**: Usa nomi di layer e campi consistenti tra progetti
3. **Test**: Verifica sempre che le relazioni importate funzionino correttamente
4. **Log**: Controlla sempre il log di importazione per identificare eventuali problemi

### Workflow Consigliato

1. **Progetto template**: Crea un progetto template con tutte le relazioni
2. **Esporta una volta**: Esporta le relazioni dal template
3. **Riutilizza**: Importa le relazioni in tutti i nuovi progetti
4. **Aggiorna**: Aggiorna il template quando necessario

## Compatibilità

- **QGIS**: Versione 3.x
- **Python**: 3.6+
- **Sistema Operativo**: Windows, Linux, macOS
- **Formato dati**: Tutti i formati supportati da QGIS (PostGIS, Shapefile, GeoPackage, ecc.)

## Limitazioni

- Le relazioni vengono importate solo se i layer di origine e destinazione sono presenti nel progetto
- I nomi dei campi devono corrispondere tra i progetti
- Le relazioni con lo stesso ID vengono saltate durante l'importazione

## Licenza

Questo plugin è distribuito sotto licenza GPL v3.

## Supporto

Per segnalare bug, richiedere funzionalità o ottenere supporto:

1. Controlla il log di debug nel plugin
2. Verifica i messaggi di errore nella console Python di QGIS
3. Assicurati di avere la versione più recente del plugin

## Changelog

### Versione 1.0.0
- Prima release stabile
- Esportazione e importazione delle relazioni
- Sistema di logging dettagliato
- Ricerca intelligente dei layer
- Gestione automatica degli indici dei campi

---

**Nota**: Questo plugin è stato sviluppato per facilitare la gestione delle relazioni in QGIS. Testalo sempre su progetti di backup prima di usarlo su dati di produzione.