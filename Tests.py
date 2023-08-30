import unittest
from sshtunnel import SSHTunnelForwarder
import mariadb
from datetime import date

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
    db_cur = conn.cursor()

    def insert(data):
        query = "INSERT INTO Patients (Firstname, Lastname, Address, City, Gender, Registration_date) VALUES (%s,%s,%s,%s,%s,%s)"
        db_cur.execute(query,data)
        conn.commit()

    def retrieve(data):
        query = "SELECT Firstname, Lastname, Address, City, Gender, Registration_date FROM Patients WHERE Firstname = (%s) AND Lastname = (%s) AND Address = (%s) AND City = (%s) AND Gender = (%s) AND Registration_date = (%s)"
        db_cur.execute(query,data)
        row = db_cur.fetchone()
        return(row[0],row[1],row[2],row[3],row[4],str(row[5]))





    def delete(patient_id):
        query = f"DELETE FROM Patients WHERE PatientID ={patient_id}"
        db_cur.execute(query)
        conn.commit()

    def check_if_deleted(patient_id):
        query = f"SELECT * FROM Patients WHERE PatientID ={patient_id}"
        db_cur.execute(query)
        row = db_cur.fetchone()
        if row is None:
            return ("ID Not found")
        else:
            return ("ID Found")       

    class TestClass(unittest.TestCase):
        
        # test if a created patient is equal to a retrieved patient
        def test_create(self):
            data = ("Robert","Brown","123 Street","London","Male",str(date.today()))
            insert(data)
            retrieved = retrieve(data)
            expected = data
            self.assertEqual(retrieved, expected)

        # test delete a patient that doesn't exist
        def test_delete(self):
            data = 74
            delete(data)
            retrieved = check_if_deleted(data)
            expected = "ID Not found"
            self.assertEqual(retrieved, expected)

        # test update a patient with ID 11
        def test_update(self):
            try:
                query = ("UPDATE Patients SET Firstname = %s WHERE PatientID = %s")
                data = ("Barry", 11)
                db_cur.execute(query,data)
                conn.commit()
                db_cur.execute("SELECT Firstname FROM Patients WHERE PatientID = %s",(11,))
                updated_name = db_cur.fetchone()
                self.assertEqual(updated_name[0],"Barry")
            except Exception as e:
                print("Error found",e)

        # test insert a patient with an invalid patient ID
        def test_data_validation(self):
            try:
                query = ("INSERT INTO Patients (PatientID, Firstname) VALUES (%s,%s)")
                data = ("David","Franks")
                db_cur.execute(query,data)
                conn.commit()
            except mariadb.Error as e:
                print("Error found",e)
            else:
                self.fail("Expected exception was not raised")



    if __name__ == "__main__":
        unittest.main(exit=False)








