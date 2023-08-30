import mariadb
import sys
from sshtunnel import SSHTunnelForwarder
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from datetime import date

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

ssh_ip_address = "95.179.193.37"
ssh_p_username = 'root'
ssh_p_password = 'e@3Sy=nPUhosPUh@'
ssh_port = 22
ssh_remote_bind_address = 3306
db_server_ip = '95.179.193.37'
db_server_port = 3306
db_user = 'externaluser'
db_user_password = 'Herts123'
db_name = 'PTSdb'
tunneled_host = '127.0.0.1'

with SSHTunnelForwarder(
    (ssh_ip_address, ssh_port),
    ssh_password=ssh_p_password,
    ssh_username=ssh_p_username,
    remote_bind_address=(db_server_ip, db_server_port)) as server:
    
    print("Trying to make a connection")
    print(server.local_bind_port)
    try:
        conn = mariadb.connect(
            host=tunneled_host,
            port=server.local_bind_port,
            user=db_user,
            passwd=db_user_password,
            db=db_name)
        print("made connection")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    cur = conn.cursor()
    

    class UI(QMainWindow):     
        def __init__(self):
            super(UI, self).__init__()

            # Load UI file - put name of file here and filepath if necessary
            uic.loadUi("patient_details.ui", self)
            

            # Define widgets
            #example code for a label
            #self.label = self.findChild(QLabel, "label_4")
            self.patient_detail_table_widget = self.findChild(QTableWidget, "tableWidget_2")
            self.delete_patient_button = self.findChild(QPushButton, "pushButton_4")
            self.create_button = self.findChild(QPushButton, "pushButton_2")
            self.update_button = self.findChild(QPushButton, "pushButton_3")
            self.error_label = self.findChild(QLabel, "label_9")
            self.search_button = self.findChild(QPushButton, "pushButton")
            self.refresh_button = self.findChild(QPushButton, "pushButton_5")
            self.edit_date_button = self.findChild(QPushButton, "pushButton_6")
            self.clear_date_button = self.findChild(QPushButton, "pushButton_7")
            self.test_label = self.findChild(QLabel, "label_10")

            self.patient_id_search = self.findChild(QTextEdit, "textEdit")
            self.first_name_search = self.findChild(QTextEdit, "textEdit_2")
            self.city_search = self.findChild(QTextEdit, "textEdit_3")
            self.last_name_search = self.findChild(QTextEdit, "textEdit_4")
            self.gender_search = self.findChild(QComboBox, "comboBox")
            self.registration_date_search = self.findChild(QDateEdit, "dateEdit")
            self.text_registration_date_search = self.findChild(QTextEdit, "textEdit_5")


            # Widget actions
            #example submit button - submit_patient is the function to be used
            self.patient_detail_table_widget.cellClicked.connect(self.get_clicked_cell)
            self.delete_patient_button.clicked.connect(self.delete_confirmation)
            self.create_button.clicked.connect(self.show_create_window)
            self.update_button.clicked.connect(self.show_update_window)
            self.refresh_button.clicked.connect(self.load_patient_details)
            self.search_button.clicked.connect(self.search_patient)
            self.edit_date_button.clicked.connect(self.show_calendar_window)
            self.clear_date_button.clicked.connect(self.clear_date)

            self.show()

        #this can also have column in as a parameter
        def get_clicked_cell(self, row):
            patient_id = self.patient_detail_table_widget.item(row,0).text()
            return patient_id

        @qtc.pyqtSlot(str)
        def delete_selected_row(self):
            current_row = self.patient_detail_table_widget.currentRow()
            patient_id = self.patient_detail_table_widget.item(current_row,0).text()
            query = f"DELETE FROM Patients WHERE PatientID = {patient_id}"
            cur.execute(query)
            conn.commit()
            self.run()
        
        def load_patient_details(self):
            try:
                query = "SELECT * FROM Patients"
                cur.execute(query)
                allSQLRows = cur.fetchall()
                self.patient_detail_table_widget.setRowCount(len(allSQLRows))
                cur.execute(query)
                table_row = 0
                for row in cur:
                    self.patient_detail_table_widget.setItem(table_row, 0, QtWidgets.QTableWidgetItem(str(row[0])))
                    self.patient_detail_table_widget.setItem(table_row, 1, QtWidgets.QTableWidgetItem(row[1]))
                    self.patient_detail_table_widget.setItem(table_row, 2, QtWidgets.QTableWidgetItem(row[2]))
                    self.patient_detail_table_widget.setItem(table_row, 3, QtWidgets.QTableWidgetItem(row[3]))
                    self.patient_detail_table_widget.setItem(table_row, 4, QtWidgets.QTableWidgetItem(row[4]))
                    self.patient_detail_table_widget.setItem(table_row, 5, QtWidgets.QTableWidgetItem(row[5]))
                    self.patient_detail_table_widget.setItem(table_row, 6, QtWidgets.QTableWidgetItem(str(row[6])))
                    table_row+=1
            except:
                print("Error retrieving entry from database")

        def search_patient(self):
            data = []
            query = "SELECT * FROM Patients WHERE 1=1"
            if self.patient_id_search.toPlainText():
                query +=  " AND PatientID = %s"
                data.append(self.patient_id_search.toPlainText())
            if self.first_name_search.toPlainText():
                query += " AND Firstname = %s"
                data.append(self.first_name_search.toPlainText())
            if self.last_name_search.toPlainText():
                query += " AND Lastname = %s"
                data.append(self.last_name_search.toPlainText())
            if self.city_search.toPlainText():
                query += " AND City = %s"
                data.append(self.city_search.toPlainText())
            if self.gender_search.currentText() != "All":
                query += " AND Gender = %s"
                data.append(self.gender_search.currentText())
            if self.text_registration_date_search.toPlainText():
                query += " AND Registration_date = %s"
                data.append(self.text_registration_date_search.toPlainText())
            cur.execute(query, data)
            conn.commit()
            allSQLRows = cur.fetchall()
            self.patient_detail_table_widget.setRowCount(len(allSQLRows))
            cur.execute(query, data)
            table_row = 0
            for row in cur:
                self.patient_detail_table_widget.setItem(table_row, 0, QtWidgets.QTableWidgetItem(str(row[0])))
                self.patient_detail_table_widget.setItem(table_row, 1, QtWidgets.QTableWidgetItem(row[1]))
                self.patient_detail_table_widget.setItem(table_row, 2, QtWidgets.QTableWidgetItem(row[2]))
                self.patient_detail_table_widget.setItem(table_row, 3, QtWidgets.QTableWidgetItem(row[3]))
                self.patient_detail_table_widget.setItem(table_row, 4, QtWidgets.QTableWidgetItem(row[4]))
                self.patient_detail_table_widget.setItem(table_row, 5, QtWidgets.QTableWidgetItem(row[5]))
                self.patient_detail_table_widget.setItem(table_row, 6, QtWidgets.QTableWidgetItem(str(row[6])))
                table_row+=1

        # this function creates the create patient window
        def show_create_window(self):
            self.w = CreateWindow()
            self.w.submitted.connect(self.update_with_new_data)
            self.w.show()

        def show_calendar_window(self):
            self.w = CalendarWindow()
            self.w.submitted.connect(self.populate_registration_date_search)
            self.w.show()

        @qtc.pyqtSlot(str)
        def populate_registration_date_search(self, tester):
            self.tester = tester
            self.text_registration_date_search.setText(self.tester)

        def clear_date(self):
            self.text_registration_date_search.setText("")

        @qtc.pyqtSlot(str)
        def update_with_new_data(self):
            self.load_patient_details()

        def show_update_window(self):
            try:
                current_row = self.patient_detail_table_widget.currentRow()
                patient_id = self.patient_detail_table_widget.item(current_row,0).text()
                self.w = UpdateWindow()
                self.w.populate_patient(patient_id)
                self.w.submitted.connect(self.update_with_new_data)
                self.w.show()
            except Exception as e:
                print("Error retrieving entry from database ",e)
                self.display_patient_error()

        def display_patient_error(self):
            self.w = PatientErrorWindow()
            self.w.show()

        def delete_confirmation(self):
            try:
                current_row = self.patient_detail_table_widget.currentRow()
                patient_id = self.patient_detail_table_widget.item(current_row,0).text()
                first_name = self.patient_detail_table_widget.item(current_row,1).text()
                self.w = DeleteConfirmationWindow()
                self.w.set_patient_info(patient_id,first_name)
                self.w.submitted.connect(self.delete_selected_row)
                self.w.show()
            except Exception as e:
                self.display_patient_error()
            
        def run(self):
            self.load_patient_details()

    class CreateWindow(QMainWindow):

        submitted = qtc.pyqtSignal(str)

        def __init__(self):
            super(CreateWindow, self).__init__()

            uic.loadUi("create_patient.ui", self)

            self.show()

            self.first_name_input = self.findChild(QTextEdit, "textEdit")
            self.last_name_input = self.findChild(QTextEdit, "textEdit_2")
            self.address_input = self.findChild(QTextEdit, "textEdit_3")
            self.city_input = self.findChild(QTextEdit, "textEdit_4")
            self.gender_input = self.findChild(QComboBox, "comboBox_2")
            self.patient_label = self.findChild(QLabel, "label_3")
            self.create_button = self.findChild(QPushButton, "pushButton_6")
            self.clear_button = self.findChild(QPushButton, "pushButton_5")

            self.create_button.clicked.connect(self.create_patient)
            self.clear_button.clicked.connect(self.clear_entries)
            
        def create_patient(self):
            if self.first_name_input.toPlainText() == '' or self.last_name_input.toPlainText() == '' or self.address_input.toPlainText() == '' or self.city_input.toPlainText() == '':
                self.show_create_error_window()
            else:
                query = "INSERT INTO Patients (Firstname,Lastname,Address,City,Gender,Registration_date) VALUES (%s,%s,%s,%s,%s,%s)"
                data = (
                    self.first_name_input.toPlainText(),
                    self.last_name_input.toPlainText(),
                    self.address_input.toPlainText(),
                    self.city_input.toPlainText(),
                    str(self.gender_input.currentText()),
                    str(date.today()))
                cur.execute(query, data)
                conn.commit()
                query = "SELECT MAX(PatientID) FROM Patients"
                cur.execute(query)
                patient_id = cur.fetchone()[0]
                self.patient_label.setText(f'Patient created with ID: {str(patient_id)}')
                self.submitted.emit("create")
                self.close()
        
        def clear_entries(self):
            self.first_name_input.setPlainText('')
            self.last_name_input.setPlainText('')
            self.address_input.setPlainText('')
            self.city_input.setPlainText('')

        def show_create_error_window(self):
            self.w = CreateErrorWindow()
            self.w.show()

    class UpdateWindow(QMainWindow):

        submitted = qtc.pyqtSignal(str)

        def __init__(self):
            super(UpdateWindow, self,).__init__()
            
            uic.loadUi("update_patient.ui", self)

            self.first_name_input = self.findChild(QTextEdit, "textEdit")
            self.last_name_input = self.findChild(QTextEdit, "textEdit_2")
            self.address_input = self.findChild(QTextEdit, "textEdit_3")
            self.city_input = self.findChild(QTextEdit, "textEdit_4")
            self.gender_input = self.findChild(QComboBox, "comboBox_2")
            self.patient_label = self.findChild(QLabel, "label_3")
            self.patient_id_label = self.findChild(QLabel, "label_4")
            self.update_button = self.findChild(QPushButton, "pushButton_6")
            self.tester_button = self.findChild(QPushButton, "pushButton_7")
            #self.text_box = self.findChild(QPlainTextEdit, "plainTextEdit")

            self.show()

            self.update_button.clicked.connect(self.update_patient_data)
            
        def populate_patient(self, patient_id):
            query = f"SELECT * FROM Patients WHERE PatientID = {patient_id}"
            cur.execute(query)
            row = cur.fetchone()
            if row is not None:
                self.patient_id_label.setText(patient_id)
                self.first_name_input.setPlainText(row[1])
                self.last_name_input.setPlainText(row[2])
                self.address_input.setPlainText(row[3])
                self.city_input.setPlainText(row[4])
                self.gender_input.setCurrentText(row[5])

        def update_patient_data(self):
            patient_id = self.patient_id_label.text()
            query = "UPDATE Patients SET Firstname = %s, Lastname = %s, Address = %s, City = %s, Gender = %s WHERE PatientID = %s"
            data = (
                self.first_name_input.toPlainText(),
                self.last_name_input.toPlainText(),
                self.address_input.toPlainText(),
                self.city_input.toPlainText(),
                self.gender_input.currentText(),
                patient_id)
            cur.execute(query, data)
            conn.commit()
            self.submitted.emit("delete")
            self.close()
    
    class PatientErrorWindow(QWidget):
        def __init__(self):
            super(PatientErrorWindow, self).__init__()

            uic.loadUi("error_patient.ui", self)

            self.show()

            self.ok_button = self.findChild(QPushButton, "pushButton_2")

            self.ok_button.clicked.connect(self.exit_window)

        def exit_window(self):
            self.close()

    class DeleteConfirmationWindow(QWidget):

        submitted = qtc.pyqtSignal(str)

        def __init__(self):
            super(DeleteConfirmationWindow, self).__init__()

            uic.loadUi("delete_confirmation.ui", self)

            self.show()

            self.yes_button = self.findChild(QPushButton, "pushButton_2")
            self.no_button = self.findChild(QPushButton, "pushButton_3")
            self.patient_id_label = self.findChild(QLabel, "label_3")
            self.first_name_label = self.findChild(QLabel, "label_4")

            self.yes_button.clicked.connect(self.confirm)
            self.no_button.clicked.connect(self.close)

        def set_patient_info(self, patient_id, first_name):
            self.patient_id_label.setText("Patient ID: "+patient_id)
            self.first_name_label.setText("First name: "+first_name)

        def confirm(self):
            self.submitted.emit("delete")
            self.close()

    class CreateErrorWindow(QWidget):
        def __init__(self):
            super(CreateErrorWindow, self).__init__()

            uic.loadUi("error_create.ui", self)

            self.show()

            self.ok_button = self.findChild(QPushButton, "pushButton_2")

            self.ok_button.clicked.connect(self.exit_window)

        def exit_window(self):
            self.close()
    
    class CalendarWindow(QWidget):
        
        submitted = qtc.pyqtSignal(str)

        def __init__(self):
            super(CalendarWindow, self).__init__()

            uic.loadUi("calendar.ui", self)

            self.show()

            self.ok_button = self.findChild(QPushButton, "pushButton")
            self.calendar = self.findChild(QCalendarWidget, "calendarWidget")

            self.ok_button.clicked.connect(self.on_submit)

        def on_submit(self):
            self.submitted.emit(self.calendar.selectedDate().toString('yyyy/MM/dd'))
            self.close()

        def exit_window(self):
            self.close()

    # Initialize the app
    if __name__ == '__main__':
        app = qtw.QApplication(sys.argv)
        mw = UI()
        mw.run()
        sys.exit(app.exec())
