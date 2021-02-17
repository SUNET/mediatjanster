""" helper for downloading multistream videos from Kaltura """
import sys
import traceback
import json
import hashlib
import urllib.request
from KalturaClient import KalturaConfiguration, KalturaClient
from KalturaClient.Plugins.Core import (
    KalturaSessionType,
    KalturaMediaEntryFilter,
    KalturaFilterPager,
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QStatusBar,
    QAction,
    qApp,
    QWidget,
    QFormLayout,
    QFileDialog,
    QInputDialog,
    QProgressBar,
    QErrorMessage,
)
from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal, QThreadPool


class Worker(QRunnable):
    """ Worker thread """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class MultiDl(QMainWindow):
    session_type = ""

    def __init__(self):
        super(MultiDl, self).__init__()
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(5)
        self.initUI()

    def app_token_session(self):
        """ create kaltura session using appToken """
        self.statusbar.showMessage("Create kaltura session using appToken")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "Json Files (*.json)",
            options=options,
        )

        try:
            with open(filename) as json_data_file:
                data = json.load(json_data_file)
                api_token_id = data["api_token_id"]
                api_token = data["api_token"]
                kaltura_partnerid = data["kaltura_partnerid"]
                kaltura_serviceurl = data["kaltura_serviceurl"]

            config = KalturaConfiguration(kaltura_partnerid)
            config.serviceUrl = kaltura_serviceurl
            self.kaltura_session = KalturaClient(config)
            user_id = ""
            widget_id = "_" + str(kaltura_partnerid)

            expiry = 86400
            result = self.kaltura_session.session.startWidgetSession(widget_id, expiry)
            self.kaltura_session.setKs(result.ks)
            tokenHash = hashlib.sha256(
                result.ks.encode("ascii") + api_token.encode("ascii")
            ).hexdigest()
            type = KalturaSessionType.ADMIN

            result = self.kaltura_session.appToken.startSession(
                api_token_id, tokenHash, user_id, type, expiry
            )
            self.kaltura_session.setKs(result.ks)
            MultiDl.session_type = "appToken"
        except:
            self.error_dialog.showMessage("Error creating Kaltura session")

    def admin_secret_session(self):
        """ create kaltura session using adminsecret """
        self.statusbar.showMessage("Create kaltura session using adminsecret")
        kaltura_partnerid, ok = QInputDialog.getText(
            self, "Input kaltura partnerid", "Input partnerid:"
        )
        kaltura_adminsecret, ok = QInputDialog.getText(
            self, "Input adminsecret", "Input adminsecret:"
        )

        try:
            config = KalturaConfiguration()
            config.serviceUrl = "https://api.kaltura.nordu.net/"
            self.kaltura_session = KalturaClient(config)
            ks = self.kaltura_session.session.start(
                kaltura_adminsecret, None, KalturaSessionType.ADMIN, kaltura_partnerid
            )
            self.kaltura_session.setKs(ks)
            MultiDl.session_type = "adminSecret"
        except:
            self.error_dialog.showMessage("Error creating Kaltura session")

    def download_entry_id(self):
        """ Download videofiles from entryId """
        files_to_download = {}
        parent_entry_id, ok = QInputDialog.getText(
            self, "Input entryid", "Input entryid:"
        )
        self.statusbar.showMessage(
            "Download files for parent entryId " + parent_entry_id
        )
        self.top_label.setText(
            "Downloading files for parent entryId " + parent_entry_id
        )

        files_to_download.update(
            {
                parent_entry_id: self.kaltura_session.media.get(
                    parent_entry_id
                ).downloadUrl
            }
        )

        filter = KalturaMediaEntryFilter()
        filter.parentEntryIdEqual = parent_entry_id
        pager = KalturaFilterPager()
        child_entries = self.kaltura_session.media.list(filter, pager)

        for child in child_entries.objects:
            files_to_download.update({child.id: child.downloadUrl})

        self.thread_download(parent_entry_id, files_to_download)

    def initUI(self):
        """ user interface """
        self.setGeometry(200, 200, 400, 400)
        self.setWindowTitle("multidl")
        self.display = QLabel(self)
        self.display.move(50, 50)
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # file menu
        self.statusbar.showMessage("Choose an option from the filemenu")
        exit_act = QAction("Exit", self)
        exit_act.setStatusTip("Exit application")
        exit_act.triggered.connect(qApp.quit)
        app_token_act = QAction("Load apptoken config", self)
        app_token_act.setStatusTip("Load apptoken config")
        app_token_act.triggered.connect(self.app_token_session)
        admin_secret_act = QAction("Start adminsecret session", self)
        admin_secret_act.setStatusTip("Start adminsecret session")
        admin_secret_act.triggered.connect(self.admin_secret_session)
        entry_id_act = QAction("Download multistream", self)
        entry_id_act.setStatusTip("Download multistream")
        entry_id_act.triggered.connect(self.download_entry_id)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(app_token_act)
        file_menu.addAction(admin_secret_act)
        file_menu.addAction(entry_id_act)
        file_menu.addAction(exit_act)

        # Layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.top_label = QLabel("Choose an option from the filemenu")
        self.error_dialog = QErrorMessage()
        self.download_label_1 = QLabel()
        self.download_label_2 = QLabel()
        self.download_label_3 = QLabel()
        self.download_label_4 = QLabel()
        self.progress_bar_1 = QProgressBar()
        self.progress_bar_1.hide()
        self.progress_bar_2 = QProgressBar()
        self.progress_bar_2.hide()
        self.progress_bar_3 = QProgressBar()
        self.progress_bar_3.hide()
        self.progress_bar_4 = QProgressBar()
        self.progress_bar_4.hide()
        self.layout = QFormLayout(self.main_widget)
        self.layout.addRow(self.top_label)
        self.layout.addRow(self.download_label_1, self.progress_bar_1)
        self.layout.addRow(self.download_label_2, self.progress_bar_2)
        self.layout.addRow(self.download_label_3, self.progress_bar_3)
        self.layout.addRow(self.download_label_4, self.progress_bar_4)
        self.show()

    def thread_download(self, parent_entryid, files_to_download):
        """ start worker threads for downloading files """
        count = 1
        for entryid, download_url in files_to_download.items():
            save_loc = parent_entryid + "-" + entryid + ".mp4"
            if count == 1:
                worker = Worker(
                    urllib.request.urlretrieve, download_url, save_loc, self.callback_1
                )
                self.progress_bar_1.show()
                self.download_label_1.setText("Downloading " + entryid)
                worker.signals.finished.connect(self.thread_1_complete)
            if count == 2:
                worker = Worker(
                    urllib.request.urlretrieve, download_url, save_loc, self.callback_2
                )
                self.progress_bar_2.show()
                self.download_label_2.setText("Downloading " + entryid)
                worker.signals.finished.connect(self.thread_2_complete)
            if count == 3:
                worker = Worker(
                    urllib.request.urlretrieve, download_url, save_loc, self.callback_3
                )
                self.progress_bar_3.show()
                self.download_label_3.setText("Downloading " + entryid)
                worker.signals.finished.connect(self.thread_3_complete)
            if count == 4:
                worker = Worker(
                    urllib.request.urlretrieve, download_url, save_loc, self.callback_4
                )
                self.progress_bar_4.show()
                self.download_label_4.setText("Downloading " + entryid)
                worker.signals.finished.connect(self.thread_4_complete)

            self.threadpool.start(worker)
            count += 1

    def callback_1(self, progress, blocksize, totalsize):
        """ callback for progress bar download 1 """
        data_read = progress * blocksize
        if totalsize > 0:
            download_percentage = data_read * 100 / totalsize
            self.progress_bar_1.setValue(int(download_percentage))

    def callback_2(self, progress, blocksize, totalsize):
        """ callback for progress bar download 2 """
        data_read = progress * blocksize
        if totalsize > 0:
            download_percentage = data_read * 100 / totalsize
            self.progress_bar_2.setValue(int(download_percentage))

    def callback_3(self, progress, blocksize, totalsize):
        """ callback for progress bar download 3 """
        data_read = progress * blocksize
        if totalsize > 0:
            download_percentage = data_read * 100 / totalsize
            self.progress_bar_3.setValue(int(download_percentage))

    def callback_4(self, progress, blocksize, totalsize):
        """ callback for progress bar download 4 """
        data_read = progress * blocksize
        if totalsize > 0:
            download_percentage = data_read * 100 / totalsize
            self.progress_bar_4.setValue(int(download_percentage))

    def thread_1_complete(self):
        """ self explanatory! """
        self.download_label_1.setText("Download complete!")
        self.progress_bar_1.hide()

    def thread_2_complete(self):
        """ self explanatory! """
        self.download_label_2.setText("Download complete!")
        self.progress_bar_2.hide()

    def thread_3_complete(self):
        """ self explanatory! """
        self.download_label_3.setText("Download complete!")
        self.progress_bar_3.hide()

    def thread_4_complete(self):
        """ self explanatory! """
        self.download_label_4.setText("Download complete!")
        self.progress_bar_4.hide()


def window():
    """ main function """
    app = QApplication(sys.argv)
    win = MultiDl()
    win.show()
    sys.exit(app.exec_())


window()
