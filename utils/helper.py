from flask_sqlalchemy import SQLAlchemy
import os 


class DbHelper:
    
    def add_record(self, query):
        db.session.add(query)
        db.session.commit()
        db.close()
        
    def update_record():
        db.session.commit()
        db.close()
        
    def delete_record():
        db.session.delete()
        db.session.commit()
        db.close()

class OsHelper:

    def create_file(filename):
        fd = os.open(filename, "w")
        return fd
    
