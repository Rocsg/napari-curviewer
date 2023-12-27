from qtpy.QtWidgets import QFileDialog, QMessageBox


# Fonction pour ouvrir le sélecteur de fichiers et retourner le chemin sélectionné
def select_file():
    # Crée un dialogue pour ouvrir un fichier, le paramètre 'None' peut être remplacé par une fenêtre parent si nécessaire
    dialog = QFileDialog(None, "Select an image file")

    # Définit le mode pour sélectionner un seul fichier
    dialog.setFileMode(QFileDialog.ExistingFile)

    # Filtre pour n'afficher que certains types de fichiers (par exemple, images)
    dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)")

    # Ouvre le dialogue et attend que l'utilisateur sélectionne un fichier
    if dialog.exec_():
        # Récupère le chemin du fichier sélectionné
        file_path = dialog.selectedFiles()[0]
        return file_path
    return None


def popup(message):
    msg = QMessageBox()

    msg.setWindowTitle("Message from napari-curviewer")
    msg.setText(message)

    # Set the icon and buttons (optional)
    msg.setIcon(QMessageBox.Information)
    msg.setStandardButtons(QMessageBox.Ok)

    # Show the message box
    msg.exec_()
